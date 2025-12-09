import cv2
import mediapipe as mp
import face_recognition
import numpy as np


class FaceRecognizer:
    def __init__(self):
        self.detector = mp.solutions.face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.6
        )

    def encode_faces(self, bgr_frame):
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)
        results = self.detector.process(rgb)

        face_locations = []
        encodings = []

        if results.detections:
            h, w, _ = rgb.shape
            for det in results.detections:
                box = det.location_data.relative_bounding_box
                top = int(box.ymin * h)
                left = int(box.xmin * w)
                bottom = int((box.ymin + box.height) * h)
                right = int((box.xmin + box.width) * w)
                face_locations.append((top, right, bottom, left))

            encodings = face_recognition.face_encodings(rgb, face_locations)

        return face_locations, encodings

    def match_faces(self, encodings, db):
        matches = []
        for encoding in encodings:
            matches.append(db.lookup(encoding))
        return matches
