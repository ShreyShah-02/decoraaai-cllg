import os
import json
import base64
import mimetypes
import requests
from typing import List, Dict, Any, Optional
from services.ai.provider_base import VisionAnalysisResult, GeneratedDesignResult, BaseVisionProvider, BaseChatProvider, BaseImageProvider
from services.ai.local_cv_fallback import LocalCVFallback

class GeminiProvider(BaseVisionProvider, BaseChatProvider, BaseImageProvider):
    """
    Google Gemini Multimodal AI Provider for Computer Vision,
    Interior Design Chat, and Image Synthesis.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.vision_model = "gemini-3.6-flash"
        self.chat_model = "gemini-3.6-flash"
        self.image_model = "gemini-3.1-flash-image"
        self.local_fallback = LocalCVFallback()

    def _encode_image(self, image_path: str) -> Optional[Dict[str, str]]:
        if not os.path.exists(image_path):
            return None
        try:
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type or not mime_type.startswith("image/"):
                mime_type = "image/jpeg"

            with open(image_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")

            return {
                "mime_type": mime_type,
                "data": b64_data
            }
        except Exception as e:
            print(f"Error encoding image for Gemini: {e}")
            return None

    def analyze_room_image(self, image_path: str, context: Optional[Dict[str, Any]] = None) -> VisionAnalysisResult:
        if not self.api_key:
            return self.local_fallback.analyze_room_image(image_path, context)

        image_data = self._encode_image(image_path)
        if not image_data:
            return self.local_fallback.analyze_room_image(image_path, context)

        prompt = """
        You are a professional AI Interior Design Computer Vision system.
        Analyze this room photo thoroughly and respond with a STRICT, VALID JSON object with this exact schema:
        {
          "roomType": "living_room | master_bedroom | bedroom | kids_bedroom | kitchen | dining_room | bathroom | balcony | pooja_room | home_office | study_room | hallway | foyer",
          "estimatedSize": "small | medium | large | spacious",
          "detectedStyle": "Modern | Modern Luxury | Minimalist | Scandinavian | Contemporary | Traditional | Industrial | Japandi | Indian Contemporary",
          "dominantColors": ["Color 1", "Color 2", "Color 3", "Color 4"],
          "detectedObjects": ["sofa", "coffee_table", "tv_unit", "chandelier", "rug", etc.],
          "structureInfo": {
            "walls": "smooth plaster / accent wall",
            "ceiling": "false ceiling / standard flat",
            "windows": "large floor-to-ceiling / standard casement",
            "doors": "wooden flush door",
            "columns": "none / corner column"
          },
          "lightingAnalysis": {
            "naturalLighting": "High / Moderate / Low",
            "fixtures": "cove lighting, recessed spots, pendant",
            "colorTemperature": "Warm White 3000K / Neutral 4000K"
          },
          "floorMaterial": "Italian Marble / Vitrified Tile / Hardwood Oak / Granite"
        }
        Return ONLY valid JSON.
        """

        url = f"{self.base_url}/{self.vision_model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"inline_data": image_data}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }

        try:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text)

                return VisionAnalysisResult(
                    room_type=parsed.get("roomType", "living_room"),
                    estimated_size=parsed.get("estimatedSize", "medium"),
                    detected_style=parsed.get("detectedStyle", "Modern Luxury"),
                    dominant_colors=parsed.get("dominantColors", ["Warm White", "Beige"]),
                    detected_objects=parsed.get("detectedObjects", []),
                    structure_info=parsed.get("structureInfo", {}),
                    lighting_analysis=parsed.get("lightingAnalysis", {}),
                    floor_material=parsed.get("floorMaterial", "Italian Marble"),
                    raw_analysis=parsed
                )
            else:
                print(f"Gemini API returned status {res.status_code}: {res.text[:150]}")
        except Exception as e:
            print(f"Gemini Vision call failed: {e}")

        # Fallback to local computer vision on failure
        return self.local_fallback.analyze_room_image(image_path, context)

    def analyze_multi_images(self, image_paths: List[str], context: Optional[Dict[str, Any]] = None) -> VisionAnalysisResult:
        if not self.api_key or not image_paths:
            return self.local_fallback.analyze_multi_images(image_paths, context)

        parts: List[Dict[str, Any]] = [
            {"text": "Analyze these multiple angles of the same room to build a comprehensive 3D spatial understanding. Return valid JSON matching the schema."}
        ]

        for p in image_paths[:4]: # Max 4 images
            img_data = self._encode_image(p)
            if img_data:
                parts.append({"inline_data": img_data})

        url = f"{self.base_url}/{self.vision_model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }

        try:
            res = requests.post(url, json=payload, timeout=40)
            if res.status_code == 200:
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text)

                return VisionAnalysisResult(
                    room_type=parsed.get("roomType", "living_room"),
                    estimated_size=parsed.get("estimatedSize", "medium"),
                    detected_style=parsed.get("detectedStyle", "Modern Luxury"),
                    dominant_colors=parsed.get("dominantColors", ["Warm White", "Beige"]),
                    detected_objects=parsed.get("detectedObjects", []),
                    structure_info=parsed.get("structureInfo", {}),
                    lighting_analysis=parsed.get("lightingAnalysis", {}),
                    floor_material=parsed.get("floorMaterial", "Italian Marble"),
                    raw_analysis=parsed
                )
        except Exception as e:
            print(f"Gemini Multi-image analysis failed: {e}")

        return self.local_fallback.analyze_multi_images(image_paths, context)

    def generate_chat_response(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> str:
        if not self.api_key:
            return self._local_chat_response(messages, context)

        # Format system prompt and conversation history
        system_instruction = (
            "You are DecoraAI, an elite AI Interior Designer. "
            "You provide thoughtful, highly actionable interior architecture advice, material selections, "
            "spatial optimization tips, and lighting recommendations. "
            "Maintain conversational context about the house and room."
        )

        if context:
            system_instruction += f"\nContext: House='{context.get('house_name', 'My House')}', Room='{context.get('room_name', 'Room')}', Style='{context.get('style', 'Modern Luxury')}', Budget=₹{context.get('budget', '15,00,000')}."

        contents = []
        for m in messages:
            role = "user" if m.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": m.get("message") or m.get("content", "")}]
            })

        url = f"{self.base_url}/{self.chat_model}:generateContent?key={self.api_key}"
        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}
        }

        try:
            res = requests.post(url, json=payload, timeout=25)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"Gemini chat failed: {e}")

        return self._local_chat_response(messages, context)

    def generate_image(self, prompt: str, reference_image_path: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> GeneratedDesignResult:
        # Check if Imagen 3 predict endpoint is accessible with this key
        if self.api_key:
            try:
                imagen_url = f"{self.base_url}/imagen-3.0-generate-002:predict?key={self.api_key}"
                payload = {
                    "instances": [{"prompt": prompt}],
                    "parameters": {"sampleCount": 1, "aspectRatio": "4:3"}
                }
                res = requests.post(imagen_url, json=payload, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    predictions = data.get("predictions", [])
                    if predictions and "bytesBase64Encoded" in predictions[0]:
                        b64 = predictions[0]["bytesBase64Encoded"]
                        return GeneratedDesignResult(
                            image_url=f"data:image/png;base64,{b64}",
                            prompt=prompt,
                            explanation="Photorealistic interior visualization generated with Google Imagen AI.",
                            metadata={"provider": "gemini_imagen"}
                        )
            except Exception as e:
                pass

        # Fallback to local synthesizer
        return self.local_fallback.generate_image(prompt, reference_image_path, options)

    def _local_chat_response(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> str:
        last_msg = (messages[-1].get("message") or messages[-1].get("content", "")).lower() if messages else ""
        room_name = (context or {}).get("room_name", "this room")
        style = (context or {}).get("style", "Modern Luxury")

        if "sofa" in last_msg or "seating" in last_msg:
            return f"For {room_name}, an L-shaped sectional in textured bouclé or taupe performance fabric will maximize seating capacity while maintaining clear walking aisles. Pairing it with a low-profile walnut coffee table adds warmth."
        elif "color" in last_msg or "wall" in last_msg:
            return f"To elevate {room_name}, consider soft warm white (LRV ~82) for primary walls, paired with a subtle fluted wood or lime-wash accent wall. This balances natural light and creates visual depth."
        elif "lighting" in last_msg or "bright" in last_msg:
            return f"I recommend a 3-layer lighting plan: 3000K warm white recessed ceiling spots for ambient light, LED strip profiles in cove moldings for soft indirect glow, and a statement brass or matte black fixture for accent."
        elif "budget" in last_msg or "cost" in last_msg:
            return f"To optimize the budget for {room_name}, focus investment on durable core pieces (flooring and primary seating), while using smart alternatives like high-grade laminate with edge banding for cabinetry and secondary storage."
        else:
            return f"I've tailored the design of {room_name} in {style} styling. We have preserved the natural window placement and room proportions while introducing cohesive materials, ambient lighting, and functional layout zoning. Let me know if you'd like adjustments to specific elements!"
