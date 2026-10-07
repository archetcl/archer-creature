from __future__ import annotations

import threading
from typing import Any

try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None

try:
    import SpeechRecognition as sr
except Exception:  # pragma: no cover
    sr = None


class VoiceManager:
    def __init__(self, voice_name: str | None = None, volume: int = 75):
        self.voice_name = voice_name or ""
        self.volume = max(0, min(100, volume))
        self._tts_engine: Any = None
        self._active = False

    def available(self) -> bool:
        return pyttsx3 is not None or sr is not None

    def speak(self, text: str, volume: int | None = None) -> bool:
        if not text:
            return False
        if pyttsx3 is not None:
            self._tts_engine = pyttsx3.init()
            if volume is not None:
                self.volume = max(0, min(100, volume))
            self._tts_engine.setProperty("volume", self.volume / 100.0)
            if self.voice_name:
                for voice in self._tts_engine.getProperty("voices"):
                    if self.voice_name.lower() in voice.name.lower():
                        self._tts_engine.setProperty("voice", voice.id)
                        break
            self._tts_engine.say(text)
            self._tts_engine.runAndWait()
            return True
        return False

    def listen_once(self, timeout: int = 10) -> str:
        if sr is None:
            return ""

        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=timeout)
            try:
                return recognizer.recognize_google(audio)
            except Exception:
                try:
                    return recognizer.recognize_sphinx(audio)
                except Exception:
                    return ""
        except Exception:
            return ""

    def listen_async(self, callback, timeout: int = 10) -> None:
        def worker() -> None:
            result = self.listen_once(timeout=timeout)
            callback(result if result else "")

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def stop(self) -> None:
        self._active = False
