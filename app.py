import os
import time
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from sqlalchemy import inspect, text
from flask import Flask, render_template, request, jsonify, send_from_directory, session

# Load environment variables
load_dotenv()

# Import Database & Models
from models import (
    init_db, db_session, engine, User, HouseProject, HouseStyleProfile, Room, RoomImage,
    RoomAnalysis, UserPreferences, Design, FurnitureRecommendation,
    CostEstimate, DesignChat, AsyncJob
)

# Import AI Engine Services
from services.ai.orchestrator import orchestrator
from services.vision.image_analyzer import image_analyzer
from services.vision.floorplan_analyzer import floorplan_analyzer
from services.design.design_engine import design_engine
from services.design.room_rules import get_room_rule, ROOM_RULES, normalize_room_type
from services.recommendation.furniture_engine import furniture_engine
from services.recommendation.material_lighting import material_lighting_engine
from services.cost.estimator import cost_estimator

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv("SECRET_KEY", "decoraai-super-secret-key-2026")
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# ==============================================================================
# 1. CORE & QUICK PROMPT ROUTES
# ==============================================================================

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required. Please login as admin."}), 401
            return render_template("auth.html", error="Admin login required to access Database Explorer.")

        user = db_session.query(User).filter_by(id=user_id).first()
        if not user or not user.is_admin:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Access denied. Administrator privileges required."}), 403
            return render_template("auth.html", error="Access denied. Administrator privileges required.")

        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("auth.html")

@app.route("/admin/db")
@admin_required
def admin_db_page():
    return render_template("db_admin.html")

@app.route("/admin/db/download")
@admin_required
def download_db():
    db_path = "interior_design.db"
    if os.path.exists(db_path):
        return send_from_directory(".", db_path, as_attachment=True)
    return jsonify({"error": "Database file not found"}), 404

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/generate", methods=["POST"])
def generate_quick_prompt():
    """
    Fast homepage generation endpoint connected to the multi-provider AI engine.
    """
    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Missing prompt in request"}), 400

    try:
        gen_result = orchestrator.generate_image(prompt=prompt)
        return jsonify({
            "image": gen_result.image_url,
            "prompt": prompt,
            "explanation": gen_result.explanation,
            "provider": gen_result.metadata.get("provider", "ai_engine")
        })
    except Exception as e:
        print(f"Error in /generate: {e}")
        return jsonify({"error": "Failed to generate design", "details": str(e)}), 500

@app.route("/api/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        data = request.get_json() or {}
        if "gemini_api_key" in data:
            os.environ["GEMINI_API_KEY"] = data["gemini_api_key"].strip()
            orchestrator.gemini.api_key = data["gemini_api_key"].strip()
        if "colab_url" in data:
            os.environ["COLAB_API"] = data["colab_url"].strip()
            orchestrator.colab.endpoint_url = data["colab_url"].strip()
        return jsonify({"status": "success", "message": "Configuration updated successfully"})

    return jsonify({
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "colab_api": os.getenv("COLAB_API", "")
    })

# ==============================================================================
# 2. AUTHENTICATION APIs
# ==============================================================================

@app.route("/api/auth/signup", methods=["POST"])
def auth_signup():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400

    existing = db_session.query(User).filter_by(email=email).first()
    if existing:
        return jsonify({"error": "An account with this email already exists"}), 400

    user = User(name=name, email=email)
    user.set_password(password)
    db_session.add(user)
    db_session.commit()

    session["user_id"] = user.id
    session["user_name"] = user.name
    return jsonify({"status": "success", "user": user.to_dict()}), 201

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = db_session.query(User).filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user.id
    session["user_name"] = user.name
    return jsonify({"status": "success", "user": user.to_dict()})

@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully"})

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False, "user": None})

    user = db_session.query(User).filter_by(id=user_id).first()
    if not user:
        session.clear()
        return jsonify({"authenticated": False, "user": None})

    return jsonify({"authenticated": True, "user": user.to_dict()})

# ==============================================================================
# 3. DATABASE EXPLORER / ADMIN APIs
# ==============================================================================

@app.route("/api/admin/db/tables", methods=["GET"])
@admin_required
def get_db_tables():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    tables_info = []

    for name in table_names:
        try:
            count_res = db_session.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar()
            tables_info.append({
                "name": name,
                "row_count": count_res or 0
            })
        except Exception:
            tables_info.append({"name": name, "row_count": 0})

    return jsonify({"tables": tables_info})

@app.route("/api/admin/db/table/<table_name>", methods=["GET"])
@admin_required
def get_db_table_data(table_name):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return jsonify({"error": "Table not found"}), 404

    columns = [col["name"] for col in inspector.get_columns(table_name)]

    try:
        query_res = db_session.execute(text(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 100"))
        rows = [dict(zip(columns, row)) for row in query_res.fetchall()]
        return jsonify({
            "table_name": table_name,
            "columns": columns,
            "rows": rows,
            "total_returned": len(rows)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/db/user/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_db_user(user_id):
    current_admin_id = session.get("user_id")
    if current_admin_id == user_id:
        return jsonify({"error": "You cannot delete your own active admin account."}), 400

    user = db_session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    db_session.delete(user)
    db_session.commit()
    return jsonify({"status": "success", "message": f"User '{user.name}' (ID: {user_id}) deleted successfully."})

@app.route("/api/admin/db/table/<table_name>/<row_id>", methods=["DELETE"])
@admin_required
def delete_db_table_row(table_name, row_id):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return jsonify({"error": "Table not found"}), 404

    if table_name == "users" and str(session.get("user_id")) == str(row_id):
        return jsonify({"error": "You cannot delete your own active admin account."}), 400

    try:
        if table_name == "users":
            user = db_session.query(User).filter_by(id=row_id).first()
            if user:
                db_session.delete(user)
                db_session.commit()
                return jsonify({"status": "success", "message": f"User '{user.name}' (ID: {row_id}) deleted successfully."})
            return jsonify({"error": "User not found"}), 404
        elif table_name == "house_projects":
            house = db_session.query(HouseProject).filter_by(id=row_id).first()
            if house:
                db_session.delete(house)
                db_session.commit()
                return jsonify({"status": "success", "message": f"House project (ID: {row_id}) deleted successfully."})
            return jsonify({"error": "House project not found"}), 404
        else:
            db_session.execute(text(f"DELETE FROM {table_name} WHERE id = :id"), {"id": row_id})
            db_session.commit()
            return jsonify({"status": "success", "message": f"Record (ID: {row_id}) deleted from '{table_name}'."})
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/db/query", methods=["POST"])
@admin_required
def run_db_query():
    data = request.get_json() or {}
    raw_query = data.get("query", "").strip()

    if not raw_query:
        return jsonify({"error": "Query cannot be empty"}), 400

    start_time = time.time()
    try:
        result = db_session.execute(text(raw_query))
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        if result.returns_rows:
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return jsonify({
                "columns": columns,
                "rows": rows,
                "execution_time_ms": elapsed_ms
            })
        else:
            db_session.commit()
            return jsonify({
                "columns": [],
                "rows": [],
                "message": f"Query executed successfully ({result.rowcount} rows affected)",
                "execution_time_ms": elapsed_ms
            })
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400

# ==============================================================================
# 4. HOUSE PROJECT APIs (LEVEL 2)
# ==============================================================================

def generate_default_rooms_for_config(config_type: str, num_villas: int = 1, custom_count: int = 6):
    def get_unit_rooms(prefix=""):
        if config_type == "1bhk":
            return [
                {"name": f"{prefix}Living Room", "room_type": "living_room", "length_ft": 16, "width_ft": 14},
                {"name": f"{prefix}Master Bedroom", "room_type": "master_bedroom", "length_ft": 14, "width_ft": 12},
                {"name": f"{prefix}Kitchen", "room_type": "kitchen", "length_ft": 10, "width_ft": 8},
                {"name": f"{prefix}Bathroom 1", "room_type": "bathroom", "length_ft": 8, "width_ft": 6},
                {"name": f"{prefix}Balcony", "room_type": "balcony", "length_ft": 10, "width_ft": 4}
            ]
        elif config_type == "2bhk":
            return [
                {"name": f"{prefix}Living Room", "room_type": "living_room", "length_ft": 18, "width_ft": 14},
                {"name": f"{prefix}Master Bedroom", "room_type": "master_bedroom", "length_ft": 15, "width_ft": 13},
                {"name": f"{prefix}Kids Bedroom", "room_type": "kids_bedroom", "length_ft": 13, "width_ft": 11},
                {"name": f"{prefix}Kitchen", "room_type": "kitchen", "length_ft": 12, "width_ft": 10},
                {"name": f"{prefix}Dining Room", "room_type": "dining_room", "length_ft": 11, "width_ft": 10},
                {"name": f"{prefix}Bathroom 1", "room_type": "bathroom", "length_ft": 8, "width_ft": 6},
                {"name": f"{prefix}Balcony", "room_type": "balcony", "length_ft": 12, "width_ft": 5}
            ]
        elif config_type == "4bhk_villa":
            return [
                {"name": f"{prefix}Grand Living Room", "room_type": "living_room", "length_ft": 24, "width_ft": 16},
                {"name": f"{prefix}Master Bedroom Suite", "room_type": "master_bedroom", "length_ft": 18, "width_ft": 15},
                {"name": f"{prefix}Kids Bedroom", "room_type": "kids_bedroom", "length_ft": 15, "width_ft": 13},
                {"name": f"{prefix}Guest Bedroom", "room_type": "guest_bedroom", "length_ft": 14, "width_ft": 12},
                {"name": f"{prefix}Parents Bedroom", "room_type": "bedroom", "length_ft": 15, "width_ft": 13},
                {"name": f"{prefix}Gourmet Kitchen", "room_type": "kitchen", "length_ft": 16, "width_ft": 12},
                {"name": f"{prefix}Formal Dining Room", "room_type": "dining_room", "length_ft": 15, "width_ft": 12},
                {"name": f"{prefix}Master Spa Bathroom", "room_type": "bathroom", "length_ft": 10, "width_ft": 8},
                {"name": f"{prefix}Common Bathroom", "room_type": "bathroom", "length_ft": 8, "width_ft": 6},
                {"name": f"{prefix}Pooja Room", "room_type": "pooja_room", "length_ft": 8, "width_ft": 6},
                {"name": f"{prefix}Home Office / Study", "room_type": "home_office", "length_ft": 12, "width_ft": 10},
                {"name": f"{prefix}Panoramic Balcony", "room_type": "balcony", "length_ft": 16, "width_ft": 6}
            ]
        elif config_type == "5bhk_estate":
            return [
                {"name": f"{prefix}Grand Living Hall", "room_type": "living_room", "length_ft": 26, "width_ft": 18},
                {"name": f"{prefix}Master Suite", "room_type": "master_bedroom", "length_ft": 20, "width_ft": 16},
                {"name": f"{prefix}Kids Bedroom", "room_type": "kids_bedroom", "length_ft": 15, "width_ft": 13},
                {"name": f"{prefix}Guest Suite", "room_type": "guest_bedroom", "length_ft": 15, "width_ft": 13},
                {"name": f"{prefix}Bedroom 4", "room_type": "bedroom", "length_ft": 14, "width_ft": 13},
                {"name": f"{prefix}Bedroom 5", "room_type": "bedroom", "length_ft": 14, "width_ft": 12},
                {"name": f"{prefix}Chef Kitchen", "room_type": "kitchen", "length_ft": 18, "width_ft": 12},
                {"name": f"{prefix}Formal Dining", "room_type": "dining_room", "length_ft": 16, "width_ft": 14},
                {"name": f"{prefix}Master Spa Bathroom", "room_type": "bathroom", "length_ft": 12, "width_ft": 9},
                {"name": f"{prefix}Common Bathroom", "room_type": "bathroom", "length_ft": 8, "width_ft": 6},
                {"name": f"{prefix}Pooja Sanctuary", "room_type": "pooja_room", "length_ft": 9, "width_ft": 7},
                {"name": f"{prefix}Home Theatre / Lounge", "room_type": "living_room", "length_ft": 16, "width_ft": 14},
                {"name": f"{prefix}Study / Office", "room_type": "home_office", "length_ft": 14, "width_ft": 11},
                {"name": f"{prefix}Terrace Lounge", "room_type": "terrace", "length_ft": 20, "width_ft": 12},
                {"name": f"{prefix}Balcony", "room_type": "balcony", "length_ft": 18, "width_ft": 6}
            ]
        elif config_type == "custom":
            all_types = [
                ("Living Room", "living_room"), ("Master Bedroom", "master_bedroom"),
                ("Kitchen", "kitchen"), ("Dining Room", "dining_room"),
                ("Kids Bedroom", "kids_bedroom"), ("Guest Bedroom", "guest_bedroom"),
                ("Pooja Room", "pooja_room"), ("Home Office", "home_office"),
                ("Bathroom 1", "bathroom"), ("Bathroom 2", "bathroom"),
                ("Balcony", "balcony"), ("Terrace", "terrace")
            ]
            res = []
            for i in range(min(max(custom_count, 1), len(all_types))):
                name, rtype = all_types[i]
                res.append({"name": f"{prefix}{name}", "room_type": rtype, "length_ft": 14, "width_ft": 12})
            return res
        else:  # Default 3bhk
            return [
                {"name": f"{prefix}Living Room", "room_type": "living_room", "length_ft": 20, "width_ft": 15},
                {"name": f"{prefix}Master Bedroom", "room_type": "master_bedroom", "length_ft": 16, "width_ft": 14},
                {"name": f"{prefix}Kids Bedroom", "room_type": "kids_bedroom", "length_ft": 14, "width_ft": 12},
                {"name": f"{prefix}Guest Bedroom", "room_type": "guest_bedroom", "length_ft": 13, "width_ft": 12},
                {"name": f"{prefix}Kitchen", "room_type": "kitchen", "length_ft": 14, "width_ft": 10},
                {"name": f"{prefix}Dining Room", "room_type": "dining_room", "length_ft": 13, "width_ft": 11},
                {"name": f"{prefix}Bathroom 1", "room_type": "bathroom", "length_ft": 8, "width_ft": 6},
                {"name": f"{prefix}Pooja Room", "room_type": "pooja_room", "length_ft": 8, "width_ft": 6},
                {"name": f"{prefix}Balcony", "room_type": "balcony", "length_ft": 14, "width_ft": 5}
            ]

    all_rooms = []
    if num_villas > 1:
        for v in range(1, num_villas + 1):
            all_rooms.extend(get_unit_rooms(f"Villa {v} - "))
    else:
        all_rooms = get_unit_rooms("")
    return all_rooms

@app.route("/api/house/create", methods=["POST"])
def create_house_project():
    data = request.get_json() or {}
    name = data.get("name", "My Dream Home").strip()
    total_budget = float(data.get("total_budget", 1500000.0))
    approx_area = float(data.get("approx_area_sqft", 1500.0))
    floors = int(data.get("floors", 1))
    lifestyle = data.get("lifestyle_requirements", ["Family", "Work from Home"])
    style = data.get("primary_style", "Modern Luxury")
    room_config = data.get("room_config", "3bhk")
    num_villas = int(data.get("num_villas", 1))
    num_rooms = int(data.get("num_rooms", 6))
    user_id = session.get("user_id")

    house = HouseProject(
        user_id=user_id,
        name=name,
        total_budget=total_budget,
        approx_area_sqft=approx_area,
        floors=floors,
        lifestyle_requirements=json.dumps(lifestyle)
    )
    db_session.add(house)
    db_session.flush()

    # Create House Style Profile
    style_profile = HouseStyleProfile(
        house_id=house.id,
        primary_style=style,
        main_palette=json.dumps(data.get("main_palette", ["Warm White", "Beige", "Walnut"])),
        accent_materials=json.dumps(data.get("accent_materials", ["Walnut Wood", "Fluted Glass"])),
        metal_finish=data.get("metal_finish", "Matte Black"),
        lighting_temp=data.get("lighting_temp", "Warm White (3000K)"),
        flooring_spec=data.get("flooring_spec", "Light Italian Marble")
    )
    db_session.add(style_profile)

    # Populate Rooms based on room_config and num_villas if not explicitly given
    rooms_input = data.get("rooms")
    if not rooms_input:
        rooms_input = generate_default_rooms_for_config(room_config, num_villas=num_villas, custom_count=num_rooms)

    for r_data in rooms_input:
        r_name = r_data.get("name", "Room")
        r_type = r_data.get("room_type")
        resolved_type = normalize_room_type(r_name if not r_type or r_type == 'living_room' else r_type)

        room = Room(
            house_id=house.id,
            name=r_name,
            room_type=resolved_type,
            floor_number=int(r_data.get("floor_number", 1)),
            length_ft=float(r_data.get("length_ft", 14.0)),
            width_ft=float(r_data.get("width_ft", 12.0)),
            height_ft=float(r_data.get("height_ft", 10.0)),
            windows_count=int(r_data.get("windows_count", 1)),
            doors_count=int(r_data.get("doors_count", 1)),
            natural_light_level=r_data.get("natural_light_level", "moderate")
        )
        db_session.add(room)

    db_session.commit()
    return jsonify({"status": "success", "house": house.to_dict()}), 201

@app.route("/api/houses", methods=["GET"])
def list_houses():
    user_id = session.get("user_id")
    query = db_session.query(HouseProject)
    if user_id:
        # Show user's houses or public starter houses
        houses = query.filter((HouseProject.user_id == user_id) | (HouseProject.user_id.is_(None))).order_by(HouseProject.created_at.desc()).all()
    else:
        houses = query.order_by(HouseProject.created_at.desc()).all()

    return jsonify({"houses": [h.to_dict() for h in houses]})

@app.route("/api/house/<int:house_id>", methods=["GET", "DELETE"])
def house_detail_or_delete(house_id):
    house = db_session.query(HouseProject).filter_by(id=house_id).first()
    if not house:
        return jsonify({"error": "House project not found"}), 404

    if request.method == "DELETE":
        db_session.delete(house)
        db_session.commit()
        return jsonify({"status": "success", "message": "House project deleted successfully"})

    return jsonify({"house": house.to_dict()})

@app.route("/api/house/<int:house_id>/profile", methods=["POST", "PUT"])
def update_house_style_profile(house_id):
    house = db_session.query(HouseProject).filter_by(id=house_id).first()
    if not house:
        return jsonify({"error": "House project not found"}), 404

    data = request.get_json() or {}
    profile = house.style_profile
    if not profile:
        profile = HouseStyleProfile(house_id=house.id)
        db_session.add(profile)

    if "primary_style" in data and data["primary_style"]:
        profile.primary_style = data["primary_style"].strip()
    if "main_palette" in data:
        palette = data["main_palette"]
        if isinstance(palette, str):
            palette = [c.strip() for c in palette.split(",") if c.strip()]
        profile.main_palette = json.dumps(palette)
    if "accent_materials" in data:
        materials = data["accent_materials"]
        if isinstance(materials, str):
            materials = [m.strip() for m in materials.split(",") if m.strip()]
        profile.accent_materials = json.dumps(materials)
    if "metal_finish" in data and data["metal_finish"]:
        profile.metal_finish = data["metal_finish"].strip()
    if "lighting_temp" in data and data["lighting_temp"]:
        profile.lighting_temp = data["lighting_temp"].strip()
    if "flooring_spec" in data and data["flooring_spec"]:
        profile.flooring_spec = data["flooring_spec"].strip()

    db_session.commit()
    return jsonify({"status": "success", "style_profile": profile.to_dict()})

@app.route("/api/house/<int:house_id>/rooms", methods=["POST"])
def add_rooms_to_house(house_id):
    house = db_session.query(HouseProject).filter_by(id=house_id).first()
    if not house:
        return jsonify({"error": "House project not found"}), 404

    data = request.get_json() or {}
    rooms_data = data.get("rooms", [data] if "name" in data else [])

    added_rooms = []
    for r_data in rooms_data:
        name = r_data.get("name", "New Room")
        raw_type = r_data.get("room_type")
        if not raw_type or raw_type == "living_room":
            resolved_type = normalize_room_type(name)
        else:
            resolved_type = normalize_room_type(raw_type)

        room = Room(
            house_id=house.id,
            name=name,
            room_type=resolved_type,
            floor_number=int(r_data.get("floor_number", 1)),
            length_ft=float(r_data.get("length_ft", 14.0)),
            width_ft=float(r_data.get("width_ft", 12.0)),
            height_ft=float(r_data.get("height_ft", 10.0)),
            windows_count=int(r_data.get("windows_count", 1)),
            doors_count=int(r_data.get("doors_count", 1)),
            natural_light_level=r_data.get("natural_light_level", "moderate")
        )
        db_session.add(room)
        added_rooms.append(room)

    db_session.commit()
    return jsonify({"status": "success", "added_rooms": [r.to_dict() for r in added_rooms]}), 201

@app.route("/api/house/<int:house_id>/generate", methods=["POST"])
def generate_whole_house_design(house_id):
    """
    Generate a unified interior design across all rooms in the house project.
    """
    house = db_session.query(HouseProject).filter_by(id=house_id).first()
    if not house:
        return jsonify({"error": "House project not found"}), 404

    style_profile = house.style_profile.to_dict() if house.style_profile else {
        "primary_style": "Modern Luxury",
        "main_palette": ["Warm White", "Beige", "Walnut Wood"],
        "accent_materials": ["Walnut Wood", "Fluted Glass"],
        "metal_finish": "Matte Black",
        "flooring_spec": "Light Italian Marble"
    }

    generated_designs = []
    for room in house.rooms:
        # Clean previous designs for this room to ensure 1 latest design per room
        for old_d in room.designs:
            db_session.delete(old_d)

        effective_room_type = normalize_room_type(room.room_type)
        if effective_room_type == "living_room" and room.name and "living" not in room.name.lower():
            effective_room_type = normalize_room_type(room.name)

        v_analysis = room.analysis.to_dict() if room.analysis else None
        u_prefs = room.preferences.to_dict() if room.preferences else None

        # Generate room visualization
        design_output = design_engine.generate_room_design(
            room_type=effective_room_type,
            style=style_profile["primary_style"],
            house_style_profile=style_profile,
            user_preferences=u_prefs,
            vision_analysis=v_analysis
        )

        design = Design(
            room_id=room.id,
            house_id=house.id,
            title=f"{style_profile['primary_style']} {room.name}",
            image_url=design_output["image_url"],
            prompt=design_output["prompt"],
            explanation=design_output["explanation"]
        )
        db_session.add(design)
        db_session.flush()

        # Generate & store furniture recommendations
        recs = furniture_engine.get_recommendations(room.room_type, style_profile["primary_style"])
        for r_item in recs:
            rec = FurnitureRecommendation(
                room_id=room.id,
                design_id=design.id,
                name=r_item["name"],
                category=r_item["category"],
                dimensions=r_item["dimensions"],
                estimated_cost=r_item["estimated_cost"],
                location_hint=r_item["location_hint"],
                reason=r_item["reason"]
            )
            db_session.add(rec)

        # Generate & store cost estimate
        area = room.length_ft * room.width_ft
        c_est = cost_estimator.estimate_room_cost(room.room_type, area, style_profile["primary_style"])
        cost = CostEstimate(
            room_id=room.id,
            house_id=house.id,
            design_id=design.id,
            furniture_cost=c_est["furniture_cost"],
            materials_cost=c_est["materials_cost"],
            lighting_cost=c_est["lighting_cost"],
            paint_cost=c_est["paint_cost"],
            decor_cost=c_est["decor_cost"],
            total_cost=c_est["total_cost"]
        )
        db_session.add(cost)

        generated_designs.append(design.to_dict())

    db_session.commit()
    return jsonify({
        "status": "success",
        "house_id": house.id,
        "style_profile": style_profile,
        "designs": generated_designs
    })

@app.route("/api/house/<int:house_id>/designs", methods=["GET"])
def get_house_designs(house_id):
    house = db_session.query(HouseProject).filter_by(id=house_id).first()
    if not house:
        return jsonify({"error": "House project not found"}), 404

    latest_designs = []
    for room in house.rooms:
        if room.designs:
            latest_designs.append(room.designs[-1])

    return jsonify({"designs": [d.to_dict() for d in latest_designs]})

@app.route("/api/house/<int:house_id>/cost", methods=["GET"])
def get_house_cost_estimate(house_id):
    house = db_session.query(HouseProject).filter_by(id=house_id).first()
    if not house:
        return jsonify({"error": "House project not found"}), 404

    style = house.style_profile.primary_style if house.style_profile else "Modern Luxury"
    rooms_data = [r.to_dict() for r in house.rooms]
    house_cost = cost_estimator.estimate_house_cost(rooms_data, style)

    return jsonify({
        "house_id": house.id,
        "house_name": house.name,
        "total_budget": house.total_budget,
        "estimated_cost": house_cost
    })

# ==============================================================================
# 5. ROOM LEVEL APIs (LEVEL 1)
# ==============================================================================

@app.route("/api/room/<int:room_id>", methods=["GET"])
def get_room(room_id):
    room = db_session.query(Room).filter_by(id=room_id).first()
    if not room:
        return jsonify({"error": "Room not found"}), 404
    return jsonify({"room": room.to_dict(include_details=True)})

@app.route("/api/room/<int:room_id>/upload", methods=["POST"])
def upload_room_images(room_id):
    room = db_session.query(Room).filter_by(id=room_id).first()
    if not room:
        return jsonify({"error": "Room not found"}), 404

    if 'images' not in request.files and 'image' not in request.files:
        return jsonify({"error": "No image files provided in request"}), 400

    files = request.files.getlist('images') or [request.files.get('image')]
    is_floor_plan = request.form.get("is_floor_plan", "false").lower() == "true"
    angle_desc = request.form.get("angle_description", "main_view")

    saved_images = []
    for file in files:
        if file and file.filename:
            filename = f"room_{room_id}_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            room_img = RoomImage(
                room_id=room.id,
                image_path=filepath,
                angle_description=angle_desc,
                is_floor_plan=is_floor_plan
            )
            db_session.add(room_img)
            saved_images.append(room_img)

    db_session.commit()
    return jsonify({
        "status": "success",
        "uploaded_images": [img.to_dict() for img in saved_images]
    }), 201

@app.route("/api/room/<int:room_id>/analyze", methods=["POST"])
def analyze_room(room_id):
    room = db_session.query(Room).filter_by(id=room_id).first()
    if not room:
        return jsonify({"error": "Room not found"}), 404

    image_paths = [img.image_path for img in room.images if os.path.exists(img.image_path)]
    context = {"room_type": room.room_type, "room_name": room.name}

    analysis_res = image_analyzer.analyze_room(image_paths, context)

    # Persist or update RoomAnalysis
    existing_analysis = db_session.query(RoomAnalysis).filter_by(room_id=room_id).first()
    if existing_analysis:
        existing_analysis.room_type = analysis_res.room_type
        existing_analysis.estimated_size = analysis_res.estimated_size
        existing_analysis.detected_style = analysis_res.detected_style
        existing_analysis.dominant_colors = json.dumps(analysis_res.dominant_colors)
        existing_analysis.detected_objects = json.dumps(analysis_res.detected_objects)
        existing_analysis.structure_info = json.dumps(analysis_res.structure_info)
        existing_analysis.lighting_analysis = json.dumps(analysis_res.lighting_analysis)
        existing_analysis.floor_material = analysis_res.floor_material
        existing_analysis.raw_analysis = json.dumps(analysis_res.raw_analysis)
        existing_analysis.analyzed_at = datetime.utcnow()
        analysis_record = existing_analysis
    else:
        analysis_record = RoomAnalysis(
            room_id=room_id,
            room_type=analysis_res.room_type,
            estimated_size=analysis_res.estimated_size,
            detected_style=analysis_res.detected_style,
            dominant_colors=json.dumps(analysis_res.dominant_colors),
            detected_objects=json.dumps(analysis_res.detected_objects),
            structure_info=json.dumps(analysis_res.structure_info),
            lighting_analysis=json.dumps(analysis_res.lighting_analysis),
            floor_material=analysis_res.floor_material,
            raw_analysis=json.dumps(analysis_res.raw_analysis)
        )
        db_session.add(analysis_record)

    db_session.commit()
    return jsonify({
        "status": "success",
        "room_id": room_id,
        "analysis": analysis_record.to_dict()
    })

@app.route("/api/room/<int:room_id>/generate", methods=["POST"])
def generate_room_design_endpoint(room_id):
    room = db_session.query(Room).filter_by(id=room_id).first()
    if not room:
        return jsonify({"error": "Room not found"}), 404

    data = request.get_json() or {}
    style = data.get("style") or (room.house.style_profile.primary_style if room.house and room.house.style_profile else "Modern Luxury")
    custom_palette = data.get("palette") or data.get("color_palette")

    house_profile = room.house.style_profile.to_dict() if room.house and room.house.style_profile else None
    if custom_palette and house_profile:
        if isinstance(custom_palette, str):
            custom_palette = [c.strip() for c in custom_palette.split(",") if c.strip()]
        house_profile = dict(house_profile)
        house_profile["main_palette"] = custom_palette

    v_analysis = room.analysis.to_dict() if room.analysis else None
    u_prefs = room.preferences.to_dict() if room.preferences else data.get("preferences")

    # Clean previous designs for this room to ensure 1 latest design
    for old_d in room.designs:
        db_session.delete(old_d)

    # Get reference image if available
    ref_img = room.images[0].image_path if room.images and os.path.exists(room.images[0].image_path) else None

    effective_room_type = normalize_room_type(room.room_type)
    if effective_room_type == "living_room" and room.name and "living" not in room.name.lower():
        effective_room_type = normalize_room_type(room.name)

    design_out = design_engine.generate_room_design(
        room_type=effective_room_type,
        style=style,
        house_style_profile=house_profile,
        user_preferences=u_prefs,
        vision_analysis=v_analysis,
        reference_image_path=ref_img
    )

    design = Design(
        room_id=room.id,
        house_id=room.house_id,
        title=f"{style} {room.name}",
        image_url=design_out["image_url"],
        prompt=design_out["prompt"],
        explanation=design_out["explanation"]
    )
    db_session.add(design)
    db_session.flush()

    # Generate furniture & materials & cost
    recs = furniture_engine.get_recommendations(effective_room_type, style)
    for r_item in recs:
        rec = FurnitureRecommendation(
            room_id=room.id,
            design_id=design.id,
            name=r_item["name"],
            category=r_item["category"],
            dimensions=r_item["dimensions"],
            estimated_cost=r_item["estimated_cost"],
            location_hint=r_item["location_hint"],
            reason=r_item["reason"]
        )
        db_session.add(rec)

    area = room.length_ft * room.width_ft
    c_est = cost_estimator.estimate_room_cost(room.room_type, area, style)
    cost = CostEstimate(
        room_id=room.id,
        house_id=room.house_id,
        design_id=design.id,
        furniture_cost=c_est["furniture_cost"],
        materials_cost=c_est["materials_cost"],
        lighting_cost=c_est["lighting_cost"],
        paint_cost=c_est["paint_cost"],
        decor_cost=c_est["decor_cost"],
        total_cost=c_est["total_cost"]
    )
    db_session.add(cost)
    db_session.commit()

    materials = material_lighting_engine.get_material_recommendations(room.room_type, style)
    lighting = material_lighting_engine.get_lighting_recommendations(room.room_type, style)

    return jsonify({
        "status": "success",
        "design": design.to_dict(),
        "furniture_recommendations": [r.to_dict() for r in design.recommendations],
        "materials": materials,
        "lighting": lighting,
        "cost_estimate": cost.to_dict()
    }), 201

# ==============================================================================
# 6. DESIGN CHATBOT & COST APIs
# ==============================================================================

@app.route("/api/design/<int:design_id>", methods=["GET"])
def get_design(design_id):
    design = db_session.query(Design).filter_by(id=design_id).first()
    if not design:
        return jsonify({"error": "Design not found"}), 404

    room = design.room
    style = design.title.split()[0] if design.title else "Modern Luxury"
    room_type = room.room_type if room else "living_room"

    materials = material_lighting_engine.get_material_recommendations(room_type, style)
    lighting = material_lighting_engine.get_lighting_recommendations(room_type, style)

    return jsonify({
        "design": design.to_dict(),
        "furniture_recommendations": [r.to_dict() for r in design.recommendations],
        "materials": materials,
        "lighting": lighting,
        "cost_estimate": design.cost_estimate.to_dict() if design.cost_estimate else None,
        "chats": [c.to_dict() for c in design.chats]
    })

@app.route("/api/design/<int:design_id>/chat", methods=["POST"])
def design_chat(design_id):
    """
    Contextual AI chatbot conversing with house, room, and design memory.
    """
    design = db_session.query(Design).filter_by(id=design_id).first()
    if not design:
        return jsonify({"error": "Design not found"}), 404

    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Save User message
    user_chat = DesignChat(
        house_id=design.house_id,
        room_id=design.room_id,
        design_id=design.id,
        role="user",
        message=user_message
    )
    db_session.add(user_chat)
    db_session.flush()

    # Gather conversation context
    past_chats = db_session.query(DesignChat).filter_by(design_id=design.id).order_by(DesignChat.created_at.asc()).all()
    messages_history = [{"role": c.role, "message": c.message} for c in past_chats]

    room = design.room
    house = design.house
    chat_context = {
        "house_name": house.name if house else "My House",
        "room_name": room.name if room else "Room",
        "room_type": room.room_type if room else "living_room",
        "style": house.style_profile.primary_style if house and house.style_profile else "Modern Luxury",
        "budget": house.total_budget if house else 1500000
    }

    # Generate AI Response via Orchestrator
    ai_reply_text = orchestrator.generate_chat_response(messages_history, chat_context)

    ai_chat = DesignChat(
        house_id=design.house_id,
        room_id=design.room_id,
        design_id=design.id,
        role="assistant",
        message=ai_reply_text
    )
    db_session.add(ai_chat)
    db_session.commit()

    return jsonify({
        "status": "success",
        "reply": ai_reply_text,
        "chat": ai_chat.to_dict()
    })

@app.route("/api/design/<int:design_id>/cost", methods=["GET"])
def get_design_cost(design_id):
    design = db_session.query(Design).filter_by(id=design_id).first()
    if not design:
        return jsonify({"error": "Design not found"}), 404

    if design.cost_estimate:
        return jsonify({"cost_estimate": design.cost_estimate.to_dict()})

    room = design.room
    area = (room.length_ft * room.width_ft) if room else 180.0
    r_type = room.room_type if room else "living_room"
    c_est = cost_estimator.estimate_room_cost(r_type, area)

    return jsonify({"cost_estimate": c_est})

# ==============================================================================
# 7. ASYNC JOBS API
# ==============================================================================

@app.route("/api/jobs/<job_id>", methods=["GET"])
def get_job_status(job_id):
    job = db_session.query(AsyncJob).filter_by(id=job_id).first()
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"job": job.to_dict()})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f">> Starting DecoraAI Interior Design Engine on http://127.0.0.1:{port}")
    app.run(debug=True, host="127.0.0.1", port=port)