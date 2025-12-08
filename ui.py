import cv2


class Overlay:

    @staticmethod
    def draw_text(frame, text, x, y, color=(0, 255, 0), scale=0.7, thickness=2):
        cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)

    @staticmethod
    def draw_box(frame, box, color=(0, 255, 0), thickness=2):
        top, right, bottom, left = box
        cv2.rectangle(frame, (left, top), (right, bottom), color, thickness)

    def add_overlays(self, frame, face_locations, matches):
        """Draw boxes + names + confidence scores."""
        for (top, right, bottom, left), match in zip(face_locations, matches):
            name = match.name if match.name else "Unknown"
            conf = int(match.confidence * 100)

            # Draw face bounding box
            self.draw_box(frame, (top, right, bottom, left))

            # Label below face
            label = f"{name} ({conf}%)"
            self.draw_text(frame, label, left, bottom + 20)

        return frame

    @staticmethod
    def draw_instructions(frame, text):
        """Text shown when no face detected."""
        cv2.putText(
            frame,
            text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
