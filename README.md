# D-Vision: Smart Glasses Face Recognition Demo

This demo lets you run the smart-glasses experience on your laptop webcam before hardware arrives. It detects faces in real time, recognizes known people, and overlays their names on the video feed.

## Features
- Real-time webcam capture with OpenCV.
- Face detection and recognition using the lightweight [`face_recognition`](https://github.com/ageitgey/face_recognition) library.
- Simple CLI flow to add new people to the local database.
- JSON-based database storing names and embeddings for offline use.
- Overlay UI that labels recognized faces with confidence scores and shows "Unknown Person" when no match is found.
- Designed with future hardware integration points for Pi Camera input and HUD/OLED display output.

## Folder Structure
```
app.py              # Main entry point: detection + recognition pipeline
camera.py           # Webcam capture helper (future: swap in Pi Camera)
recognition.py      # Face encoding + matching logic
ui.py               # Drawing utilities for bounding boxes and labels
database.py         # JSON-backed storage for embeddings
requirements.txt    # Python dependencies
face_db.json        # Created after you add faces; stores embeddings and names
```

## Installation
1. Install Python 3.10+.
2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   *On Raspberry Pi later:* use prebuilt wheels for `dlib`/`face_recognition` or `pip install face_recognition --no-binary :all:` if building from source.

## Usage
### Run the real-time recognition demo
```bash
python app.py
```
- Press `q` to quit.
- If no faces are detected, the live feed still shows with an on-screen instruction.

### Add a new known face
```bash
python app.py --add_face --name "Mom"
```
- Keep your face in view; the first detected face is saved automatically.
- Press `q` to cancel without saving.

### Webcam selection
Use a different camera index if needed (default is `0`):
```bash
python app.py --camera-index 1
```

### Database file
- Stored at `face_db.json` by default; change with `--db-path /path/to/file.json`.
- Structure example:
```json
{
  "people": [
    {
      "name": "Mom",
      "embedding": [0.11, 0.02, ...]
    }
  ]
}
```
- Embeddings are 128-length float vectors from `face_recognition`.

## Performance tips (for Raspberry Pi Zero 2 W later)
- Frames are resized before detection to cap the longest side at 500 px.
- Use the default `hog` model for CPU-only inference; switch to `--detection-model cnn` if you enable GPU acceleration.
- Lower `--frame-width` to reduce processing load.
- Keep database small and curated to speed up matching.

## Troubleshooting
- **Webcam not found**: the app logs an error and exits. Make sure no other process is using the camera.
- **No faces detected**: you still see the live feed; adjust lighting or move closer.

## Future integration points
- Swap the webcam capture in `camera.py` with Pi Camera APIs.
- Redirect labels drawn in `ui.py` to a small HUD/OLED screen instead of the computer display.
