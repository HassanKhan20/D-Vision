"""
D-Vision - AI-Powered Smart Glasses Application.

Main entry point for the face recognition system designed for
dementia assistance. Runs on desktop for development, with
planned deployment to Raspberry Pi Zero 2 W.

Usage:
    python -m dvision                       # Run face recognition
    python -m dvision --add-face --name "Name" # Add a new face
    python -m dvision --camera-index 1      # Use different camera
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from .camera import Camera
from .config import DEFAULT_DB_PATH, RECOGNITION_SKIP_FRAMES
from .database import FaceDatabase
from .recognition import FaceRecognizer
from .ui import Overlay

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("D-Vision")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="D-Vision Dementia Assist Smart Glasses",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Camera device index",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Path to face database JSON file",
    )
    parser.add_argument(
        "--add-face",
        action="store_true",
        help="Add a new face to the database",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Name for the person (required with --add-face)",
    )

    return parser.parse_args()


def add_face_flow(
    camera: Camera,
    recognizer: FaceRecognizer,
    db: FaceDatabase,
    name: str,
) -> None:
    """
    Capture and save a new face to the database.
    
    Displays the camera feed until a face is detected, then
    prompts for the person's relation to the user.
    
    Args:
        camera: Camera instance for video capture.
        recognizer: FaceRecognizer for encoding faces.
        db: FaceDatabase to save the new person.
        name: Name of the person being added.
    """
    logger.info("Add-face mode: Look at the camera.")
    embedding: Optional[np.ndarray] = None

    while True:
        ok, frame = camera.read()
        if not ok or frame is None:
            continue

        boxes, encodings = recognizer.encode_faces(frame)
        display = frame.copy()

        if boxes and encodings:
            # Face detected - show preview
            top, right, bottom, left = boxes[0]
            cv2.rectangle(display, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(
                display, "Capturing face...", (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2
            )

            cv2.imshow("Add Face", display)
            cv2.waitKey(1000)  # Brief pause to show capture feedback

            embedding = encodings[0]
            break

        # No face yet - show instructions
        cv2.putText(
            display, "Align face...", (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
        )
        cv2.imshow("Add Face", display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            embedding = None
            break

    cv2.destroyAllWindows()

    if embedding is not None:
        relation = input(f"Relation of {name} to user: ").strip()
        db.add_embedding(name, embedding, relation)
        db.save()
        logger.info("✔ Added %s (%s)", name, relation)
    else:
        logger.info("No face captured → Nothing saved")


def recognition_loop(
    camera: Camera,
    recognizer: FaceRecognizer,
    db: FaceDatabase,
) -> None:
    """
    Main recognition loop - continuously detect and identify faces.
    
    Uses skip-frame processing to reduce CPU load: only runs face
    detection/encoding every Nth frame (configured by RECOGNITION_SKIP_FRAMES).
    Cached results are displayed on skipped frames for smooth video.
    
    Args:
        camera: Camera instance for video capture.
        recognizer: FaceRecognizer for detection and encoding.
        db: FaceDatabase for matching faces.
    """
    logger.info(
        "Recognition loop started (skip-frame: %d). Press 'q' to quit.",
        RECOGNITION_SKIP_FRAMES
    )
    overlay = Overlay()
    
    # Skip-frame processing state
    frame_counter = 0
    cached_boxes: list = []
    cached_matches: list = []

    while True:
        ok, frame = camera.read()
        if not ok or frame is None:
            continue

        frame_counter += 1
        display = frame  # Avoid copy on skipped frames
        
        # Only run expensive face detection/encoding every Nth frame
        if frame_counter % RECOGNITION_SKIP_FRAMES == 0:
            boxes, encodings = recognizer.encode_faces(frame)
            
            if encodings:
                # Match each detected face against the database
                matches = []
                for enc in encodings:
                    person, conf = db.lookup(enc)
                    matches.append((person, conf))
                cached_boxes, cached_matches = boxes, matches
            else:
                cached_boxes, cached_matches = [], []
        
        # Draw overlays using cached or fresh results
        if cached_boxes:
            display = frame.copy()  # Only copy when drawing
            overlay.draw_overlays(display, cached_boxes, cached_matches)
        else:
            display = frame.copy()
            overlay.draw_instructions(display, "Scanning...")

        cv2.imshow("D-Vision", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            logger.info("Manual exit")
            break

    db.save()
    camera.release()
    cv2.destroyAllWindows()


def main() -> None:
    """Application entry point."""
    opts = parse_args()

    # Validate arguments
    if opts.add_face and not opts.name:
        logger.error("--name is required with --add-face")
        sys.exit(1)

    # Initialize components
    db = FaceDatabase(opts.db_path)
    db.load()
    logger.info("Loaded database with %d people", len(db.people))

    cam = Camera(index=opts.camera_index)
    if not cam.open():
        logger.error("Failed to open camera %d", opts.camera_index)
        sys.exit(1)

    rec = FaceRecognizer()

    try:
        if opts.add_face:
            add_face_flow(cam, rec, db, opts.name)
        else:
            recognition_loop(cam, rec, db)
    except KeyboardInterrupt:
        logger.info("User interrupted")
    finally:
        db.save()
        cam.release()
        cv2.destroyAllWindows()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
