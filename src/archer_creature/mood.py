from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Achievement:
    key: str
    title: str
    description: str
    unlocked: bool = False
    unlocked_at: str | None = None


class AchievementTracker:
    def __init__(self):
        self.achievements: dict[str, Achievement] = {
            "first_chat": Achievement("first_chat", "FIRST CHAT", "Talked to your creature.", False, None),
            "night_owl": Achievement("night_owl", "NIGHT OWL", "Used the creature after midnight.", False, None),
            "chaos": Achievement("chaos", "CHAOS", "Reached maximum chaos.", False, None),
            "friend": Achievement("friend", "FRIEND", "Talked to the creature 100 times.", False, None),
            "gamer": Achievement("gamer", "GAMER", "Detected 10 games.", False, None),
            "marathon": Achievement("marathon", "MARATHON", "Creature has been running for 24 hours.", False, None),
        }

    def evaluate(self, stats: dict[str, object]) -> list[Achievement]:
        if int(stats.get("messages", 0)) >= 1:
            self._unlock("first_chat")
        if int(stats.get("games_detected", 0)) >= 10:
            self._unlock("gamer")
        if int(stats.get("chaos_level", 0)) >= 100:
            self._unlock("chaos")
        if int(stats.get("messages", 0)) >= 100:
            self._unlock("friend")
        return [achievement for achievement in self.achievements.values() if achievement.unlocked]

    def _unlock(self, key: str) -> None:
        achievement = self.achievements.get(key)
        if achievement and not achievement.unlocked:
            achievement.unlocked = True
            achievement.unlocked_at = "now"

    def list_unlocked(self) -> list[Achievement]:
        return [item for item in self.achievements.values() if item.unlocked]
