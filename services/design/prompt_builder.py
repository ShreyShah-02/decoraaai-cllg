from typing import Dict, Any, Optional
from services.design.room_rules import get_room_rule

class PromptBuilder:
    """
    Constructs high-fidelity interior design visual prompts preserving
    original room structural boundaries while applying targeted style DNA.
    """

    def build_room_prompt(
        self,
        room_type: str,
        style: str = "Modern Luxury",
        house_style_profile: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        vision_analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        rule = get_room_rule(room_type)
        h_profile = house_style_profile or {}
        u_prefs = user_preferences or {}
        v_analysis = vision_analysis or {}

        # 1. Base style & room
        prompt_parts = [
            f"Award-winning architectural interior design photograph of a {rule['display_name']}",
            f"Interior style: {style}"
        ]

        # 2. House style profile cohesion
        if h_profile.get("main_palette"):
            palette_str = ", ".join(h_profile["main_palette"])
            prompt_parts.append(f"Color palette: {palette_str}")
        if h_profile.get("accent_materials"):
            mat_str = ", ".join(h_profile["accent_materials"])
            prompt_parts.append(f"Materials: {mat_str}")
        if h_profile.get("metal_finish"):
            prompt_parts.append(f"Hardware & fixtures: {h_profile['metal_finish']}")
        if h_profile.get("flooring_spec"):
            prompt_parts.append(f"Flooring: {h_profile['flooring_spec']}")

        # 3. Key furniture & room configuration
        furniture_str = ", ".join(rule["key_furniture"][:4])
        prompt_parts.append(f"Key furniture elements: {furniture_str}")
        prompt_parts.append(f"Lighting design: {rule['lighting_plan']}")

        # 4. User preferences override
        if u_prefs.get("primary_color"):
            prompt_parts.append(f"Primary accent tone: {u_prefs['primary_color']}")
        if u_prefs.get("special_instructions"):
            prompt_parts.append(f"Custom user requirement: {u_prefs['special_instructions']}")

        # 5. Preservation & realism directives
        prompt_parts.append(
            "Preserving exact architectural structural boundaries, window placement, ceiling height, and door openings. "
            "Photorealistic 8k, Architectural Digest featured, perfectly balanced ray-traced interior illumination, ultra-detailed textures."
        )

        return ". ".join(prompt_parts)

prompt_builder = PromptBuilder()
