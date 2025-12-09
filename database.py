import json
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
from scipy.spatial.distance import cosine


class Person:
    def __init__(self, name, embedding, relation="", last_seen=None, seen_count=0):
        self.name = name
        self.embedding = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        self.relation = relation
        self.last_seen = last_seen
        self.seen_count = seen_count

    def to_dict(self):
        return {
            "name": self.name,
            "embedding": self.embedding,
            "relation": self.relation,
            "last_seen": self.last_seen,
            "seen_count": self.seen_count,
        }

    @staticmethod
    def from_dict(data):
        return Person(
            data["name"],
            np.array(data["embedding"], dtype="float32"),
            data.get("relation", ""),
            data.get("last_seen", None),
            data.get("seen_count", 0),
        )


class FaceDatabase:
    def __init__(self, path: Path):
        self.path = path
        self.people = []

    def load(self):
        if self.path.exists():
            with open(self.path, "r") as f:
                data = json.load(f)
                self.people = [Person.from_dict(p) for p in data]

    def save(self):
        with open(self.path, "w") as f:
            json.dump([p.to_dict() for p in self.people], f, indent=2)

    def add_embedding(self, name, embedding, relation=""):
        emb = np.array(embedding, dtype="float32")
        self.people.append(Person(name, emb, relation))

    def lookup(self, encoding, tolerance=0.91):
        if not self.people:
            return None, 0.0

        best_person = None
        best_conf = 0.0
        encoding = np.array(encoding, dtype="float32")

        for person in self.people:
            stored = np.array(person.embedding, dtype="float32")
            conf = max(0.0, 1.0 - cosine(encoding, stored))

            if conf > best_conf:
                best_conf = round(conf, 2)
                best_person = person

        if best_person and best_conf >= tolerance:
            now = datetime.now()
            if not best_person.last_seen:
                best_person.seen_count += 1
            else:
                last = datetime.fromisoformat(best_person.last_seen)
                if now - last > timedelta(seconds=60):
                    best_person.seen_count += 1

            best_person.last_seen = now.isoformat(timespec="minutes")
            return best_person, best_conf

        return None, best_conf
