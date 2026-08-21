import os
import json
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session

from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///interior_design.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    houses = relationship("HouseProject", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "houses_count": len(self.houses) if self.houses else 0
        }

class HouseProject(Base):
    __tablename__ = "house_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(200), nullable=False)
    approx_area_sqft = Column(Float, default=1500.0)
    floors = Column(Integer, default=1)
    total_budget = Column(Float, default=1500000.0)
    lifestyle_requirements = Column(Text, default="[]")  # JSON list
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="houses")
    rooms = relationship("Room", back_populates="house", cascade="all, delete-orphan")
    style_profile = relationship("HouseStyleProfile", back_populates="house", uselist=False, cascade="all, delete-orphan")
    designs = relationship("Design", back_populates="house", cascade="all, delete-orphan")
    cost_estimate = relationship("CostEstimate", back_populates="house", uselist=False, cascade="all, delete-orphan")
    chats = relationship("DesignChat", back_populates="house", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "approx_area_sqft": self.approx_area_sqft,
            "floors": self.floors,
            "total_budget": self.total_budget,
            "lifestyle_requirements": json.loads(self.lifestyle_requirements) if self.lifestyle_requirements else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "rooms": [r.to_dict(include_details=False) for r in self.rooms],
            "style_profile": self.style_profile.to_dict() if self.style_profile else None
        }

class HouseStyleProfile(Base):
    __tablename__ = "house_style_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey("house_projects.id"), nullable=False, unique=True)
    primary_style = Column(String(100), default="Modern Luxury")
    main_palette = Column(Text, default='["Warm White", "Beige", "Soft Gray"]')  # JSON list
    accent_materials = Column(Text, default='["Walnut Wood", "Fluted Glass"]')    # JSON list
    metal_finish = Column(String(100), default="Matte Black")
    lighting_temp = Column(String(100), default="Warm White (3000K)")
    flooring_spec = Column(String(100), default="Light Italian Marble")

    house = relationship("HouseProject", back_populates="style_profile")

    def to_dict(self):
        return {
            "id": self.id,
            "house_id": self.house_id,
            "primary_style": self.primary_style,
            "main_palette": json.loads(self.main_palette) if self.main_palette else [],
            "accent_materials": json.loads(self.accent_materials) if self.accent_materials else [],
            "metal_finish": self.metal_finish,
            "lighting_temp": self.lighting_temp,
            "flooring_spec": self.flooring_spec
        }

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey("house_projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    room_type = Column(String(100), default="living_room")  # living_room, master_bedroom, kitchen, etc.
    floor_number = Column(Integer, default=1)
    length_ft = Column(Float, default=14.0)
    width_ft = Column(Float, default=12.0)
    height_ft = Column(Float, default=10.0)
    windows_count = Column(Integer, default=1)
    doors_count = Column(Integer, default=1)
    natural_light_level = Column(String(50), default="moderate") # high, moderate, low
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    house = relationship("HouseProject", back_populates="rooms")
    images = relationship("RoomImage", back_populates="room", cascade="all, delete-orphan")
    analysis = relationship("RoomAnalysis", back_populates="room", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="room", uselist=False, cascade="all, delete-orphan")
    designs = relationship("Design", back_populates="room", cascade="all, delete-orphan")
    recommendations = relationship("FurnitureRecommendation", back_populates="room", cascade="all, delete-orphan")
    cost_estimates = relationship("CostEstimate", back_populates="room", cascade="all, delete-orphan")

    def to_dict(self, include_details=True):
        data = {
            "id": self.id,
            "house_id": self.house_id,
            "name": self.name,
            "room_type": self.room_type,
            "floor_number": self.floor_number,
            "dimensions": {
                "length_ft": self.length_ft,
                "width_ft": self.width_ft,
                "height_ft": self.height_ft,
                "area_sqft": round(self.length_ft * self.width_ft, 1)
            },
            "windows_count": self.windows_count,
            "doors_count": self.doors_count,
            "natural_light_level": self.natural_light_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "images_count": len(self.images),
            "designs_count": len(self.designs),
            "latest_design_image": self.designs[-1].image_url if self.designs else None
        }
        if include_details:
            data["images"] = [img.to_dict() for img in self.images]
            data["analysis"] = self.analysis.to_dict() if self.analysis else None
            data["preferences"] = self.preferences.to_dict() if self.preferences else None
            data["designs"] = [d.to_dict() for d in self.designs]
            data["recommendations"] = [r.to_dict() for r in self.recommendations]
            data["cost_estimate"] = self.cost_estimates[-1].to_dict() if self.cost_estimates else None
        return data

class RoomImage(Base):
    __tablename__ = "room_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    image_path = Column(String(500), nullable=False)
    angle_description = Column(String(100), default="main_view")
    is_floor_plan = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="images")

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "image_path": self.image_path,
            "angle_description": self.angle_description,
            "is_floor_plan": self.is_floor_plan,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }

class RoomAnalysis(Base):
    __tablename__ = "room_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, unique=True)
    room_type = Column(String(100))
    estimated_size = Column(String(50), default="medium")
    detected_style = Column(String(100), default="Contemporary")
    dominant_colors = Column(Text, default="[]")  # JSON list
    detected_objects = Column(Text, default="[]") # JSON list
    structure_info = Column(Text, default="{}")   # JSON dict
    lighting_analysis = Column(Text, default="{}")# JSON dict
    floor_material = Column(String(100), default="Unknown")
    raw_analysis = Column(Text, default="{}")     # Full AI output
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="analysis")

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "room_type": self.room_type,
            "estimated_size": self.estimated_size,
            "detected_style": self.detected_style,
            "dominant_colors": json.loads(self.dominant_colors) if self.dominant_colors else [],
            "detected_objects": json.loads(self.detected_objects) if self.detected_objects else [],
            "structure_info": json.loads(self.structure_info) if self.structure_info else {},
            "lighting_analysis": json.loads(self.lighting_analysis) if self.lighting_analysis else {},
            "floor_material": self.floor_material,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None
        }

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    style = Column(String(100), default="Modern Luxury")
    primary_color = Column(String(50), default="Warm White")
    secondary_color = Column(String(50), default="Beige")
    accent_color = Column(String(50), default="Walnut")
    avoid_colors = Column(Text, default="[]")          # JSON list
    preferred_materials = Column(Text, default="[]")   # JSON list
    lifestyle_requirements = Column(Text, default="[]")# JSON list
    special_instructions = Column(Text, default="")

    room = relationship("Room", back_populates="preferences")

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "style": self.style,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "accent_color": self.accent_color,
            "avoid_colors": json.loads(self.avoid_colors) if self.avoid_colors else [],
            "preferred_materials": json.loads(self.preferred_materials) if self.preferred_materials else [],
            "lifestyle_requirements": json.loads(self.lifestyle_requirements) if self.lifestyle_requirements else [],
            "special_instructions": self.special_instructions
        }

class Design(Base):
    __tablename__ = "designs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    house_id = Column(Integer, ForeignKey("house_projects.id"), nullable=True)
    title = Column(String(200), default="Interior Design Visualization")
    image_url = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="designs")
    house = relationship("HouseProject", back_populates="designs")
    recommendations = relationship("FurnitureRecommendation", back_populates="design", cascade="all, delete-orphan")
    cost_estimate = relationship("CostEstimate", back_populates="design", uselist=False, cascade="all, delete-orphan")
    chats = relationship("DesignChat", back_populates="design", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "house_id": self.house_id,
            "title": self.title,
            "image_url": self.image_url,
            "prompt": self.prompt,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class FurnitureRecommendation(Base):
    __tablename__ = "furniture_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    design_id = Column(Integer, ForeignKey("designs.id"), nullable=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), default="Seating")
    dimensions = Column(String(100), default="Standard")
    estimated_cost = Column(Float, default=0.0)
    location_hint = Column(String(200), default="Main wall")
    reason = Column(Text, default="")

    room = relationship("Room", back_populates="recommendations")
    design = relationship("Design", back_populates="recommendations")

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "design_id": self.design_id,
            "name": self.name,
            "category": self.category,
            "dimensions": self.dimensions,
            "estimated_cost": self.estimated_cost,
            "location_hint": self.location_hint,
            "reason": self.reason
        }

class CostEstimate(Base):
    __tablename__ = "cost_estimates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    house_id = Column(Integer, ForeignKey("house_projects.id"), nullable=True)
    design_id = Column(Integer, ForeignKey("designs.id"), nullable=True)
    furniture_cost = Column(Float, default=0.0)
    materials_cost = Column(Float, default=0.0)
    lighting_cost = Column(Float, default=0.0)
    paint_cost = Column(Float, default=0.0)
    decor_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="cost_estimates")
    house = relationship("HouseProject", back_populates="cost_estimate")
    design = relationship("Design", back_populates="cost_estimate")

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "house_id": self.house_id,
            "design_id": self.design_id,
            "furniture_cost": self.furniture_cost,
            "materials_cost": self.materials_cost,
            "lighting_cost": self.lighting_cost,
            "paint_cost": self.paint_cost,
            "decor_cost": self.decor_cost,
            "total_cost": self.total_cost,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class DesignChat(Base):
    __tablename__ = "design_chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    house_id = Column(Integer, ForeignKey("house_projects.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    design_id = Column(Integer, ForeignKey("designs.id"), nullable=True)
    role = Column(String(20), nullable=False) # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    house = relationship("HouseProject", back_populates="chats")
    design = relationship("Design", back_populates="chats")

    def to_dict(self):
        return {
            "id": self.id,
            "house_id": self.house_id,
            "room_id": self.room_id,
            "design_id": self.design_id,
            "role": self.role,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class AsyncJob(Base):
    __tablename__ = "async_jobs"

    id = Column(String(100), primary_key=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(50), default="QUEUED") # QUEUED, ANALYZING, GENERATING, COMPLETED, FAILED
    progress_percent = Column(Integer, default=0)
    result_data = Column(Text, default="{}")
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "progress_percent": self.progress_percent,
            "result_data": json.loads(self.result_data) if self.result_data else {},
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class DesignFeedback(Base):
    __tablename__ = "design_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    design_id = Column(Integer, ForeignKey("designs.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rating = Column(Integer, default=5)
    feedback_text = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "design_id": self.design_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "feedback_text": self.feedback_text,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class DesignOrder(Base):
    __tablename__ = "design_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    house_id = Column(Integer, ForeignKey("house_projects.id"), nullable=True)
    order_type = Column(String(100), default="Design Consultation") # Consultation, 3D Blueprint, Contractor Execution
    status = Column(String(50), default="PENDING") # PENDING, CONFIRMED, COMPLETED
    amount_inr = Column(Float, default=5000.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "house_id": self.house_id,
            "order_type": self.order_type,
            "status": self.status,
            "amount_inr": self.amount_inr,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

def init_db():
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "house_projects" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("house_projects")]
        if "user_id" not in columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE house_projects ADD COLUMN user_id INTEGER REFERENCES users(id)"))
                conn.commit()

    # Ensure default admin user exists
    admin_email = "admin@decoraai.com"
    existing_admin = db_session.query(User).filter_by(email=admin_email).first()
    if not existing_admin:
        admin_user = User(name="DecoraAI Admin", email=admin_email, is_admin=True)
        admin_user.set_password("admin123")
        db_session.add(admin_user)
        db_session.commit()
    elif not existing_admin.is_admin:
        existing_admin.is_admin = True
        db_session.commit()
