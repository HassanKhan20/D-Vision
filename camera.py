from typing import Any, Optional, Tuple

import cv2


class Camera:
    """
    Webcam wrapper to grab frames and perform lightweight resizing.

    Future integration: replace webcam with Pi Camera feed here when hardware is available.
    """

    def __init__(self, index: int = 0, frame_width: int = 640):
        self.index = index
        self.frame_width = frame_width
        self._capture: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        self._capture = cv2.VideoCapture(self.index)
        if not self._capture.isOpened():
            return False
        if self.frame_width:
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        return True

    def read(self) -> Tuple[bool, Optional[Any]]:
        if self._capture is None:
            return False, None
        success, frame = self._capture.read()
        return success, frame

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
