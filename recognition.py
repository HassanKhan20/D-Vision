from typing import List, Sequence, Tuple

import cv2
import face_recognition
import numpy as np

from database import FaceDatabase, PersonMatch


class FaceRecognizer:
    """Encodes and matches faces using the lightweight face_recognition library."""

    def __init__(self, model: str = "hog"):
        self.model = model

    def encode_faces(self, frame) -> Tuple[Sequence[Tuple[int, int, int, int]], List[np.ndarray]]:
        """Locate faces and return their embeddings."""
        small_frame = self._resize_for_speed(frame)
        face_locations = face_recognition.face_locations(small_frame, model=self.model)
        encodings = face_recognition.face_encodings(small_frame, face_locations)

        # Scale locations back to original frame size
        scale_y = frame.shape[0] / small_frame.shape[0]
        scale_x = frame.shape[1] / small_frame.shape[1]
        scaled_locations = []
        for top, right, bottom, left in face_locations:
            scaled_locations.append(
                (
                    int(top * scale_y),
                    int(right * scale_x),
                    int(bottom * scale_y),
                    int(left * scale_x),
                )
            )
        return scaled_locations, encodings

    def match_faces(self, encodings: List[np.ndarray], db: FaceDatabase) -> List[PersonMatch]:
        matches: List[PersonMatch] = []
        if not encodings:
            return matches

        known_encodings, names = db.get_all_embeddings()
        if not known_encodings:
            return [PersonMatch(name=None, confidence=0.0) for _ in encodings]

        for encoding in encodings:
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_index = int(np.argmin(distances))
            best_distance = float(distances[best_index])
            confidence = self._distance_to_confidence(best_distance)
            matched_name = names[best_index] if confidence > 0 else None
            matches.append(PersonMatch(name=matched_name, confidence=confidence))
        return matches

    @staticmethod
    def _resize_for_speed(frame, max_dimension: int = 500):
        height, width = frame.shape[:2]
        if max(height, width) <= max_dimension:
            return frame
        scale = max_dimension / float(max(height, width))
        new_size = (int(width * scale), int(height * scale))
        return cv2.resize(frame, new_size)

    @staticmethod
    def _distance_to_confidence(distance: float) -> float:
        # A simple mapping where lower distance -> higher confidence.
        confidence = max(0.0, 1.0 - distance)
        return round(confidence, 2)
