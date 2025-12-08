import cv2

class Overlay:
    @staticmethod
    def draw_boxes(frame, face_locations, labels=None):
        """Draw bounding boxes and optional labels on faces."""
        for i, (top, right, bottom, left) in enumerate(face_locations):
            # Draw rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Draw label if provided
            if labels and i < len(labels) and labels[i]:
                text = labels[i]
                cv2.putText(
                    frame, text,
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

    @staticmethod
    def draw_instructions(frame, text):
        """Draw user instructions at bottom of the screen."""
        cv2.putText(
            frame, text,
            (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    def add_overlays(self, frame, face_locations, matches):
        """Draw recognition results."""
        labels = []

        for person, confidence in matches:
            if person:
                labels.append(f"{person.name} ({int(confidence*100)}%)")
            else:
                labels.append("Unknown")

        self.draw_boxes(frame, face_locations, labels)
        return frame
