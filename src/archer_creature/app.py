from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .config import DEFAULT_CHAOS_LEVEL, DEFAULT_MODEL, DEFAULT_PERSONALITY, SETTINGS_PATH


class SettingsManager:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else SETTINGS_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.settings: dict[str, Any] = self._defaults()
        self.load()

    def _defaults(self) -> dict[str, Any]:
        return {
            "first_run": True,
            "ai_model": DEFAULT_MODEL,
            "personality": DEFAULT_PERSONALITY,
            "chaos_level": DEFAULT_CHAOS_LEVEL,
            "voice_enabled": True,
            "voice_name": "",
            "voice_volume": 75,
            "microphone_index": 0,
            "always_on_top": True,
            "start_with_windows": False,
            "animations_enabled": True,
            "application_monitoring": True,
            "computer_monitoring": True,
            "random_events": True,
            "notifications": True,
            "memory_enabled": True,
            "transparency": 85,
            "creature_size": 220,
            "position_x": 0,
            "position_y": 0,
            "theme": "neon_dark",
            "auto_personality": True,
            "voice_language": "en-US",
            "model_status": "unknown",
        }

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            self.settings = self._defaults()
            self.save()
            return self.settings

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            merged = self._defaults()
            merged.update(raw)
            self.settings = merged
        except Exception:
            self.settings = self._defaults()
            self.save()
        return self.settings

    def save(self) -> None:
        self.path.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save()

    def update(self, values: dict[str, Any]) -> None:
        self.settings.update(values)
        self.save()

    def as_dict(self) -> dict[str, Any]:
        return deepcopy(self.settings)
