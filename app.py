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
logger = logging.getLogger("D-Vision")


def parse_args():
    parser = argparse.ArgumentParser(
        description="D-Vision Dementia Assist Smart Glasses",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--db-path", type=Path, default=Path("face_db.json"))

    parser.add_argument(
        "--add_face",
        action="store_true",
        help="Add a new face to the database"
    )
    parser.add_argument("--name", type=str, help="Name for --add_face")

    return parser.parse_args()


def add_face_flow(camera, recognizer, db, name: str):
    logger.info("Add-face mode: Look at the camera.")
    embedding = None

    while True:
        ok, frame = camera.read()
        if not ok:
            continue

        boxes, encodings = recognizer.encode_faces(frame)
        display = frame.copy()

        if boxes and encodings:
            (t, r, b, l) = boxes[0]
            cv2.rectangle(display, (l, t), (r, b), (0, 255, 0), 2)
            cv2.putText(display, "Capturing face...", (l, t - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

            cv2.imshow("Add Face", display)
            cv2.waitKey(1000)

            embedding = encodings[0]
            break

        cv2.putText(display, "Align face...", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
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


def recognition_loop(camera, recognizer, db):
    logger.info("Recognition loop started. Press q to quit")
    overlay = Overlay()

    while True:
        ok, frame = camera.read()
        if not ok:
            continue

        boxes, encodings = recognizer.encode_faces(frame)
        display = frame.copy()

        if encodings:
            matches = []
            for enc in encodings:
                person, conf = db.lookup(enc)
                matches.append((person, conf))

            overlay.draw_overlays(display, boxes, matches)
        else:
            overlay.draw_instructions(display, "Scanning...")

        cv2.imshow("D-Vision", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            logger.info("Manual exit")
            break

    db.save()
    camera.release()
    cv2.destroyAllWindows()


def main():
    opts = parse_args()

    if opts.add_face and not opts.name:
        logger.error("--name required with --add_face")
        sys.exit(1)

    # Load DB
    db = FaceDatabase(opts.db_path)
    db.load()
    logger.info("Loaded DB (%d people)", len(db.people))

    # Camera
    cam = Camera(index=opts.camera_index)
    cam.open()

    # Recognizer
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
