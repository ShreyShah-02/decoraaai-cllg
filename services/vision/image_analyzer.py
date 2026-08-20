import os
from typing import List, Dict, Any, Optional
from services.ai.orchestrator import orchestrator
from services.ai.provider_base import VisionAnalysisResult

class ImageAnalyzer:
    """
    High-level Computer Vision service for analyzing single or multiple room photos.
    """

    def analyze_room(self, image_paths: List[str], room_context: Optional[Dict[str, Any]] = None) -> VisionAnalysisResult:
        if not image_paths:
            return orchestrator.local_cv._default_result(room_context)

        valid_paths = [p for p in image_paths if os.path.exists(p)]
        if not valid_paths:
            return orchestrator.local_cv._default_result(room_context)

        if len(valid_paths) == 1:
            return orchestrator.analyze_room_image(valid_paths[0], room_context)
        else:
            return orchestrator.analyze_multi_images(valid_paths, room_context)

image_analyzer = ImageAnalyzer()
