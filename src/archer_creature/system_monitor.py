from __future__ import annotations

import json
import time
from typing import Any

import requests

from .config import DEFAULT_MODEL


class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = DEFAULT_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.last_error: str | None = None
        self.last_response_time = 0.0

    def healthcheck(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.ok
        except Exception as exc:
            self.last_error = str(exc)
            return False

    def list_models(self) -> list[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            payload = response.json()
            names = []
            for model in payload.get("models", []):
                name = model.get("name") or model.get("model")
                if name:
                    names.append(name)
            return sorted(set(names))
        except Exception as exc:
            self.last_error = str(exc)
            return []

    def set_model(self, model: str) -> None:
        self.model = model

    def chat(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.7) -> str:
        if not self.model:
            raise ValueError("No Ollama model selected.")

        start = time.perf_counter()
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "options": {"temperature": temperature},
            "stream": False,
        }
        if system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": system_prompt})

        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=45)
            if not response.ok:
                self.last_error = response.text
                raise RuntimeError(f"Ollama request failed: {response.status_code}")
            data = response.json()
            message = data.get("message", {}).get("content", "")
            if not message:
                return "Ollama responded without text."
            return message.strip()
        except Exception as exc:
            self.last_error = str(exc)
            raise
        finally:
            self.last_response_time = time.perf_counter() - start

    @property
    def response_time(self) -> float:
        return self.last_response_time

    def build_chat_payload(self, system_prompt: str, user_message: str, extra_context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = extra_context or {}
        if context:
            user_message = f"{user_message}\n\nContext:\n{json.dumps(context, indent=2)}"
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
        }
