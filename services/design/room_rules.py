from typing import Dict, Any, List

ROOM_RULES: Dict[str, Dict[str, Any]] = {
    "living_room": {
        "display_name": "Living Room",
        "primary_focus": "Conversation circle, TV feature wall, and natural light intake",
        "key_furniture": ["L-shaped Sectional Sofa", "Marble/Wood Coffee Table", "Fluted Wood TV Media Console", "Lounge Accent Chair", "Geometric Area Rug"],
        "recommended_materials": ["Engineered Walnut Wood", "Italian Marble", "Bouclé / Velvet Upholstery", "Matte Black Metal Accents"],
        "lighting_plan": "Recessed ceiling LED spots (3000K) + Indirect cove strip + Brass floor reading lamp",
        "layout_strategy": "Maintain 36-inch clearance around main seating zone; anchor seating with large rug."
    },
    "master_bedroom": {
        "display_name": "Master Bedroom",
        "primary_focus": "Serenity, acoustic softness, and luxury headboard accent wall",
        "key_furniture": ["King Size Storage Bed with Padded Headboard", "Dual Nightstands", "Full-Height Wardrobe with Fluted Glass", "Dressing Vanity Mirror", "Accent Armchair"],
        "recommended_materials": ["Warm Oak Wood", "Textured Linen Wall Covering", "Brushed Brass Trims", "High-Pile Rug"],
        "lighting_plan": "Warm 2700K ambient ceiling lighting + Dual bedside pendant/sconce reading lights",
        "layout_strategy": "Position bed on primary wall facing away from direct doorway view; provide ample wardrobe swing clearance."
    },
    "bedroom": {
        "display_name": "Bedroom",
        "primary_focus": "Comfort, space efficiency, and organized wardrobe storage",
        "key_furniture": ["Queen Bed with Hydraulic Lift Storage", "Compact Bedside Tables", "3-Door Sliding Wardrobe", "Wall-Mounted Study Ledge"],
        "recommended_materials": ["Natural Teak Finish", "Soft Beige Paint", "Matte Black Handles"],
        "lighting_plan": "Warm 3000K recessed spots + Bedside wall sconces",
        "layout_strategy": "Optimize floor area with sliding wardrobe doors and wall-mounted shelves."
    },
    "kids_bedroom": {
        "display_name": "Kids Bedroom",
        "primary_focus": "Playfulness, safety, study productivity, and expandable storage",
        "key_furniture": ["Single / Bunk Bed with Safety Rails", "Ergonomic Study Desk & Chair", "Low-Height Book & Toy Storage", "Magnetic/Chalkboard Feature Wall"],
        "recommended_materials": ["Non-toxic Matte Laminates", "Birch Plywood", "Washable Performance Fabric", "Soft Foam Play Mat"],
        "lighting_plan": "Bright 4000K study task lighting + Warm dimmable night lamp",
        "layout_strategy": "Ensure rounded furniture corners, maximize open floor space for play."
    },
    "guest_bedroom": {
        "display_name": "Guest Bedroom",
        "primary_focus": "Welcoming comfort, minimalist elegance, and universal usability",
        "key_furniture": ["Queen Bed", "Luggage Bench / Stool", "Wardrobe with Hanging Space", "Bedside Table with USB Charging"],
        "recommended_materials": ["Neutral Linen", "Warm Walnut Wood", "Neutral Wall Art"],
        "lighting_plan": "Soft ambient ceiling light + Bedside table lamps",
        "layout_strategy": "Keep surfaces uncluttered and intuitive for visiting guests."
    },
    "kitchen": {
        "display_name": "Kitchen",
        "primary_focus": "Ergonomic Golden Work Triangle (Sink - Hob - Refrigerator)",
        "key_furniture": ["Modular Kitchen Cabinets (L/U-Shape/Parallel)", "Quartz/Granite Countertop", "Glass Backsplash", "Pull-Out Pantry Tower", "Built-in Chimney & Hob"],
        "recommended_materials": ["Anti-Fingerprint Acrylic / PU Finish", "Stain-Resistant Quartz", "Seamless Vitrified Floor Tiles"],
        "lighting_plan": "High CRI 4000K under-cabinet task LED strips + Recessed ceiling ambient lights",
        "layout_strategy": "Maintain 48-inch aisle between parallel counters; place sink near natural window ventilation."
    },
    "dining_room": {
        "display_name": "Dining Room",
        "primary_focus": "Gathering focal point and seamless connection to kitchen and living areas",
        "key_furniture": ["6-Seater Sintered Stone / Wood Dining Table", "Upholstered Dining Chairs", "Crockery Storage Console", "Linear Chandelier"],
        "recommended_materials": ["Sintered Stone Top", "Solid Oak Legs", "Fluted Glass Cabinetry", "Brushed Gold Accents"],
        "lighting_plan": "Statement linear pendant suspended 32 inches above table top (3000K warm)",
        "layout_strategy": "Allow 36 inches between chair backs and walls/buffet for smooth guest movement."
    },
    "bathroom": {
        "display_name": "Bathroom",
        "primary_focus": "Wet and dry zoning, luxury spa ambiance, and moisture resistance",
        "key_furniture": ["Floating Vanity with Quartz Top", "LED Backlit Anti-Fog Mirror", "Glass Shower Partition", "Concealed Wall-Hung WC", "Towel Rack & Niche Storage"],
        "recommended_materials": ["Large-Format Porcelain Tiles (Anti-skid)", "Quartz Countertop", "Matte Black / Chrome Diverters"],
        "lighting_plan": "4000K vertical vanity mirror lighting (no shadows) + 3000K ceiling shower spot",
        "layout_strategy": "Strict wet-dry separation with a toughened glass cubicle and recessed shower niche."
    },
    "study_room": {
        "display_name": "Study Room",
        "primary_focus": "Focus, acoustic quietness, and ergonomic comfort",
        "key_furniture": ["Deep Study Desk", "High-Back Ergonomic Mesh Chair", "Ceiling-Height Bookshelf", "Pin-up Board / Marker Board"],
        "recommended_materials": ["Warm Oak Wood", "Matte Anti-Glare Surfaces", "Acoustic Wall Panels"],
        "lighting_plan": "Adjustable 4000K desk task lamp + Diffused ambient ceiling fixtures",
        "layout_strategy": "Place desk perpendicular to window to avoid screen glare while capturing daylight."
    },
    "home_office": {
        "display_name": "Home Office",
        "primary_focus": "Professional video-call backdrop, high productivity, and wire concealment",
        "key_furniture": ["Executive Desk with Integrated Cable Tray", "Ergonomic Chair", "Bookshelf with Trophy/Artifact Display", "Sleek Credenza"],
        "recommended_materials": ["Walnut Veneer", "Leather Upholstery", "Acoustic Slatted Wood Wall"],
        "lighting_plan": "Frontal 4000K video-lighting profile + Warm background accent backlight",
        "layout_strategy": "Ensure neat, aesthetically composed backdrop wall behind executive chair."
    },
    "balcony": {
        "display_name": "Balcony",
        "primary_focus": "Outdoor relaxation, fresh air, and greenery integration",
        "key_furniture": ["Weatherproof Rattan Chairs", "Compact Coffee Table", "Vertical Planter Wall", "Outdoor Wooden Deck Tiles"],
        "recommended_materials": ["Composite Teak Decking", "Rust-Proof Powder-Coated Aluminum", "Natural Greenery"],
        "lighting_plan": "Warm 2700K IP65 waterproof fairy / wall sconce lights",
        "layout_strategy": "Preserve unobstructed panoramic view; leave walking passage to railing."
    },
    "pooja_room": {
        "display_name": "Pooja Room",
        "primary_focus": "Divine tranquility, Vastu compliance, and sacred brass accents",
        "key_furniture": ["Carved Teakwood / Marble Mandir Platform", "Storage Drawers for Puja Samagri", "Brass Diya & Bell Stand", "Low Seating Asanas / Chowki"],
        "recommended_materials": ["Pristine White Makrana Marble", "Solid Teak Wood", "Etched Brass Bells and Inlays"],
        "lighting_plan": "Warm golden 2700K ambient illumination + Backlit Om / Gayatri mantra jaali",
        "layout_strategy": "East or North-East orientation; maintain clean symmetry and peaceful minimalism."
    },
    "utility_room": {
        "display_name": "Utility / Laundry Room",
        "primary_focus": "Efficiency, water drainage, and appliance organization",
        "key_furniture": ["Stacked Washing Machine & Dryer Cabinet", "Ironing Board Pull-Out", "Detergent & Broom Storage Cabinet", "Deep Stainless Steel Sink"],
        "recommended_materials": ["Waterproof PVC / BWP Marine Ply", "Granite Ledge", "Ceramic Wall Tiles"],
        "lighting_plan": "Bright 4000K ceiling task light",
        "layout_strategy": "Optimize vertical stacking to preserve floor space for laundry baskets."
    },
    "store_room": {
        "display_name": "Store Room",
        "primary_focus": "Maximum volume storage and systematic categorization",
        "key_furniture": ["Heavy-Duty Adjustable Steel/Wood Racks", "Overhead Loft Storage Cabinets", "Step Stool"],
        "recommended_materials": ["Durable Melamine Faced Chipboard", "Powder-Coated Steel Frame"],
        "lighting_plan": "High lumen 4000K sensor-activated ceiling light",
        "layout_strategy": "Floor-to-ceiling perimeter shelving with central aisle."
    },
    "entrance_foyer": {
        "display_name": "Entrance / Foyer",
        "primary_focus": "Grand first impression, privacy screening, and everyday convenience",
        "key_furniture": ["Shoe Console with Seating Bench", "Round Accent Mirror", "Fluted Partition Screen", "Key / Mail Drop Tray"],
        "recommended_materials": ["Italian Marble Inlay", "Walnut Veneer Console", "Warm Brass Mirror Frame"],
        "lighting_plan": "Warm 3000K welcoming chandelier or statement pendant + Cove wash",
        "layout_strategy": "Provide clear transition from exterior to main living area with shoe storage."
    },
    "hallway": {
        "display_name": "Hallway / Corridor",
        "primary_focus": "Smooth circulation and art gallery presentation",
        "key_furniture": ["Narrow Floating Console", "Framed Architectural Art Pieces", "Long Runner Rug"],
        "recommended_materials": ["Light Vitrified Tile / Wood Runner", "Warm Neutral Wall Paint"],
        "lighting_plan": "Recessed directional spotlighting focused on wall artwork",
        "layout_strategy": "Keep floor path completely clear; standard minimum 40-inch width."
    },
    "terrace": {
        "display_name": "Terrace",
        "primary_focus": "Outdoor entertaining, rooftop dining, and evening stargazing",
        "key_furniture": ["Weather-Resistant Gazebo / Pergola", "Outdoor Dining Set", "Lounge Sofa with Waterproof Cushions", "Bar Counter with Stools"],
        "recommended_materials": ["Anti-skid Terracotta / Porcelain Tiles", "Weathered Teak", "Powder-Coated Steel"],
        "lighting_plan": "Festoon string lights + Solar bollard garden lights",
        "layout_strategy": "Zone into dining, lounge, and open-sky stargazing corners."
    },
    "garage": {
        "display_name": "Garage",
        "primary_focus": "Vehicle protection, tool storage, and easy maintenance",
        "key_furniture": ["Modular Wall Tool Organizers", "Heavy Duty Overhead Storage Racks", "Epoxy Flooring"],
        "recommended_materials": ["Industrial Epoxy Floor Coating", "Galvanized Steel Shelving"],
        "lighting_plan": "High-intensity 5000K daylight LED batten tubes",
        "layout_strategy": "Keep car clearance of at least 3 feet on all sides from storage units."
    }
}

def normalize_room_type(room_type_or_name: str) -> str:
    raw = (room_type_or_name or "living_room").lower().strip()
    norm = raw.replace(" ", "_").replace("-", "_")

    if norm in ROOM_RULES:
        return norm

    # Smart keyword inference
    if any(k in raw for k in ["child", "kid", "baby", "nursery", "toddler"]):
        return "kids_bedroom"
    if "master" in raw:
        return "master_bedroom"
    if "guest" in raw:
        return "guest_bedroom"
    if any(k in raw for k in ["bed", "sleep"]):
        return "bedroom"
    if any(k in raw for k in ["kitchen", "pantry", "cook"]):
        return "kitchen"
    if any(k in raw for k in ["dining", "eat"]):
        return "dining_room"
    if any(k in raw for k in ["bath", "toilet", "washroom", "powder", "restroom", "lavatory"]):
        return "bathroom"
    if any(k in raw for k in ["pooja", "puja", "mandir", "temple", "prayer"]):
        return "pooja_room"
    if any(k in raw for k in ["office", "workstation"]):
        return "home_office"
    if any(k in raw for k in ["study", "library", "reading"]):
        return "study_room"
    if any(k in raw for k in ["balcony", "deck", "verandah"]):
        return "balcony"
    if any(k in raw for k in ["terrace", "roof"]):
        return "terrace"
    if any(k in raw for k in ["garage", "parking"]):
        return "garage"
    if any(k in raw for k in ["utility", "laundry"]):
        return "utility_room"
    if any(k in raw for k in ["store", "storage"]):
        return "store_room"
    if any(k in raw for k in ["foyer", "entry", "entrance", "lobby"]):
        return "entrance_foyer"
    if any(k in raw for k in ["hallway", "corridor", "passage"]):
        return "hallway"
    if any(k in raw for k in ["living", "hall", "drawing", "lounge", "tv room"]):
        return "living_room"

    return "living_room"

def get_room_rule(room_type: str) -> Dict[str, Any]:
    norm = normalize_room_type(room_type)
    return ROOM_RULES.get(norm, ROOM_RULES["living_room"])
