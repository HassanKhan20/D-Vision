import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np


@dataclass
class PersonMatch:
    name: str | None
    confidence: float


class FaceDatabase:
    """Simple JSON-backed database for known people and embeddings."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.people: List[dict] = []

    def load(self) -> None:
        if not self.path.exists():
            self.people = []
            return
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.people = data.get("people", [])

    def save(self) -> None:
        payload = {"people": self.people}
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add_embedding(self, name: str, embedding: np.ndarray) -> None:
        serialized = embedding.tolist()
        self.people.append({"name": name, "embedding": serialized})

    def get_all_embeddings(self) -> Tuple[List[np.ndarray], List[str]]:
        embeddings = []
        names = []
        for person in self.people:
            embeddings.append(np.asarray(person["embedding"]))
            names.append(person["name"])
        return embeddings, names
