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
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--db-path", type=Path, default=Path("face_db.json"))
    parser.add_argument("--add_face", action="store_true")
    parser.add_argument("--name", type=str, default=None)
    parser.add_argument("--frame-width", type=int, default=640)
    parser.add_argument("--detection-model", type=str, default="hog", choices=["hog", "cnn"])
    return parser.parse_args()


def add_face_flow(camera: Camera, recognizer: FaceRecognizer, db: FaceDatabase, name: str):
    overlay = Overlay()
    logger.info("Add-face mode: press SPACE to save, 'q' to cancel")

    while True:
        success, frame = camera.read()
        if not success or frame is None:
            logger.error("Camera read failed")
            break

        rgb_frame, face_locations, encodings = recognizer.encode_faces(frame)
        display_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        if face_locations:
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
            Overlay.draw_instructions(display_frame, "Press SPACE to save face")
        else:
            Overlay.draw_instructions(display_frame, "No face detected — look at the camera")

        cv2.imshow("Add Face", display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            logger.info("Canceled adding face.")
            break

        if key == ord(" ") and encodings:
            db.add_embedding(name, encodings[0])
            logger.info(f"Stored new face for {name}")
            break

    cv2.destroyAllWindows()


def recognition_loop(camera: Camera, recognizer: FaceRecognizer, db: FaceDatabase):
    overlay = Overlay()
    logger.info("Recognition mode — press 'q' to quit")

    while True:
        success, frame = camera.read()
        if not success or frame is None:
            logger.error("Camera frame read failed")
            continue

        rgb_frame, face_locations, encodings = recognizer.encode_faces(frame)
        display_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        if face_locations:
            matches = recognizer.match_faces(encodings, db)

            for (top, right, bottom, left), match in zip(face_locations, matches):
                cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                label = f"{match.name} ({match.confidence:.2f})" if match.name else "Unknown"
                cv2.putText(display_frame, label, (left, top - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            Overlay.draw_instructions(display_frame, "No face detected 👀 Move closer")

        cv2.imshow("D-Vision Smart Glasses", display_frame)

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
        logger.error("Failed to initialize camera.")
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
