"""
Face recognition module for D-Vision.

Uses MediaPipe for fast face detection and dlib (via face_recognition)
for generating 128-dimensional face embeddings.
"""

import cv2
import mediapipe as mp
import face_recognition
import numpy as np
from typing import List, Tuple


# Type aliases for clarity
FaceLocation = Tuple[int, int, int, int]  # (top, right, bottom, left)
FaceEncoding = np.ndarray  # 128-dimensional float array


class FaceRecognizer:
    """
    Hybrid face detection and encoding pipeline.
    
    Uses MediaPipe for fast GPU-accelerated face detection, then
    dlib for generating robust face embeddings.
    
    Note for Pi Zero 2 W: Consider reducing min_detection_confidence
    or switching to a lighter model for better performance.
    """

    def __init__(self) -> None:
        self.detector = mp.solutions.face_detection.FaceDetection(
            model_selection=1,  # 0 = short-range, 1 = full-range
            min_detection_confidence=0.6,
        )

    def encode_faces(
        self, bgr_frame: np.ndarray
    ) -> Tuple[List[FaceLocation], List[FaceEncoding]]:
        """
        Detect faces and generate encodings from a BGR frame.
        
        Args:
            bgr_frame: OpenCV BGR image (numpy array).
            
        Returns:
            Tuple of (face_locations, face_encodings).
            Both lists will be empty if no faces are detected.
        """
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)
        results = self.detector.process(rgb)

        face_locations: List[FaceLocation] = []
        encodings: List[FaceEncoding] = []

        if results.detections:
            h, w, _ = rgb.shape
            
            for det in results.detections:
                box = det.location_data.relative_bounding_box
                top = int(box.ymin * h)
                left = int(box.xmin * w)
                bottom = int((box.ymin + box.height) * h)
                right = int((box.xmin + box.width) * w)
                face_locations.append((top, right, bottom, left))

            # Generate embeddings using dlib (via face_recognition)
            encodings = face_recognition.face_encodings(rgb, face_locations)

        return face_locations, encodings

