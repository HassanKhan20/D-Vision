"""
D-Vision Configuration Constants.

Centralized configuration for the D-Vision face recognition system.
Designed for portability to Raspberry Pi Zero 2 W hardware.
"""

from pathlib import Path

# =============================================================================
# Face Recognition
# =============================================================================
RECOGNITION_TOLERANCE: float = 0.91  # Minimum confidence for positive match
SEEN_COOLDOWN_SECONDS: int = 60      # Cooldown before incrementing seen_count

# =============================================================================
# Performance Tuning
# =============================================================================
RECOGNITION_SKIP_FRAMES: int = 2     # Process every Nth frame (1=all, 2=half, 3=third)
                                     # Higher values = better FPS, slower detection

# =============================================================================
# Camera Settings
# =============================================================================
DEFAULT_CAMERA_INDEX: int = 0
DEFAULT_FRAME_WIDTH: int = 640
CAMERA_FPS: int = 60
CAMERA_BUFFER_SIZE: int = 1  # Minimize latency for real-time processing

# For Raspberry Pi, you may need to adjust:
# CAMERA_FPS = 30  # Pi Zero 2 W may not sustain 60fps
# DEFAULT_FRAME_WIDTH = 320  # Lower resolution for performance

# =============================================================================
# UI Colors (BGR format for OpenCV)
# =============================================================================
COLOR_GREEN: tuple[int, int, int] = (0, 255, 0)
COLOR_WHITE: tuple[int, int, int] = (255, 255, 255)
COLOR_YELLOW: tuple[int, int, int] = (255, 255, 0)
COLOR_CYAN: tuple[int, int, int] = (0, 255, 255)
COLOR_LIGHT_PURPLE: tuple[int, int, int] = (200, 200, 255)

# =============================================================================
# Paths
# =============================================================================
DEFAULT_DB_PATH: Path = Path("face_db.json")

# =============================================================================
# Future: STT/LLM Integration Placeholders
# =============================================================================
# STT_MODEL: str = "whisper-tiny"  # Lightweight for Pi Zero 2 W
# LLM_ENDPOINT: str = "http://localhost:8080/v1/chat"
