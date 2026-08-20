from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class VisionAnalysisResult:
    room_type: str
    estimated_size: str
    detected_style: str
    dominant_colors: List[str]
    detected_objects: List[str]
    structure_info: Dict[str, Any]
    lighting_analysis: Dict[str, Any]
    floor_material: str
    raw_analysis: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeneratedDesignResult:
    image_url: str
    prompt: str
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseVisionProvider(ABC):
    @abstractmethod
    def analyze_room_image(self, image_path: str, context: Optional[Dict[str, Any]] = None) -> VisionAnalysisResult:
        pass

    @abstractmethod
    def analyze_multi_images(self, image_paths: List[str], context: Optional[Dict[str, Any]] = None) -> VisionAnalysisResult:
        pass

class BaseChatProvider(ABC):
    @abstractmethod
    def generate_chat_response(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> str:
        pass

class BaseImageProvider(ABC):
    @abstractmethod
    def generate_image(self, prompt: str, reference_image_path: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> GeneratedDesignResult:
        pass
