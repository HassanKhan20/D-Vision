"""
Camera module for D-Vision.

Provides a webcam abstraction layer that can be swapped for
Raspberry Pi camera or other video sources.
"""

import cv2
import numpy as np
from typing import Optional, Tuple

from .config import (
    DEFAULT_CAMERA_INDEX,
    DEFAULT_FRAME_WIDTH,
    CAMERA_FPS,
    CAMERA_BUFFER_SIZE,
)


class Camera:
    """
    Webcam capture wrapper with configurable settings.
    
    Designed to be easily swappable for Pi Camera on Raspberry Pi Zero 2 W.
    
    Attributes:
        index: Camera device index (0 = default webcam).
        frame_width: Target frame width in pixels.
    """

    def __init__(
        self,
        index: int = DEFAULT_CAMERA_INDEX,
        frame_width: int = DEFAULT_FRAME_WIDTH,
    ) -> None:
        self.index = index
        self.frame_width = frame_width
        self._capture: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        """
        Open the camera device and configure settings.
        
        Returns:
            True if camera opened successfully, False otherwise.
        """
        self._capture = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
        
        if not self._capture.isOpened():
            return False
        
        # Configure camera settings
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self._capture.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)  # Minimize latency
        self._capture.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        
        return True

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the camera.
        
        Returns:
            Tuple of (success: bool, frame: numpy array or None).
        """
        if self._capture is None:
            return False, None
            
        success, frame = self._capture.read()
        if not success or frame is None:
            return False, None
        return True, frame

    def release(self) -> None:
        """Release camera resources."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
