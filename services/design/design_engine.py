from typing import Dict, Any, Optional
from services.ai.orchestrator import orchestrator
from services.design.prompt_builder import prompt_builder
from services.design.room_rules import get_room_rule

class DesignEngine:
    """
    Core AI Design Engine responsible for generating room visualizations,
    synthesizing architectural explanations, and applying whole-house design language.
    """

    def generate_room_design(
        self,
        room_type: str,
        style: str = "Modern Luxury",
        house_style_profile: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        vision_analysis: Optional[Dict[str, Any]] = None,
        reference_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        rule = get_room_rule(room_type)

        # 1. Build prompt
        prompt = prompt_builder.build_room_prompt(
            room_type=room_type,
            style=style,
            house_style_profile=house_style_profile,
            user_preferences=user_preferences,
            vision_analysis=vision_analysis
        )

        # 2. Call AI image generator
        gen_result = orchestrator.generate_image(
            prompt=prompt,
            reference_image_path=reference_image_path,
            options={"room_type": room_type, "style": style}
        )

        # 3. Formulate dynamic AI architectural explanation
        palette = (house_style_profile or {}).get("main_palette", ["Warm White", "Beige"])
        palette_text = ", ".join(palette) if isinstance(palette, list) else str(palette)
        flooring = (house_style_profile or {}).get("flooring_spec", "Italian Marble")
        lighting_temp = (house_style_profile or {}).get("lighting_temp", "Warm White (3000K)")

        explanation = None
        # Try dynamic Gemini synthesis
        try:
            chat_context = {
                "room_name": rule["display_name"],
                "room_type": room_type,
                "style": style,
                "palette": palette_text,
                "flooring": flooring,
                "lighting": lighting_temp
            }
            prompt_req = [
                {"role": "user", "message": f"Write a concise 2-sentence architectural rationale for designing this {rule['display_name']} in {style} style using {palette_text} palette, {flooring} flooring, and {lighting_temp} lighting. Focus on space planning and visual balance."}
            ]
            ai_exp = orchestrator.generate_chat_response(prompt_req, chat_context)
            if ai_exp and len(ai_exp) > 20:
                explanation = ai_exp
        except Exception:
            pass

        if not explanation:
            explanation = (
                f"Designed in {style} aesthetic with a curated palette of {palette_text} and {flooring} flooring. "
                f"The spatial arrangement emphasizes {rule['primary_focus'].lower()}, aligning key pieces like {rule['key_furniture'][0]} "
                f"with {lighting_temp} ambient illumination to maximize comfort, natural light, and clear walking aisles."
            )

        return {
            "title": f"{style} {rule['display_name']}",
            "image_url": gen_result.image_url,
            "prompt": prompt,
            "explanation": explanation,
            "room_type": room_type,
            "style": style
        }

design_engine = DesignEngine()
