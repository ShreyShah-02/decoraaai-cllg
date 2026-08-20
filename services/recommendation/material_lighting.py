from typing import Dict, Any, List

class MaterialLightingEngine:
    """
    Intelligent Material & 3-Tier Lighting recommendation service
    calibrated per room type and house style profile.
    """

    def get_material_recommendations(self, room_type: str, style: str = "Modern Luxury") -> Dict[str, Any]:
        norm = (room_type or "living_room").lower().replace(" ", "_")

        base_materials = {
            "living_room": {
                "flooring": "Light Italian Botticino Marble (800x1600mm)",
                "wall_finish": "Smooth Lime-wash warm white with Fluted Walnut Wood Feature Panel",
                "hardware_finish": "Matte Black & Brushed Champagne Brass",
                "upholstery": "High-durability bouclé fabric (50,000+ Martindale cycles)",
                "curtains": "Floor-to-ceiling sheer linen with thermal blackout drape layer"
            },
            "master_bedroom": {
                "flooring": "Engineered European Oak Herringbone Hardwood",
                "wall_finish": "Acoustic fabric padded headboard paneling + subtle neutral wall paint",
                "hardware_finish": "Brushed Brass & Soft Champagne Gold",
                "upholstery": "Rich velvet & breathable woven cotton-linen blend",
                "curtains": "100% blackout velvet drapes with motorized track"
            },
            "kitchen": {
                "flooring": "Seamless Matte Vitrified Anti-Skid Tiles (1200x600mm)",
                "countertops": "20mm Polished Calacatta Quartz (heat, scratch, and stain resistant)",
                "cabinet_finish": "Anti-fingerprint Matte Acrylic (E0 grade marine core)",
                "backsplash": "Full-height continuous Quartz slab / Fluted ceramic subway tiles",
                "hardware_finish": "Concealed Gola Profile handles in Matte Black"
            },
            "bathroom": {
                "flooring": "Anti-skid Honed Porcelain Slate Tiles",
                "wall_finish": "Large format Bookmatched Statuario Marble Tiles",
                "countertops": "Seamless Composite Quartz Countertop",
                "hardware_finish": "PVD Coated Matte Black Thermostatic Diverters and Faucets"
            },
            "dining_room": {
                "flooring": "Continuous Polished Marble with contrasting border inlay",
                "wall_finish": "Mirrored fluted glass paneling to amplify perceived space",
                "table_top": "12mm Sintered Stone (Diamond hard, scratch proof)",
                "hardware_finish": "Brushed Brass Chandelier Stem and Credenza Pulls"
            }
        }

        return base_materials.get(norm, base_materials["living_room"])

    def get_lighting_recommendations(self, room_type: str, style: str = "Modern Luxury") -> Dict[str, Any]:
        norm = (room_type or "living_room").lower().replace(" ", "_")

        lighting_plans = {
            "living_room": {
                "color_temperature": "3000K Warm White",
                "ambient": "Dimmable anti-glare recessed COB LED ceiling spots (12W each)",
                "task": "Slim brass floor lamp beside reading armchair",
                "accent": "Concealed LED strip cove lighting washing the ceiling perimeter (9W/meter) + TV backlight",
                "fixture_style": "Minimalist recessed architectural housings + Modern organic brass statement chandelier"
            },
            "master_bedroom": {
                "color_temperature": "2700K - 3000K Soft Warm",
                "ambient": "Diffused indirect ceiling false ceiling perimeter illumination",
                "task": "Dual focused directional bedside reading spot lights (3W)",
                "accent": "Suspended minimalist bedside blown-glass pendants + illuminated wardrobe interior sensors",
                "fixture_style": "Flush mount matte black fixtures with brushed brass decorative trims"
            },
            "kitchen": {
                "color_temperature": "4000K Neutral Daylight (High CRI 95+ for accurate food color rendering)",
                "ambient": "Evenly distributed wide-angle ceiling downlights (15W)",
                "task": "High-output continuous under-cabinet LED profile strips illuminating countertops directly",
                "accent": "Glass cabinet interior backlighting showcasing glassware",
                "fixture_style": "IP44 moisture-resistant recessed fixtures"
            },
            "bathroom": {
                "color_temperature": "4000K Neutral Daylight at vanity / 3000K warm in shower",
                "ambient": "IP65 rated waterproof ceiling downlights",
                "task": "Vertical side-lit LED vanity mirror (eliminating facial shadows for grooming)",
                "accent": "Illuminated recessed shower wall niche for shampoo and toiletries",
                "fixture_style": "Sealed IP65 waterproof recessed housings"
            },
            "dining_room": {
                "color_temperature": "3000K Warm Dining Glow",
                "ambient": "Soft perimeter cove lighting",
                "task": "Linear multi-bulb pendant suspended 30-34 inches above table center",
                "accent": "Directional spotlighting highlighting framed artwork on dining accent wall",
                "fixture_style": "Sculptural linear brass and frosted glass chandelier"
            }
        }

        return lighting_plans.get(norm, lighting_plans["living_room"])

material_lighting_engine = MaterialLightingEngine()
