from typing import Dict, Any, List, Optional
from services.recommendation.furniture_engine import furniture_engine

class CostEstimator:
    """
    Streamlined Cost Estimation Engine calculating room-level and house-level
    cost estimates based on furniture, materials, lighting, and finishes.
    """

    def estimate_room_cost(self, room_type: str, room_area_sqft: float = 180.0, style: str = "Modern Luxury") -> Dict[str, float]:
        # 1. Base furniture cost from recommendations
        items = furniture_engine.get_recommendations(room_type, style)
        furniture_total = sum(item["estimated_cost"] for item in items)

        # 2. Material & flooring cost based on sqft
        material_rate_per_sqft = 350.0 if "luxury" in style.lower() else 220.0
        materials_cost = round(room_area_sqft * material_rate_per_sqft, 2)

        # 3. Lighting cost
        lighting_cost = 35000.0 if "living" in room_type.lower() or "master" in room_type.lower() else 20000.0

        # 4. Paint / wall finish cost
        paint_cost = round(room_area_sqft * 75.0, 2)

        # 5. Decor & styling accessories
        decor_cost = 25000.0 if "living" in room_type.lower() else 15000.0

        total = furniture_total + materials_cost + lighting_cost + paint_cost + decor_cost

        return {
            "furniture_cost": float(furniture_total),
            "materials_cost": float(materials_cost),
            "lighting_cost": float(lighting_cost),
            "paint_cost": float(paint_cost),
            "decor_cost": float(decor_cost),
            "total_cost": float(total)
        }

    def estimate_house_cost(self, rooms: List[Dict[str, Any]], style: str = "Modern Luxury") -> Dict[str, Any]:
        total_furniture = 0.0
        total_materials = 0.0
        total_lighting = 0.0
        total_paint = 0.0
        total_decor = 0.0
        total_house = 0.0
        room_breakdowns = []

        for r in rooms:
            r_type = r.get("room_type", "living_room")
            area = float(r.get("dimensions", {}).get("area_sqft", 180.0) if isinstance(r.get("dimensions"), dict) else 180.0)
            cost = self.estimate_room_cost(r_type, area, style)

            total_furniture += cost["furniture_cost"]
            total_materials += cost["materials_cost"]
            total_lighting += cost["lighting_cost"]
            total_paint += cost["paint_cost"]
            total_decor += cost["decor_cost"]
            total_house += cost["total_cost"]

            room_breakdowns.append({
                "room_id": r.get("id"),
                "room_name": r.get("name", r_type),
                "room_type": r_type,
                "cost": cost
            })

        return {
            "furniture_cost": total_furniture,
            "materials_cost": total_materials,
            "lighting_cost": total_lighting,
            "paint_cost": total_paint,
            "decor_cost": total_decor,
            "total_cost": total_house,
            "rooms": room_breakdowns
        }

cost_estimator = CostEstimator()
