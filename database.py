import json
import numpy as np
from pathlib import Path
import face_recognition


class Person:
    def __init__(self, name: str, embedding: np.ndarray):
        self.name = name
        self.embedding = embedding.tolist()

    def to_dict(self):
        return {"name": self.name, "embedding": self.embedding}

    @staticmethod
    def from_dict(data):
        return Person(data["name"], np.array(data["embedding"]))


class FaceDatabase:
    def __init__(self, path: Path):
        self.path = path
        self.people = []  # List[Person]

    def load(self):
        if self.path.exists():
            with open(self.path, "r") as f:
                data = json.load(f)
                self.people = [Person.from_dict(p) for p in data]

    def save(self):
        with open(self.path, "w") as f:
            json.dump([p.to_dict() for p in self.people], f, indent=2)

    def add_embedding(self, name: str, embedding):
        """Add a new face embedding to DB."""
        self.people.append(Person(name, embedding))

    def lookup(self, embedding, threshold=0.6):
        """Find best match using face distance."""
        if not self.people:
            return None, 0.0

        known_encodings = [np.array(p.embedding) for p in self.people]
        distances = face_recognition.face_distance(known_encodings, embedding)

        best_idx = np.argmin(distances)
        best_dist = distances[best_idx]

        if best_dist < threshold:
            confidence = 1.0 - best_dist
            return self.people[best_idx], round(confidence, 2)

        return None, 0.0
