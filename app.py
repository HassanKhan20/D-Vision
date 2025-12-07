import argparse
import logging
import sys
from pathlib import Path

import cv2

from camera import Camera
from database import FaceDatabase
from recognition import FaceRecognizer
from ui import Overlay


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Real-time face recognition demo for AI-powered smart glasses.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--camera-index", type=int, default=0, help="Webcam index to use.")
    parser.add_argument("--db-path", type=Path, default=Path("face_db.json"), help="Path to the face database file.")
    parser.add_argument(
        "--add_face",
        action="store_true",
        help="Add a new face to the database instead of running the recognition demo.",
    )
    parser.add_argument("--name", type=str, default=None, help="Name to register when using --add_face.")
    parser.add_argument(
        "--frame-width",
        type=int,
        default=640,
        help="Width to resize frames for faster processing (height auto-scales).",
    )
    parser.add_argument(
        "--detection-model",
        type=str,
        default="hog",
        choices=["hog", "cnn"],
        help="Model used by face_recognition for locating faces.",
    )
    return parser.parse_args()


def add_face_flow(camera: Camera, recognizer: FaceRecognizer, db: FaceDatabase, name: str):
    logger.info("Add-face mode: press 'q' to cancel.")
    while True:
        success, frame = camera.read()
        if not success:
            logger.error("Failed to read from the camera. Aborting add-face flow.")
            break

        face_locations, encodings = recognizer.encode_faces(frame)
        overlay_frame = frame.copy()
        Overlay.draw_boxes(overlay_frame, face_locations, labels=None)
        Overlay.draw_instructions(overlay_frame, "Look at the camera to capture your face.")
        cv2.imshow("Add Face", overlay_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            logger.info("Add-face flow cancelled by user.")
            break

        if encodings:
            embedding = encodings[0]
            db.add_embedding(name, embedding)
            logger.info("Stored new face for %s", name)
            break

    cv2.destroyAllWindows()


def recognition_loop(camera: Camera, recognizer: FaceRecognizer, db: FaceDatabase):
    overlay = Overlay()
    logger.info("Starting recognition loop. Press 'q' to quit.")

    while True:
        success, frame = camera.read()
        if not success:
            logger.error("Webcam feed unavailable. Please check the connection and retry.")
            break

        face_locations, encodings = recognizer.encode_faces(frame)

        if not face_locations:
            # Show live feed even when no faces are detected.
            Overlay.draw_instructions(frame, "No faces detected. Keep looking at the camera.")
            cv2.imshow("D-Vision Smart Glasses", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue

        matches = recognizer.match_faces(encodings, db)
        overlay_frame = overlay.add_overlays(frame, face_locations, matches)

        cv2.imshow("D-Vision Smart Glasses", overlay_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


def main():
    args = parse_args()

    if args.add_face and not args.name:
        logger.error("--name is required when using --add_face")
        sys.exit(1)

    db = FaceDatabase(args.db_path)
    db.load()

    camera = Camera(index=args.camera_index, frame_width=args.frame_width)
    if not camera.open():
        logger.error("Failed to initialize webcam. Ensure it is connected and not in use.")
        sys.exit(1)

    recognizer = FaceRecognizer(model=args.detection_model)

    if args.add_face:
        add_face_flow(camera, recognizer, db, args.name)
    else:
        recognition_loop(camera, recognizer, db)

    db.save()
    camera.release()


if __name__ == "__main__":
    main()
