from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "ARCHER CREATURE"
APP_VERSION = "0.1.0"
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("ARCHER_CREATURE_DATA_DIR", ROOT_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS_PATH = DATA_DIR / "settings.json"
MEMORY_PATH = DATA_DIR / "memory.json"
STATISTICS_PATH = DATA_DIR / "statistics.json"
ACHIEVEMENTS_PATH = DATA_DIR / "achievements.json"
DEFAULT_MODEL = "qwen3:4b"
DEFAULT_PERSONALITY = "FRIENDLY"
DEFAULT_CHAOS_LEVEL = 25

if os.name == "nt":
    USER_DATA_DIR = Path.home() / "AppData" / "Local" / "ARCHER_CREATURE"
else:
    USER_DATA_DIR = Path.home() / ".archer_creature"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
