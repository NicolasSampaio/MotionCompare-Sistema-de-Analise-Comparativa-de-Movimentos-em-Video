from dataclasses import dataclass

@dataclass
class PoseLandmark:
    """Classe para representar um landmark do corpo."""
    x: float
    y: float
    z: float
    visibility: float 
