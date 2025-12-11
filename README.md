<h1 align="center">🕶️ D-Vision — AI-Powered Smart Glasses</h1>

<p align="center">
Real-time face detection & recognition for wearable heads-up displays
<br>
Powered by OpenCV · MediaPipe · Face Recognition (dlib)
</p>

---

## 🎯 Mission

Bring personal AI assistance into the real world — starting with **smart glasses that recognize who you're looking at** and instantly show helpful context.

This repo contains the **desktop MVP** so the experience can be tested **before custom hardware arrives**.

---

## ✨ Features

| Feature | Status |
|--------|:------:|
| Real-time face detection on webcam | ✅ |
| Face recognition with confidence scoring | ✅ |
| Add new people to database via CLI | ✅ |
| Name + visual overlays | ✅ |
| Works completely offline | 🔒 |
| Pipeline ready for Raspberry Pi HUD | 🧩 Next |

---

## 🧱 Architecture

```
Camera -> RGB Frame -> Detection -> Encoding -> Matching -> HUD Overlay
```

| Module | Purpose |
|--------|---------|
| `src/dvision/app.py` | Main runtime + CLI |
| `src/dvision/camera.py` | Webcam capture abstraction (swap for Pi later) |
| `src/dvision/recognition.py` | Face embeddings + matching engine |
| `src/dvision/ui.py` | Bounding boxes + name labels in video feed |
| `src/dvision/database.py` | Local JSON embedding storage |
| `src/dvision/config.py` | Centralized configuration constants |

---

## 🛠️ Installation

> Requires Python **3.10+**

```sh
git clone https://github.com/HassanKhan20/D-Vision.git
cd D-Vision

python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate

pip install --upgrade pip
pip install -e .
```

---

## 🚀 Usage

### 🎥 Run Face Recognition

```sh
python -m dvision
```

Press **Q** anytime to exit.

### ➕ Add a Face to the Database

```sh
python -m dvision --add-face --name "Hassan"
```

A face is saved as soon as it detects one.

### 📷 Choose Webcam Device

```sh
python -m dvision --camera-index 1
```

---

## 🗂️ Face Database Format

The file `face_db.json` updates automatically:

```json
[
  {
    "name": "Hassan",
    "embedding": [0.12, -0.03, ...],
    "relation": "Self",
    "last_seen": "2024-01-15T10:30",
    "seen_count": 5
  }
]
```

Runs offline — your identity stays on-device 🔒

---

## 🔧 Development

### Install Dev Dependencies

```sh
pip install -e ".[dev]"
```

### Run Linting

```sh
ruff check src/
```

### Type Checking

```sh
mypy src/dvision/
```

---

## 🍓 Raspberry Pi Zero 2 W

For deployment on Pi, adjust settings in `src/dvision/config.py`:

```python
# Lower resolution for performance
DEFAULT_FRAME_WIDTH = 320
CAMERA_FPS = 30
```

Install Pi-specific dependencies:

```sh
pip install -e ".[pi]"
```

---

## 📜 License

MIT
