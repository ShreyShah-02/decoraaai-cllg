import os
import requests
from typing import Dict, Any, Optional
from services.ai.provider_base import GeneratedDesignResult, BaseImageProvider
from services.ai.local_cv_fallback import LocalCVFallback

class ColabProvider(BaseImageProvider):
    """
    Provider connecting to a Google Colab or local Stable Diffusion ngrok tunnel.
    """

    def __init__(self, endpoint_url: Optional[str] = None):
        self.endpoint_url = endpoint_url or os.getenv("COLAB_API", "https://stagnant-tapered-congrats.ngrok-free.dev/generate")
        self.local_fallback = LocalCVFallback()

    def generate_image(self, prompt: str, reference_image_path: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> GeneratedDesignResult:
        if not self.endpoint_url:
            return self.local_fallback.generate_image(prompt, reference_image_path, options)

        try:
            headers = {"ngrok-skip-browser-warning": "true"}
            payload = {"prompt": prompt}

            response = requests.post(self.endpoint_url, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                data = response.json()
                if "image" in data:
                    img_data = data["image"]
                    if not img_data.startswith("data:image"):
                        img_data = f"data:image/png;base64,{img_data}"
                    return GeneratedDesignResult(
                        image_url=img_data,
                        prompt=prompt,
                        explanation="Generated via Google Colab Stable Diffusion endpoint.",
                        metadata={"provider": "colab_sd"}
                    )
                elif "image_url" in data:
                    return GeneratedDesignResult(
                        image_url=data["image_url"],
                        prompt=prompt,
                        explanation="Generated via Google Colab Stable Diffusion endpoint.",
                        metadata={"provider": "colab_sd"}
                    )
        except Exception as e:
            print(f"Colab generation connection error: {e}")

        return self.local_fallback.generate_image(prompt, reference_image_path, options)
