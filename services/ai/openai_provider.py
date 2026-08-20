import os
import json
import base64
import requests
from typing import List, Dict, Any, Optional
from services.ai.provider_base import VisionAnalysisResult, GeneratedDesignResult, BaseVisionProvider, BaseChatProvider, BaseImageProvider
from services.ai.local_cv_fallback import LocalCVFallback

class OpenAIProvider(BaseVisionProvider, BaseChatProvider, BaseImageProvider):
    """
    OpenAI Provider supporting GPT-4o (Vision & Structured JSON) and DALL-E 3.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.local_fallback = LocalCVFallback()

    def analyze_room_image(self, image_path: str, context: Optional[Dict[str, Any]] = None) -> VisionAnalysisResult:
        if not self.api_key or not os.path.exists(image_path):
            return self.local_fallback.analyze_room_image(image_path, context)

        try:
            with open(image_path, "rb") as f:
                b64_img = base64.b64encode(f.read()).decode("utf-8")

            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o",
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this interior room image. Output JSON with roomType, estimatedSize, detectedStyle, dominantColors, detectedObjects, structureInfo, lightingAnalysis, floorMaterial."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                        ]
                    }
                ],
                "max_tokens": 800
            }

            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return VisionAnalysisResult(
                    room_type=parsed.get("roomType", "living_room"),
                    estimated_size=parsed.get("estimatedSize", "medium"),
                    detected_style=parsed.get("detectedStyle", "Modern Luxury"),
                    dominant_colors=parsed.get("dominantColors", ["Warm White", "Beige"]),
                    detected_objects=parsed.get("detectedObjects", []),
                    structure_info=parsed.get("structureInfo", {}),
                    lighting_analysis=parsed.get("lightingAnalysis", {}),
                    floor_material=parsed.get("floorMaterial", "Hardwood"),
                    raw_analysis=parsed
                )
        except Exception as e:
            print(f"OpenAI Vision error: {e}")

        return self.local_fallback.analyze_room_image(image_path, context)

    def analyze_multi_images(self, image_paths: List[str], context: Optional[Dict[str, Any]] = None) -> VisionAnalysisResult:
        return self.local_fallback.analyze_multi_images(image_paths, context)

    def generate_chat_response(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> str:
        if not self.api_key:
            return self.local_fallback._local_chat_response(messages, context)

        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            
            chat_msgs = [{"role": "system", "content": "You are DecoraAI, an elite interior designer. Provide expert architectural and styling advice."}]
            for m in messages:
                chat_msgs.append({"role": m.get("role", "user"), "content": m.get("message") or m.get("content", "")})

            res = requests.post(url, headers=headers, json={"model": "gpt-4o-mini", "messages": chat_msgs}, timeout=25)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"OpenAI chat error: {e}")

        return self.local_fallback._local_chat_response(messages, context)

    def generate_image(self, prompt: str, reference_image_path: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> GeneratedDesignResult:
        if not self.api_key:
            return self.local_fallback.generate_image(prompt, reference_image_path, options)

        try:
            url = "https://api.openai.com/v1/images/generations"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "dall-e-3",
                "prompt": f"Professional architectural photograph of interior design: {prompt}. Highly realistic, 8k resolution, architectural digest style, balanced interior lighting.",
                "n": 1,
                "size": "1024x1024"
            }
            res = requests.post(url, headers=headers, json=payload, timeout=50)
            if res.status_code == 200:
                img_url = res.json()["data"][0]["url"]
                return GeneratedDesignResult(
                    image_url=img_url,
                    prompt=prompt,
                    explanation="Photorealistic interior visualization generated via DALL-E 3.",
                    metadata={"provider": "dall-e-3"}
                )
        except Exception as e:
            print(f"OpenAI DALL-E 3 error: {e}")

        return self.local_fallback.generate_image(prompt, reference_image_path, options)
