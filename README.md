<h1 align="center">🕶️ D-Vision — AI-Powered Smart Glasses</h1>

<p align="center">
Real-time face detection & recognition for wearable heads-up displays
<br>
Powered by OpenCV · MediaPipe · Face Recognition (dlib)
</p>

---

## 🎯 Mission

Bring personal AI assistance into the real world — starting with **smart glasses that recognize who you’re looking at** and instantly show helpful context.

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



Camera -> RGB Frame -> Detection -> Encoding -> Matching -> HUD Overlay


| Module | Purpose |
|--------|---------|
| `app.py` | Main runtime + CLI |
| `camera.py` | Webcam capture abstraction (swap for Pi later) |
| `recognition.py` | Face embeddings + matching engine |
| `ui.py` | Bounding boxes + name labels in video feed |
| `database.py` | Local JSON embedding storage |
| `requirements.txt` | Python dependencies |

---

## 🛠️ Installation

> Requires Python **3.10+**

```sh
git clone https://github.com/HassanKhan20/D-Vision.git
cd D-Vision

python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

🚀 Usage
🎥 Run Face Recognition
python app.py


Press Q anytime to exit.

➕ Add a Face to the Database
python app.py --add_face --name "Hassan"


A face is saved as soon as it detects one.

📷 Choose Webcam Device
python app.py --camera-index 1

🗂️ Face Database Format

The file updates automatically:

{
  "people": [
    {
      "name": "Hassan",
      "embedding": [0.12, -0.03, ...]
    }
  ]
}


Runs offline — your identity stays on-device 🔒
