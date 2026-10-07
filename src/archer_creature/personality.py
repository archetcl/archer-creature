from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .config import MEMORY_PATH


@dataclass
class MemoryEntry:
    id: str
    text: str
    created_at: str
    importance: float
    source: str = "user"
    tags: list[str] = field(default_factory=list)


class MemoryStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else MEMORY_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._memory: list[MemoryEntry] = []
        self.load()

    def load(self) -> list[MemoryEntry]:
        if not self.path.exists():
            self._memory = []
            self.save()
            return self._memory

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._memory = [MemoryEntry(**item) for item in data]
        except Exception:
            self._memory = []
            self.save()
        return self._memory

    def save(self) -> None:
        payload = [asdict(entry) for entry in self._memory]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add_memory(self, text: str, importance: float = 1.0, source: str = "user") -> MemoryEntry:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Memory text cannot be empty.")
        entry = MemoryEntry(
            id=f"mem-{int(datetime.now(timezone.utc).timestamp() * 1000)}",
            text=cleaned,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            importance=max(0.0, min(5.0, float(importance))),
            source=source,
            tags=self._extract_tags(cleaned),
        )
        self._memory.insert(0, entry)
        self.save()
        return entry

    def list_memories(self) -> list[MemoryEntry]:
        return sorted(self._memory, key=lambda item: item.importance, reverse=True)

    def search(self, query: str) -> list[MemoryEntry]:
        if not query:
            return self.list_memories()
        q = query.lower().strip()
        matches = []
        for entry in self._memory:
            haystack = f"{entry.text} {' '.join(entry.tags)}".lower()
            if q in haystack:
                matches.append(entry)
        return matches

    def delete(self, memory_id: str) -> bool:
        before = len(self._memory)
        self._memory = [entry for entry in self._memory if entry.id != memory_id]
        if len(self._memory) != before:
            self.save()
            return True
        return False

    def clear(self) -> None:
        self._memory = []
        self.save()

    @staticmethod
    def _extract_tags(text: str) -> list[str]:
        words = [token.strip(".,!?;:\"'[](){}") for token in text.split() if token]
        normalized = [word.lower() for word in words if len(word) > 3]
        return normalized[:8]
