from typing import List, Dict, Any, Optional
from services.design.room_rules import normalize_room_type

FURNITURE_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "living_room": [
        {"name": "L-Shaped Modular Sectional Sofa", "category": "Seating", "dimensions": "9 ft x 6 ft", "estimated_cost": 75000, "location_hint": "Main wall facing media console", "reason": "Maximizes family seating without interrupting walking aisles."},
        {"name": "Fluted Walnut TV Unit with Slat Panel", "category": "Storage", "dimensions": "7 ft x 1.5 ft", "estimated_cost": 42000, "location_hint": "Primary focal wall", "reason": "Conceals wiring while establishing architectural symmetry."},
        {"name": "Dual Nesting Marble & Brass Coffee Tables", "category": "Tables", "dimensions": "36 in dia & 24 in dia", "estimated_cost": 22000, "location_hint": "Center of seating zone", "reason": "Provides flexible surface area and visual lightness."},
        {"name": "Curved Bouclé Lounge Accent Chair", "category": "Seating", "dimensions": "32 in x 30 in", "estimated_cost": 28000, "location_hint": "Perpendicular to sofa", "reason": "Adds soft organic geometry and conversational intimacy."}
    ],
    "master_bedroom": [
        {"name": "King Size Upholstered Bed with Hydraulic Storage", "category": "Beds", "dimensions": "6.5 ft x 6 ft", "estimated_cost": 65000, "location_hint": "Center against acoustic accent wall", "reason": "Generous under-bed storage for seasonal linens."},
        {"name": "Floating Fluted Walnut Nightstands (Pair)", "category": "Tables", "dimensions": "20 in x 16 in each", "estimated_cost": 18000, "location_hint": "Flanking both sides of bed", "reason": "Floating design keeps floor clear and easy to vacuum."},
        {"name": "Floor-to-Ceiling 4-Door Wardrobe with Tinted Glass", "category": "Storage", "dimensions": "8 ft x 7 ft x 2 ft", "estimated_cost": 95000, "location_hint": "Side wall with 36 in clearance", "reason": "Maximizes vertical storage capacity with integrated internal LED illumination."},
        {"name": "Vanity Dressing Console with Backlit LED Mirror", "category": "Vanity", "dimensions": "4 ft x 1.5 ft", "estimated_cost": 32000, "location_hint": "Near natural window light", "reason": "Dedicated grooming zone with anti-glare task lighting."}
    ],
    "bedroom": [
        {"name": "Queen Size Platform Bed with Storage", "category": "Beds", "dimensions": "6 ft x 5 ft", "estimated_cost": 45000, "location_hint": "Primary wall", "reason": "Proportioned for standard bedroom square footage."},
        {"name": "3-Door Sliding Wardrobe with Mirror Panel", "category": "Storage", "dimensions": "6 ft x 7 ft x 2 ft", "estimated_cost": 55000, "location_hint": "Adjacent wall", "reason": "Sliding doors eliminate door swing clearance issues in compact rooms."},
        {"name": "Minimalist Wall-Mounted Study Desk", "category": "Workspaces", "dimensions": "3.5 ft x 1.5 ft", "estimated_cost": 14000, "location_hint": "Corner near window", "reason": "Compact workspace with integrated cord management."}
    ],
    "kitchen": [
        {"name": "Modular Base & Overhead Cabinets (Soft Close)", "category": "Cabinetry", "dimensions": "Custom fitted L-Shape", "estimated_cost": 140000, "location_hint": "Perimeter walls", "reason": "Full ergonomic utilization with tandem pull-out drawers and corner carousels."},
        {"name": "Quartz Anti-Stain Countertop (20mm)", "category": "Countertops", "dimensions": "45 sq ft", "estimated_cost": 45000, "location_hint": "Prep, sink, and cooking zones", "reason": "Non-porous, heat resistant, and easy to sanitize."},
        {"name": "Tall Pantry Unit with Internal Baskets", "category": "Storage", "dimensions": "2 ft x 7 ft x 2 ft", "estimated_cost": 38000, "location_hint": "Adjacent to refrigerator", "reason": "Consolidates dry grocery storage in high-density pull-out wire baskets."}
    ],
    "dining_room": [
        {"name": "6-Seater Sintered Stone Dining Table", "category": "Tables", "dimensions": "6 ft x 3 ft", "estimated_cost": 52000, "location_hint": "Center under linear chandelier", "reason": "Scratch-proof, thermal-resistant surface for formal and everyday dining."},
        {"name": "Upholstered Dining Chairs (Set of 6)", "category": "Seating", "dimensions": "Standard Ergonomic", "estimated_cost": 36000, "location_hint": "Around dining table", "reason": "High-density foam with stain-resistant fabric for long dining sessions."},
        {"name": "Buffet Sideboard Console with Fluted Glass", "category": "Storage", "dimensions": "5 ft x 1.5 ft", "estimated_cost": 34000, "location_hint": "Dining perimeter wall", "reason": "Crockery storage and surface for buffet serving."}
    ],
    "bathroom": [
        {"name": "Floating Quartz Vanity with Under-Mount Sink", "category": "Vanity", "dimensions": "3 ft x 1.8 ft", "estimated_cost": 28000, "location_hint": "Dry zone wall", "reason": "Modern aesthetics with concealed moisture-resistant storage drawers."},
        {"name": "Toughened Glass Shower Partition (10mm)", "category": "Partition", "dimensions": "3 ft x 6.5 ft", "estimated_cost": 18000, "location_hint": "Between shower and dry area", "reason": "Prevents water splashing and maintains bathroom hygiene."},
        {"name": "Anti-Fog Smart LED Mirror", "category": "Fixtures", "dimensions": "30 in dia", "estimated_cost": 11000, "location_hint": "Above vanity basin", "reason": "Shadow-free 4000K illumination with defogging technology."}
    ],
    "pooja_room": [
        {"name": "Carved Teakwood Mandir Unit with Brass Inlay", "category": "Sanctuary", "dimensions": "4 ft x 6 ft x 2 ft", "estimated_cost": 48000, "location_hint": "East / North-East wall", "reason": "Traditional craftsmanship with designated drawers for puja essentials."},
        {"name": "Polished White Marble Pedestal Platform", "category": "Platform", "dimensions": "4 ft x 1.5 ft", "estimated_cost": 22000, "location_hint": "Base of mandir", "reason": "Vastu compliant and easy to clean during ritual offerings."}
    ],
    "balcony": [
        {"name": "All-Weather Synthetic Wicker Chairs & Bistro Table", "category": "Outdoor Seating", "dimensions": "2 Chairs + 24 in table", "estimated_cost": 22000, "location_hint": "Corner seating nook", "reason": "UV and moisture resistant outdoor lounging."},
        {"name": "Modular Vertical Planter Trellis with Drip Tray", "category": "Greenery", "dimensions": "4 ft x 6 ft", "estimated_cost": 14000, "location_hint": "Side privacy wall", "reason": "Brings lush natural air-purifying foliage into urban spaces."}
    ],
    "kids_bedroom": [
        {"name": "Single Bunk / Storage Bed with Rounded Guardrails", "category": "Beds", "dimensions": "6.5 ft x 3.5 ft", "estimated_cost": 42000, "location_hint": "Against play feature wall", "reason": "Child-safe rounded ergonomics with integrated under-bed toy drawers."},
        {"name": "Ergonomic Child Study Desk with Height Adjustment", "category": "Workspaces", "dimensions": "4 ft x 2 ft", "estimated_cost": 24000, "location_hint": "Natural light window zone", "reason": "Posture-supporting design that grows with the child."},
        {"name": "Low-Height Montessori Bookcase & Toy Organizer", "category": "Storage", "dimensions": "4 ft x 3.5 ft x 1.2 ft", "estimated_cost": 18000, "location_hint": "Accessible wall zone", "reason": "Empowers independent child access with safe soft-close bins."},
        {"name": "Anti-Allergenic Soft Foam Play Area Rug", "category": "Decor", "dimensions": "5 ft x 5 ft", "estimated_cost": 9000, "location_hint": "Center activity zone", "reason": "Cushioned floor protection for play and reading activities."}
    ],
    "guest_bedroom": [
        {"name": "Queen Size Comfort Bed with Clean Silhouette", "category": "Beds", "dimensions": "6 ft x 5 ft", "estimated_cost": 48000, "location_hint": "Primary focal wall", "reason": "Universal hospitality comfort with hotel-grade mattress."},
        {"name": "Upholstered Luggage Bench with Bottom Shelf", "category": "Seating", "dimensions": "3.5 ft x 1.5 ft", "estimated_cost": 12000, "location_hint": "Foot of the bed", "reason": "Provides convenient luggage resting spot for visiting guests."},
        {"name": "2-Door Wardrobe with Full-Length Dressing Mirror", "category": "Storage", "dimensions": "4 ft x 7 ft x 2 ft", "estimated_cost": 38000, "location_hint": "Side alcove wall", "reason": "Generous hanging space and private guest grooming."}
    ],
    "study_room": [
        {"name": "Solid Wood Deep Study Desk with Cord Concealment", "category": "Workspaces", "dimensions": "5 ft x 2.5 ft", "estimated_cost": 32000, "location_hint": "Perpendicular to window", "reason": "Spacious reading and laptop workstation without screen glare."},
        {"name": "High-Back Ergonomic Lumbar Mesh Chair", "category": "Seating", "dimensions": "Adjustable Height", "estimated_cost": 22000, "location_hint": "At study desk", "reason": "Prevents fatigue during extended study and research sessions."},
        {"name": "Ceiling-Height Bookshelf with Lower Lockable Storage", "category": "Storage", "dimensions": "5 ft x 7.5 ft x 1.2 ft", "estimated_cost": 42000, "location_hint": "Primary library wall", "reason": "Organizes extensive book collections and reference archives."}
    ],
    "home_office": [
        {"name": "Executive Ergonomic Desk with Wire Management", "category": "Workspaces", "dimensions": "5 ft x 2.5 ft", "estimated_cost": 36000, "location_hint": "Center / facing entrance", "reason": "Spacious dual-monitor layout with integrated charging ports."},
        {"name": "High-Back Breathable Mesh Ergonomic Chair", "category": "Seating", "dimensions": "Adjustable Lumbar", "estimated_cost": 24000, "location_hint": "At executive desk", "reason": "Dynamic spinal support for 8+ hour work sessions."},
        {"name": "Full-Height Bookshelf & Display Cabinet", "category": "Storage", "dimensions": "5 ft x 7 ft x 1.2 ft", "estimated_cost": 38000, "location_hint": "Backdrop wall behind desk", "reason": "Aesthetic video conference backdrop and document archive."}
    ]
}

STYLE_MODIFIERS = {
    "japandi": {
        "prefix": "Japandi Low-Profile ",
        "material_hint": "in Natural Light Oak & Textured Linen",
        "reason_extra": "Emphasizes wabi-sabi minimalism and organic earthiness.",
        "cost_multiplier": 0.95
    },
    "minimalist": {
        "prefix": "Monochromatic Minimalist ",
        "material_hint": "with Concealed Handles & Matte Finish",
        "reason_extra": "Eliminates visual clutter and maximizes open floor area.",
        "cost_multiplier": 0.85
    },
    "modern luxury": {
        "prefix": "Luxury Designer ",
        "material_hint": "in Fluted Walnut, Bouclé & Brushed Brass",
        "reason_extra": "Infuses opulent textures and bespoke high-end elegance.",
        "cost_multiplier": 1.3
    },
    "scandinavian": {
        "prefix": "Nordic Scandinavian ",
        "material_hint": "in Blonde Ash & Soft Wool Blend",
        "reason_extra": "Enhances hygge comfort and captures natural ambient daylight.",
        "cost_multiplier": 0.9
    },
    "industrial": {
        "prefix": "Urban Industrial ",
        "material_hint": "with Matte Black Steel & Reclaimed Wood",
        "reason_extra": "Creates a bold, loft-inspired raw architectural presence.",
        "cost_multiplier": 1.05
    },
    "traditional": {
        "prefix": "Classic Heritage ",
        "material_hint": "in Polished Sheesham Wood & Antique Brass",
        "reason_extra": "Brings timeless royal craftsmanship and cultural warmth.",
        "cost_multiplier": 1.15
    },
    "indian contemporary": {
        "prefix": "Indo-Modern Crafted ",
        "material_hint": "with Handwoven Cane & Brass Accents",
        "reason_extra": "Blends artisanal Indian heritage with modern ergonomic sensibilities.",
        "cost_multiplier": 1.1
    }
}

class FurnitureRecommendationEngine:
    """
    Intelligent furniture recommendation service matching room dimensions,
    room type, and style preferences dynamically.
    """

    def get_recommendations(self, room_type: str, style: str = "Modern Luxury") -> List[Dict[str, Any]]:
        norm = normalize_room_type(room_type)
        items = FURNITURE_CATALOG.get(norm, FURNITURE_CATALOG["living_room"])
        style_key = (style or "Modern Luxury").lower()
        modifier = STYLE_MODIFIERS.get(style_key, None)

        # Format and dynamically adapt response
        result = []
        for item in items:
            name = item["name"]
            reason = item["reason"]
            cost = float(item["estimated_cost"])

            if modifier:
                name = f"{item['name']} ({modifier['material_hint']})"
                reason = f"{item['reason']} {modifier['reason_extra']}"
                cost = round(cost * modifier["cost_multiplier"], -2)

            result.append({
                "name": name,
                "category": item["category"],
                "dimensions": item["dimensions"],
                "estimated_cost": cost,
                "location_hint": item["location_hint"],
                "reason": reason
            })
        return result

furniture_engine = FurnitureRecommendationEngine()
