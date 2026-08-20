import os
import io
import json
import unittest
from PIL import Image
import app as flask_app
from models import db_session, HouseProject, Room, Design
from services.design.room_rules import get_room_rule, ROOM_RULES
from services.vision.image_analyzer import image_analyzer
from services.vision.floorplan_analyzer import floorplan_analyzer
from services.cost.estimator import cost_estimator

class TestAIInteriorDesignEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        flask_app.app.config['TESTING'] = True
        cls.client = flask_app.app.test_client()

        # Create a test dummy image
        cls.test_img_path = "uploads/test_room.jpg"
        img = Image.new("RGB", (300, 300), color=(240, 230, 210))
        img.save(cls.test_img_path)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "house_id") and cls.house_id:
            try:
                house = db_session.query(HouseProject).filter_by(id=cls.house_id).first()
                if house:
                    db_session.delete(house)
                    db_session.commit()
            except Exception:
                pass

        if os.path.exists(cls.test_img_path):
            try:
                os.remove(cls.test_img_path)
            except Exception:
                pass

    def test_01_room_rules_coverage(self):
        """Verify all 18+ room types exist and have valid structure."""
        self.assertGreaterEqual(len(ROOM_RULES), 18)
        for room_type in ["living_room", "master_bedroom", "kitchen", "pooja_room", "balcony", "home_office"]:
            rule = get_room_rule(room_type)
            self.assertIn("display_name", rule)
            self.assertIn("key_furniture", rule)
            self.assertIn("lighting_plan", rule)

    def test_02_computer_vision_analysis(self):
        """Test computer vision analysis on uploaded room image."""
        res = image_analyzer.analyze_room([self.test_img_path], {"room_type": "living_room"})
        self.assertIsNotNone(res)
        self.assertIn(res.room_type, ["living_room"])
        self.assertIsInstance(res.dominant_colors, list)
        self.assertGreater(len(res.dominant_colors), 0)

    def test_03_cost_estimation(self):
        """Test streamlined cost calculation for rooms and whole house."""
        room_cost = cost_estimator.estimate_room_cost("living_room", 200.0, "Modern Luxury")
        self.assertGreater(room_cost["total_cost"], 0)
        self.assertGreater(room_cost["furniture_cost"], 0)
        self.assertGreater(room_cost["materials_cost"], 0)

        house_cost = cost_estimator.estimate_house_cost([
            {"id": 1, "name": "Living Room", "room_type": "living_room", "dimensions": {"area_sqft": 200}},
            {"id": 2, "name": "Kitchen", "room_type": "kitchen", "dimensions": {"area_sqft": 150}}
        ])
        self.assertGreater(house_cost["total_cost"], room_cost["total_cost"])
        self.assertEqual(len(house_cost["rooms"]), 2)

    def test_04_create_house_project_api(self):
        """Test POST /api/house/create."""
        payload = {
            "name": "Luxury Sunset Villa",
            "total_budget": 2000000.0,
            "approx_area_sqft": 2200.0,
            "floors": 2,
            "primary_style": "Modern Luxury",
            "lifestyle_requirements": ["Family with Kids", "Work From Home"]
        }
        res = self.client.post("/api/house/create", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("house", data)
        self.assertEqual(data["house"]["name"], "Luxury Sunset Villa")
        self.assertGreater(len(data["house"]["rooms"]), 0)

        # Save house ID for subsequent tests
        self.__class__.house_id = data["house"]["id"]

    def test_05_list_and_get_house_api(self):
        """Test GET /api/houses and GET /api/house/<id>."""
        res = self.client.get("/api/houses")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(len(data["houses"]), 1)

        res_single = self.client.get(f"/api/house/{self.house_id}")
        self.assertEqual(res_single.status_code, 200)
        house_data = res_single.get_json()["house"]
        self.assertEqual(house_data["id"], self.house_id)
        self.__class__.room_id = house_data["rooms"][0]["id"]

    def test_06_room_upload_and_analyze_api(self):
        """Test POST /api/room/<id>/upload and POST /api/room/<id>/analyze."""
        # Upload
        with open(self.test_img_path, "rb") as f:
            data = {
                'image': (io.BytesIO(f.read()), 'test_room.jpg'),
                'is_floor_plan': 'false',
                'angle_description': 'front_angle'
            }
            res_upload = self.client.post(
                f"/api/room/{self.room_id}/upload",
                data=data,
                content_type='multipart/form-data'
            )
            self.assertEqual(res_upload.status_code, 201)

        # Analyze
        res_analyze = self.client.post(f"/api/room/{self.room_id}/analyze")
        self.assertEqual(res_analyze.status_code, 200)
        ana_data = res_analyze.get_json()
        self.assertEqual(ana_data["status"], "success")
        self.assertIn("analysis", ana_data)
        self.assertIn("dominant_colors", ana_data["analysis"])

    def test_07_room_generate_design_api(self):
        """Test POST /api/room/<id>/generate."""
        res = self.client.post(f"/api/room/{self.room_id}/generate", json={"style": "Modern Luxury"})
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("design", data)
        self.assertIn("image_url", data["design"])
        self.assertIn("furniture_recommendations", data)
        self.assertIn("materials", data)
        self.assertIn("lighting", data)
        self.assertIn("cost_estimate", data)

        self.__class__.design_id = data["design"]["id"]

    def test_08_design_chat_api(self):
        """Test contextual chatbot POST /api/design/<id>/chat."""
        res = self.client.post(
            f"/api/design/{self.design_id}/chat",
            json={"message": "Can we make the sofa L-shaped and add warm lighting?"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("reply", data)
        self.assertGreater(len(data["reply"]), 0)

    def test_09_whole_house_generate_api(self):
        """Test POST /api/house/<id>/generate."""
        res = self.client.post(f"/api/house/{self.house_id}/generate")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("designs", data)
        self.assertGreater(len(data["designs"]), 0)

    def test_10_house_cost_estimate_api(self):
        """Test GET /api/house/<id>/cost."""
        res = self.client.get(f"/api/house/{self.house_id}/cost")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("estimated_cost", data)
        self.assertGreater(data["estimated_cost"]["total_cost"], 0)

    def test_11_quick_generate_endpoint(self):
        """Test POST /generate homepage endpoint."""
        res = self.client.post("/generate", json={"prompt": "Scandinavian Kitchen with white oak cabinets"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("image", data)

    def test_12_auth_and_admin_db_security(self):
        """Test Auth and Admin-Only DB security."""
        # 1. Unauthenticated request to admin DB API returns 401
        res_guest = self.client.get("/api/admin/db/tables")
        self.assertEqual(res_guest.status_code, 401)

        # 2. Login as admin
        res_login = self.client.post("/api/auth/login", json={
            "email": "admin@decoraai.com",
            "password": "admin123"
        })
        self.assertEqual(res_login.status_code, 200)
        login_data = res_login.get_json()
        self.assertTrue(login_data["user"]["is_admin"])

        # 3. Authenticated admin request to DB tables returns 200
        res_admin = self.client.get("/api/admin/db/tables")
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn("tables", res_admin.get_json())

        # 4. Create a dummy user and test admin delete user endpoint
        res_signup = self.client.post("/api/auth/signup", json={
            "name": "Temporary Test User",
            "email": "temptest@decoraai.com",
            "password": "Password123!"
        })
        self.assertEqual(res_signup.status_code, 201)
        temp_user_id = res_signup.get_json()["user"]["id"]

        # Re-login as admin
        self.client.post("/api/auth/login", json={
            "email": "admin@decoraai.com",
            "password": "admin123"
        })

        # Delete the temp user via Admin DB API
        res_del = self.client.delete(f"/api/admin/db/user/{temp_user_id}")
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(res_del.get_json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
