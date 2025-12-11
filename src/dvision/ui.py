"""
UI overlay module for D-Vision.

Provides on-screen display elements for the heads-up display,
including face bounding boxes, names, and status messages.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional

from .config import (
    RECOGNITION_TOLERANCE,
    COLOR_GREEN,
    COLOR_WHITE,
    COLOR_YELLOW,
    COLOR_LIGHT_PURPLE,
)
from .database import Person


# Type aliases
FaceLocation = Tuple[int, int, int, int]  # (top, right, bottom, left)
MatchResult = Tuple[Optional[Person], float]  # (person or None, confidence)


class Overlay:
    """
    Heads-up display overlay renderer.
    
    Draws bounding boxes, names, and metadata on video frames.
    Designed for clear visibility on smart glasses display.
    """

    @staticmethod
    def draw_overlays(
        frame: np.ndarray,
        face_locations: List[FaceLocation],
        matches: List[MatchResult],
    ) -> np.ndarray:
        """
        Draw recognition overlays on detected faces.
        
        Args:
            frame: BGR image to draw on (modified in-place).
            face_locations: List of face bounding boxes.
            matches: List of (person, confidence) for each face.
            
        Returns:
            The modified frame.
        """
        for box, (person, conf) in zip(face_locations, matches):
            if person is None or conf < RECOGNITION_TOLERANCE:
                continue  # Skip uncertain matches

            top, right, bottom, left = box
            name = person.name
            seen = f"Seen {person.seen_count}x"
            last_seen = f"Last seen: {person.last_seen or '--'}"

            # Draw bounding box
            cv2.rectangle(frame, (left, top), (right, bottom), COLOR_GREEN, 2)

            # Draw name above box
            cv2.putText(
                frame, name, (left, top - 10),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, COLOR_GREEN, 2
            )

            # Draw seen count below box
            cv2.putText(
                frame, seen, (left, bottom + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_YELLOW, 2
            )

            # Draw last seen timestamp
            cv2.putText(
                frame, last_seen, (left, bottom + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_LIGHT_PURPLE, 1
            )

        return frame

    @staticmethod
    def draw_instructions(frame: np.ndarray, text: str) -> None:
        """Draw instruction text on the frame."""
        cv2.putText(
            frame, text, (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WHITE, 2
        )

    @staticmethod
    def draw_status_message(frame: np.ndarray, text: str) -> None:
        """Draw status message at bottom of frame."""
        cv2.putText(
            frame, text, (20, 400),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2
        )

