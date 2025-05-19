from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime

@dataclass
class PoseLandmark:
    """Classe para representar um landmark do corpo."""
    x: float
    y: float
    z: float
    visibility: float

@dataclass
class PoseFrame:
    """Classe para representar um frame com landmarks."""
    frame_number: int
    timestamp: float
    landmarks: Dict[int, PoseLandmark]

@dataclass
class PoseData:
    """Classe para representar dados de pose de um vídeo."""
    video_path: str
    video_hash: str
    fps: float
    resolution: Tuple[int, int]
    total_frames: int
    frames: List[PoseFrame]
    created_at: str = datetime.now().isoformat()
    version: str = "1.0" 
