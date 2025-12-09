import cv2
from typing import Optional, Tuple, Any

class Camera:
    def __init__(self, index=0, frame_width=640):
        self.index = index
        self.frame_width = frame_width
        self._capture = None

    def open(self) -> bool:
        self._capture = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
        if not self._capture.isOpened():
            return False
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        return True
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # No buffering → no lag
        self.cap.set(cv2.CAP_PROP_FPS, 60)


    def read(self) -> Tuple[bool, Optional[Any]]:
        success, frame = self._capture.read()
        if not success or frame is None:
            return False, None
        return True, frame

    def release(self):
        if self._capture:
            self._capture.release()
            self._capture = None
