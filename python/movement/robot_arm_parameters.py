from dataclasses import dataclass

@dataclass
class Parameters:
    SEGMENT_LENGTH: float = 300.0
    AX12_SHOULDER_MIN_ANGLE: int = -130
    AX12_SHOULDER_MAX_ANGLE: int = 130
    AX12_ELBOW_MIN_ANGLE: int = -150
    AX12_ELBOW_MAX_ANGLE: int = 150
    FORBIDDEN_RADIUS: float = 250.0


