"""
Database module for D-Vision.

Provides persistent storage for face embeddings and person metadata.
Uses JSON for simplicity and portability on resource-constrained devices.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Any

import numpy as np
from scipy.spatial.distance import cdist

from .config import RECOGNITION_TOLERANCE, SEEN_COOLDOWN_SECONDS

logger = logging.getLogger("D-Vision")


class Person:
    """
    Represents a person in the face database.
    
    Attributes:
        name: Person's name for display.
        embedding: 128-dimensional face encoding vector.
        relation: Relationship to the user (e.g., "Mother", "Doctor").
        last_seen: ISO timestamp of last recognition.
        seen_count: Number of times this person has been recognized.
    """

    def __init__(
        self,
        name: str,
        embedding: Any,
        relation: str = "",
        last_seen: Optional[str] = None,
        seen_count: int = 0,
    ) -> None:
        self.name = name
        self.embedding: List[float] = (
            embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        )
        self.relation = relation
        self.last_seen = last_seen
        self.seen_count = seen_count

    def to_dict(self) -> dict:
        """Serialize person to dictionary for JSON storage."""
        return {
            "name": self.name,
            "embedding": self.embedding,
            "relation": self.relation,
            "last_seen": self.last_seen,
            "seen_count": self.seen_count,
        }

    @staticmethod
    def from_dict(data: dict) -> "Person":
        """Deserialize person from dictionary."""
        return Person(
            name=data["name"],
            embedding=np.array(data["embedding"], dtype="float32"),
            relation=data.get("relation", ""),
            last_seen=data.get("last_seen"),
            seen_count=data.get("seen_count", 0),
        )


class FaceDatabase:
    """
    JSON-based face embedding database.
    
    Stores face encodings and metadata for recognized individuals.
    Designed for portability and offline operation.
    
    Attributes:
        path: Path to the JSON database file.
        people: List of Person objects in the database.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.people: List[Person] = []
        self._embedding_matrix: Optional[np.ndarray] = None  # Pre-computed for fast matching

    def load(self) -> None:
        """Load database from disk. Creates empty list if file doesn't exist."""
        if not self.path.exists():
            self.people = []
            self._rebuild_embedding_matrix()
            return
            
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.people = [Person.from_dict(p) for p in data]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to load database: %s", e)
            self.people = []
        
        self._rebuild_embedding_matrix()

    def _rebuild_embedding_matrix(self) -> None:
        """Pre-compute embedding matrix for vectorized matching."""
        if self.people:
            self._embedding_matrix = np.array(
                [p.embedding for p in self.people], dtype="float32"
            )
        else:
            self._embedding_matrix = None

    def save(self) -> None:
        """Persist database to disk."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.people], f, indent=2)

    def add_embedding(
        self, name: str, embedding: np.ndarray, relation: str = ""
    ) -> None:
        """Add a new person to the database."""
        emb = np.array(embedding, dtype="float32")
        self.people.append(Person(name, emb, relation))
        self._rebuild_embedding_matrix()  # Keep matrix in sync

    def lookup(
        self, encoding: np.ndarray, tolerance: float = RECOGNITION_TOLERANCE
    ) -> Tuple[Optional[Person], float]:
        """
        Find the best matching person for a face encoding.
        
        Uses vectorized cosine similarity (cdist) for O(1) batch matching
        instead of O(n) loop. Significant speedup for large databases.
        
        Args:
            encoding: 128-dimensional face encoding to match.
            tolerance: Minimum confidence threshold (default from config).
            
        Returns:
            Tuple of (matched Person or None, confidence score).
        """
        if self._embedding_matrix is None or len(self.people) == 0:
            return None, 0.0

        # Vectorized cosine similarity: 1 - cdist gives similarity
        encoding = np.array(encoding, dtype="float32").reshape(1, -1)
        distances = cdist(encoding, self._embedding_matrix, metric="cosine")[0]
        similarities = np.maximum(0.0, 1.0 - distances)
        
        best_idx = int(np.argmax(similarities))
        best_conf = round(float(similarities[best_idx]), 2)
        best_person = self.people[best_idx]

        if best_conf >= tolerance:
            now = datetime.now()
            
            # Update seen count with cooldown to prevent spam
            if best_person.last_seen is None:
                best_person.seen_count += 1
            else:
                last = datetime.fromisoformat(best_person.last_seen)
                if now - last > timedelta(seconds=SEEN_COOLDOWN_SECONDS):
                    best_person.seen_count += 1

            best_person.last_seen = now.isoformat(timespec="minutes")
            return best_person, best_conf

        return None, best_conf

