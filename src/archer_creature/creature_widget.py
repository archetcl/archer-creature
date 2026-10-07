from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MoodState:
    label: str = "curious"
    intensity: float = 0.5


def mood_from_metrics(cpu: float, ram: float, idle_seconds: float) -> MoodState:
    if idle_seconds > 600:
        return MoodState("sleepy", 1.0)
    if cpu > 90:
        return MoodState("angry", 1.0)
    if ram > 80:
        return MoodState("confused", 0.8)
    if cpu > 60:
        return MoodState("focused", 0.7)
    return MoodState("curious", 0.5)
