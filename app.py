import argparse
import logging
import sys
from pathlib import Path

import cv2
import numpy as np

from camera import Camera
from database import FaceDatabase
from recognition import FaceRecognizer
# Add this line after line 11 in app.py
logging.getLogger().setLevel(logging.DEBUG)
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
    """Capture a face and save it to the database."""
    logger.info("Add-face mode: position your face in view. Press 'q' to cancel.")
    
    while True:
        success, bgr_frame = camera.read()
        if not success or bgr_frame is None:
            logger.error("Failed to read from the camera. Aborting add-face flow.")
            break

        # Ensure frame is contiguous and valid
        bgr_frame = np.ascontiguousarray(bgr_frame)
        
        # Debug frame properties
        logger.debug(f"Frame shape: {bgr_frame.shape}, dtype: {bgr_frame.dtype}, contiguous: {bgr_frame.flags['C_CONTIGUOUS']}")

        try:
            # Get RGB frame and detections
            rgb_frame, face_locations, encodings = recognizer.encode_faces(bgr_frame)
        except Exception as e:
            logger.error(f"Error during face encoding: {e}")
            logger.error(f"Frame info - shape: {bgr_frame.shape}, dtype: {bgr_frame.dtype}")
            break
        
        # Draw on BGR frame for display
        display_frame = bgr_frame.copy()
        Overlay.draw_boxes(display_frame, face_locations, labels=None)
        
        if face_locations:
            Overlay.draw_instructions(display_frame, f"Face detected! Hold still... ({len(face_locations)} face(s))")
        else:
            Overlay.draw_instructions(display_frame, "Look at the camera to capture your face. Press 'q' to cancel.")
        
        cv2.imshow("Add Face", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            logger.info("Add-face flow cancelled by user.")
            break

        # Capture the first detected face
        if encodings and len(encodings) > 0:
            embedding = encodings[0]
            db.add_embedding(name, embedding)
            logger.info("Successfully stored face for '%s'", name)
            
            # Show confirmation for 1 second
            Overlay.draw_instructions(display_frame, f"Face captured for {name}!")
            cv2.imshow("Add Face", display_frame)
            cv2.waitKey(1000)
            break

    cv2.destroyAllWindows()


def recognition_loop(camera: Camera, recognizer: FaceRecognizer, db: FaceDatabase):
    """Main recognition loop - detect and identify faces in real-time."""
    overlay = Overlay()
    logger.info("Starting recognition loop. Press 'q' to quit.")

    while True:
        success, bgr_frame = camera.read()
        if not success or bgr_frame is None:
            logger.error("Webcam feed unavailable. Please check the connection and retry.")
            break

        # Ensure frame is contiguous
        bgr_frame = np.ascontiguousarray(bgr_frame)

        try:
            # Get RGB frame and detections (BGR→RGB conversion happens once in encode_faces)
            rgb_frame, face_locations, encodings = recognizer.encode_faces(bgr_frame)
        except Exception as e:
            logger.error(f"Error during face encoding: {e}")
            continue

        # Prepare display frame (use original BGR for OpenCV display)
        display_frame = bgr_frame.copy()

        if not face_locations:
            # Show live feed even when no faces are detected
            Overlay.draw_instructions(display_frame, "No faces detected. Keep looking at the camera.")
        else:
            # Match faces against database
            matches = recognizer.match_faces(encodings, db)
            # Add overlays to the BGR frame
            display_frame = overlay.add_overlays(display_frame, face_locations, matches)

        cv2.imshow("D-Vision Smart Glasses", display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            logger.info("Exiting recognition loop.")
            break

    cv2.destroyAllWindows()


def main():
    args = parse_args()

    if args.add_face and not args.name:
        logger.error("--name is required when using --add_face")
        sys.exit(1)

    # Initialize database
    db = FaceDatabase(args.db_path)
    db.load()
    logger.info("Loaded database from %s with %d known faces", args.db_path, len(db.people))

    # Initialize camera
    camera = Camera(index=args.camera_index, frame_width=args.frame_width)
    if not camera.open():
        logger.error("Failed to initialize webcam. Ensure it is connected and not in use.")
        sys.exit(1)
    logger.info("Camera initialized successfully")

    # Initialize recognizer
    recognizer = FaceRecognizer(model=args.detection_model)

    try:
        if args.add_face:
            add_face_flow(camera, recognizer, db, args.name)
        else:
            recognition_loop(camera, recognizer, db)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Clean up
        db.save()
        camera.release()
        logger.info("Database saved and camera released")


if __name__ == "__main__":
    main()