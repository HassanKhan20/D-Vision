from typing import List, Optional, Sequence, Tuple

import cv2

from database import PersonMatch


class Overlay:
    """Draws bounding boxes and labels on frames."""

    def add_overlays(
        self,
        frame,
        face_locations: Sequence[Tuple[int, int, int, int]],
        matches: List[PersonMatch],
    ):
        labeled_frame = frame.copy()
        labels = []
        for match in matches:
            if match.name:
                label = f"{match.name} ({match.confidence:.2f})"
            else:
                label = "Unknown Person"
            labels.append(label)

        self.draw_boxes(labeled_frame, face_locations, labels)
        return labeled_frame

    @staticmethod
    def draw_boxes(
        frame,
        face_locations: Sequence[Tuple[int, int, int, int]],
        labels: Optional[List[str]] = None,
    ) -> None:
        for i, (top, right, bottom, left) in enumerate(face_locations):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            if labels:
                Overlay.draw_label(frame, labels[i], (left, top - 10))

    @staticmethod
    def draw_label(frame, text: str, position) -> None:
        cv2.putText(
            frame,
            text,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    @staticmethod
    def draw_instructions(frame, text: str) -> None:
        cv2.putText(
            frame,
            text,
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

    # Future integration: redirect these labels to an external HUD/OLED display here.
