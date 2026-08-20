import os
from typing import List, Dict, Any, Optional
from services.ai.provider_base import VisionAnalysisResult, GeneratedDesignResult
from services.ai.gemini_provider import GeminiProvider
from services.ai.openai_provider import OpenAIProvider
from services.ai.colab_provider import ColabProvider
from services.ai.local_cv_fallback import LocalCVFallback

class AIOrchestrator:
    """
    Central AI Manager orchestrating Vision Analysis, Conversational Chatbot,
    and Photorealistic Image Generation across configured providers.
    """

    def __init__(self):
        self.gemini = GeminiProvider()
        self.openai = OpenAIProvider()
        self.colab = ColabProvider()
        self.local_cv = LocalCVFallback()

    def analyze_room_image(self, image_path: str, context: Optional[Dict[str, Any]] = None) -> VisionAnalysisResult:
        if os.getenv("GEMINI_API_KEY"):
            try:
                return self.gemini.analyze_room_image(image_path, context)
            except Exception as e:
                print(f"Gemini vision failed, attempting fallback: {e}")

        if os.getenv("OPENAI_API_KEY"):
            try:
                return self.openai.analyze_room_image(image_path, context)
            except Exception as e:
                print(f"OpenAI vision failed, attempting fallback: {e}")

        return self.local_cv.analyze_room_image(image_path, context)

    def analyze_multi_images(self, image_paths: List[str], context: Optional[Dict[str, Any]] = None) -> VisionAnalysisResult:
        if os.getenv("GEMINI_API_KEY"):
            try:
                return self.gemini.analyze_multi_images(image_paths, context)
            except Exception as e:
                print(f"Gemini multi-image vision failed, attempting fallback: {e}")

        return self.local_cv.analyze_multi_images(image_paths, context)

    def generate_chat_response(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> str:
        if os.getenv("GEMINI_API_KEY"):
            try:
                return self.gemini.generate_chat_response(messages, context)
            except Exception as e:
                print(f"Gemini chat failed, falling back: {e}")

        if os.getenv("OPENAI_API_KEY"):
            try:
                return self.openai.generate_chat_response(messages, context)
            except Exception as e:
                print(f"OpenAI chat failed, falling back: {e}")

        return self.local_cv._local_chat_response(messages, context)

    def generate_image(self, prompt: str, reference_image_path: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> GeneratedDesignResult:
        # 1. Try Gemini
        if os.getenv("GEMINI_API_KEY"):
            try:
                result = self.gemini.generate_image(prompt, reference_image_path, options)
                if result and result.image_url and not result.image_url.startswith("https://images.unsplash"):
                    return result
            except Exception as e:
                print(f"Gemini image generation exception: {e}")

        # 2. Try Colab SD tunnel if available
        colab_url = os.getenv("COLAB_API")
        if colab_url and "ngrok" in colab_url:
            try:
                res = self.colab.generate_image(prompt, reference_image_path, options)
                if res and res.image_url and not res.image_url.startswith("https://images.unsplash"):
                    return res
            except Exception as e:
                print(f"Colab generation exception: {e}")

        # 3. Try OpenAI DALL-E if key provided
        if os.getenv("OPENAI_API_KEY"):
            try:
                res = self.openai.generate_image(prompt, reference_image_path, options)
                if res and res.image_url and not res.image_url.startswith("https://images.unsplash"):
                    return res
            except Exception as e:
                print(f"OpenAI generation exception: {e}")

        # 4. Pure fallback
        return self.local_cv.generate_image(prompt, reference_image_path, options)

# Global orchestrator singleton
orchestrator = AIOrchestrator()
