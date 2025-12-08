import cv2
import face_recognition
import numpy as np
from typing import Tuple, List
from database import FaceDatabase, PersonMatch

class FaceRecognizer:
    def __init__(self, model="hog"):
        self.model = model

    def encode_faces(self, frame) -> Tuple[np.ndarray, List[Tuple[int, int, int, int]], List[np.ndarray]]:
        if frame is None:
            return frame, [], []

        # Force correct datatype + convert FROM BGR to RGB
        frame = frame.astype("uint8")
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            face_locations = face_recognition.face_locations(rgb_frame, model=self.model)
        except Exception as e:
            print(f"❌ Face detection error: {e}")
            return rgb_frame, [], []

        encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        return rgb_frame, face_locations, encodings

    def match_faces(self, encodings, db: FaceDatabase):
        matches = []
        if not encodings:
            return matches

        known_encodings, names = db.get_all_embeddings()
        if not known_encodings:
            return [PersonMatch(name=None, confidence=0.0) for _ in encodings]

        for encoding in encodings:
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_index = int(np.argmin(distances))
            best_distance = float(distances[best_index])
            confidence = max(0.0, 1.0 - best_distance)
            matches.append(PersonMatch(name=names[best_index] if confidence > 0.5 else None, confidence=round(confidence, 2)))

        return matches
