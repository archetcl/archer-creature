# ARCHER CREATURE

ARCHER CREATURE is a local Windows desktop AI companion that lives in the corner of the screen, reacts to your computer, remembers what you tell it, and speaks through local Ollama + optional Windows speech tooling.

## Why this stack

This project uses Python + PySide6 because it gives the most practical Windows-native desktop experience for a compact floating widget:

- transparent/frameless desktop overlay
- smooth animations and custom rendering
- local Ollama integration without cloud API keys
- low-overhead system monitoring
- local speech synthesis + microphone support
- resilient, local-first architecture

## Project structure

```text
ARCHER-CREATURE/
├── README.md
├── requirements.txt
├── main.py
├── .gitignore
├── src/
│   └── archer_creature/
│       ├── __init__.py
│       ├── app.py
│       ├── achievements.py
│       ├── config.py
│       ├── creature_widget.py
│       ├── memory_store.py
│       ├── mood.py
│       ├── ollama_client.py
│       ├── personality.py
│       ├── settings_manager.py
│       ├── statistics.py
│       ├── system_monitor.py
│       └── voice_manager.py
├── data/
│   └── .gitkeep
├── assets/
│   └── .gitkeep
├── tests/
│   └── test_memory_store.py
└── .venv/
```

## Install

From PowerShell in the project root:

```powershell
cd archer-creature
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install and run Ollama locally:

```powershell
ollama serve
ollama pull qwen3:4b
```

Then launch:

```powershell
python main.py
```

## Features

- animated creature widget in the desktop corner
- mood and personality engine
- local Ollama model detection and selection
- memory store with search and delete
- CPU/RAM/idle/app monitoring
- speech and TTS support with graceful offline handling
- settings, achievements, statistics, chaos, and random events
- Windows startup option and always-on-top behavior

## Notes

- The project is designed for Windows, but it retains a local-first architecture and degrades gracefully when optional components are unavailable.
- It does not upload microphone recordings, passwords, keystrokes, or screen contents anywhere.
- If Ollama is offline, the app shows a clear offline warning and does not crash.

## License

Local-use desktop software for personal machine companionship.
