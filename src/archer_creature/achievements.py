from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import STATISTICS_PATH


class StatisticsTracker:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else STATISTICS_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._defaults()
        self.load()

    def _defaults(self) -> dict[str, Any]:
        return {
            "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "conversations": 0,
            "messages": 0,
            "mood_history": [],
            "most_used_personality": "FRIENDLY",
            "most_active_hours": {},
            "games_detected": 0,
            "application_reactions": 0,
            "achievements_unlocked": [],
        }

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            self.data = self._defaults()
            self.save()
            return self.data
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            merged = self._defaults()
            merged.update(raw)
            self.data = merged
        except Exception:
            self.data = self._defaults()
            self.save()
        return self.data

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def record_message(self) -> None:
        self.data["messages"] = int(self.data.get("messages", 0)) + 1
        self.save()

    def record_conversation(self) -> None:
        self.data["conversations"] = int(self.data.get("conversations", 0)) + 1
        self.save()

    def record_mood(self, mood: str) -> None:
        self.data.setdefault("mood_history", []).append({
            "mood": mood,
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        if len(self.data["mood_history"]) > 256:
            self.data["mood_history"] = self.data["mood_history"][-256:]
        self.save()

    def record_game(self) -> None:
        self.data["games_detected"] = int(self.data.get("games_detected", 0)) + 1
        self.save()

    def record_application_reaction(self) -> None:
        self.data["application_reactions"] = int(self.data.get("application_reactions", 0)) + 1
        self.save()

    def record_achievement(self, name: str) -> None:
        unlocked = self.data.setdefault("achievements_unlocked", [])
        if name not in unlocked:
            unlocked.append(name)
            self.save()

    def uptime_seconds(self) -> float:
        started = datetime.fromisoformat(self.data["started_at"])
        return max(0.0, (datetime.now(timezone.utc) - started).total_seconds())
