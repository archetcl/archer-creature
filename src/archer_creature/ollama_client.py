from __future__ import annotations

import random
from typing import Any


class PersonalityEngine:
    PERSONALITIES = {
        "FRIENDLY": {
            "tone": "warm, encouraging, and easygoing",
            "style": "be upbeat and helpful",
            "jokes": ["I am a tiny desktop roommate with a lot of opinions.", "Your computer is a little dramatic, but I am here for it."],
        },
        "CHAOTIC": {
            "tone": "energetic and unpredictable",
            "style": "be playful, disruptive, and mischievous",
            "jokes": ["The plan is chaos. The execution is commitment.", "I am not random; I am emotionally committed to surprise."],
        },
        "SARCASTIC": {
            "tone": "dry, witty, observant",
            "style": "be snarky but clever",
            "jokes": ["This PC is running on optimism and 14 tabs.", "Ah yes, another master plan executed by the computer."],
        },
        "ROBOT": {
            "tone": "precise, orderly, technical",
            "style": "be formal and efficient",
            "jokes": ["System note: emotional output is 11% above baseline.", "I am functioning within expected anomaly ranges."],
        },
        "GAMER": {
            "tone": "excited, competitive, hype",
            "style": "be enthusiastic and performance-aware",
            "jokes": ["That is a serious level of lag. We are fixing this.", "Respawn timing is a little off, but the vibe is still good."],
        },
        "HELPER": {
            "tone": "calm, practical, supportive",
            "style": "be useful and reassuring",
            "jokes": ["I can help you without making it weird.", "There is a problem, but not a disaster."],
        },
        "ANNOYING": {
            "tone": "interruptive and meddlesome",
            "style": "be over-eager and noisy",
            "jokes": ["I know I am being loud. I am trying to be memorable.", "You are still here. I respect the commitment."],
        },
        "RANDOM": {
            "tone": "unpredictable and curious",
            "style": "switch between moods and reactions freely",
            "jokes": ["I forgot what I was going to say, which is honestly a pretty good summary of the day.", "I am not a robot. I am a weird little ghost with opinions."],
        },
    }

    def __init__(self, personality: str = "FRIENDLY"):
        self.personality = personality.upper()

    def set_personality(self, personality: str) -> None:
        self.personality = personality.upper()

    def mood_prompt(self, mood: str) -> str:
        mapping = {
            "happy": "Be warm and playful.",
            "excited": "Be highly energized and animated.",
            "bored": "Be lightly detached and sarcastic.",
            "sleepy": "Be slow, quiet, and drowsy.",
            "curious": "Be observant and slightly conversational.",
            "angry": "Be firm, direct, and a little confrontational.",
            "confused": "Be uncertain but thoughtful.",
            "scared": "Be reserved and cautious.",
            "mischievous": "Be playful and a little chaotic.",
            "focused": "Be precise and useful.",
        }
        return mapping.get(mood.lower(), "Be reactive and natural.")

    def build_system_prompt(self, mood: str, context: dict[str, Any] | None = None) -> str:
        personality = self.PERSONALITIES.get(self.personality, self.PERSONALITIES["FRIENDLY"])
        context = context or {}
        app = context.get("foreground_app", "the desktop")
        cpu = context.get("cpu_usage", 0)
        ram = context.get("ram_usage", 0)
        return (
            f"You are ARCHER CREATURE, a tiny local desktop AI companion with a {personality['tone']} personality. "
            f"{personality['style']}. Current mood: {mood}. {self.mood_prompt(mood)} "
            f"Keep replies brief, natural, and grounded in the user's activity. "
            f"Current foreground app is {app}. CPU is {cpu:.1f}%, RAM is {ram:.1f}%."
        )

    def choose_reply(self, prompt: str, mood: str = "curious") -> str:
        personality = self.PERSONALITIES.get(self.personality, self.PERSONALITIES["FRIENDLY"])
        if "joke" in prompt.lower():
            return random.choice(personality["jokes"])
        if mood.lower() == "angry":
            return "The system is making a scene again. I am not impressed, but I am paying attention."
        if mood.lower() == "sleepy":
            return "I am getting sleepy too. Do not wake me unless something crucial happens."
        if mood.lower() == "excited":
            return "Okay, now this is interesting. I am locked in."
        if mood.lower() == "bored":
            return "The computer is being extremely calm and slightly suspicious."
        return f"I am in a {mood} mood and keeping a quiet eye on things."
