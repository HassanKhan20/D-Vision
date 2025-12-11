"""
D-Vision - AI-Powered Smart Glasses for Dementia Assistance.

A real-time face recognition system designed to run on Raspberry Pi Zero 2 W
for wearable heads-up display applications.
"""

__version__ = "0.1.0"
__author__ = "Hassan Khan"

from .config import (
    RECOGNITION_TOLERANCE,
    SEEN_COOLDOWN_SECONDS,
    DEFAULT_CAMERA_INDEX,
    DEFAULT_FRAME_WIDTH,
)
from .camera import Camera
from .database import FaceDatabase, Person
from .recognition import FaceRecognizer
from .ui import Overlay

__all__ = [
    "Camera",
    "FaceDatabase",
    "Person",
    "FaceRecognizer",
    "Overlay",
    "RECOGNITION_TOLERANCE",
    "SEEN_COOLDOWN_SECONDS",
    "DEFAULT_CAMERA_INDEX",
    "DEFAULT_FRAME_WIDTH",
]
