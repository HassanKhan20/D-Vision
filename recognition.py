import cv2
import mediapipe as mp
import face_recognition
import numpy as np


class FaceRecognizer:
    def __init__(self, model="hog"):
        # Mediapipe setup
        self.mp_face_detection = mp.solutions.face_detection
        self.detector = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.55
        )

        # Recognition model (still needed for encodings + DB match)
        self.model = model

    def encode_faces(self, bgr_frame):
        """Detect faces with Mediapipe and encode them with face_recognition."""
        if bgr_frame is None:
            return None, [], []

        # Convert to RGB for detection + embeddings
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        rgb_frame = np.ascontiguousarray(rgb_frame)

        # Detect face bounding boxes
        results = self.detector.process(rgb_frame)

        face_locations = []
        encodings = []

        if results.detections:
            h, w, _ = rgb_frame.shape

            for det in results.detections:
                bbox = det.location_data.relative_bounding_box
                top = int(bbox.ymin * h)
                left = int(bbox.xmin * w)
                bottom = int((bbox.ymin + bbox.height) * h)
                right = int((bbox.xmin + bbox.width) * w)

                # Clip bounds
                top = max(top, 0)
                left = max(left, 0)
                bottom = min(bottom, h)
                right = min(right, w)

                face_locations.append((top, right, bottom, left))

            # Encode all detected faces
            encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        return rgb_frame, face_locations, encodings

    def match_faces(self, encodings, db):
        """Match detected faces against known embeddings in DB."""
        matches = []
        for encoding in encodings:
            person, confidence = db.lookup(encoding)
            matches.append((person, confidence))
        return matches
