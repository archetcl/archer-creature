from __future__ import annotations

import random
import sys
import time

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .achievements import AchievementTracker
from .config import APP_NAME, DEFAULT_MODEL
from .creature_widget import CreatureWidget
from .memory_store import MemoryStore
from .ollama_client import OllamaClient
from .personality import PersonalityEngine
from .settings_manager import SettingsManager
from .statistics import StatisticsTracker
from .system_monitor import SystemMonitor
from .voice_manager import VoiceManager


class FirstRunWizard(QDialog):
    def __init__(self, settings: SettingsManager, ollama: OllamaClient):
        super().__init__()
        self.settings = settings
        self.ollama = ollama
        self.setWindowTitle(APP_NAME)
        self.resize(420, 320)
        self.model_box = QComboBox()
        self.personality_box = QComboBox()
        self.personality_box.addItems(["FRIENDLY", "CHAOTIC", "SARCASTIC", "ROBOT", "GAMER", "HELPER", "ANNOYING", "RANDOM"])
        self.chaos_slider = QSlider(Qt.Horizontal)
        self.chaos_slider.setRange(0, 100)
        self.chaos_slider.setValue(int(self.settings.get("chaos_level", 25)))
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Hey. Apparently I'm living here now."))
        form = QFormLayout()
        form.addRow("Ollama model", self.model_box)
        form.addRow("Personality", self.personality_box)
        form.addRow("Chaos level", self.chaos_slider)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._populate_models()

    def _populate_models(self):
        models = self.ollama.list_models()
        if not models:
            models = [self.settings.get("ai_model", DEFAULT_MODEL)]
        self.model_box.clear()
        self.model_box.addItems(models)
        current = self.settings.get("ai_model", DEFAULT_MODEL)
        idx = self.model_box.findText(current)
        if idx >= 0:
            self.model_box.setCurrentIndex(idx)

    def selected_values(self):
        return {
            "ai_model": self.model_box.currentText(),
            "personality": self.personality_box.currentText(),
            "chaos_level": self.chaos_slider.value(),
        }


class MemoryDialog(QDialog):
    def __init__(self, memory_store: MemoryStore):
        super().__init__()
        self.memory_store = memory_store
        self.setWindowTitle("Memory")
        self.resize(540, 420)
        layout = QVBoxLayout(self)
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search memories")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.refresh)
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_button)
        layout.addLayout(search_row)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
        self.refresh()

    def refresh(self):
        query = self.search_input.text().strip()
        self.list_widget.clear()
        for entry in self.memory_store.search(query):
            item = QListWidgetItem(f"[{entry.created_at}] {entry.text} (importance {entry.importance})")
            item.setData(99, entry)
            self.list_widget.addItem(item)


class SettingsDialog(QDialog):
    def __init__(self, settings: SettingsManager, ollama_client: OllamaClient):
        super().__init__()
        self.settings = settings
        self.ollama_client = ollama_client
        self.setWindowTitle("Settings")
        self.resize(460, 420)
        self.model_box = QComboBox()
        models = self.ollama_client.list_models() or [self.settings.get("ai_model", DEFAULT_MODEL)]
        self.model_box.addItems(models)
        self.model_box.setCurrentText(self.settings.get("ai_model", DEFAULT_MODEL))

        self.personality_box = QComboBox()
        self.personality_box.addItems(["FRIENDLY", "CHAOTIC", "SARCASTIC", "ROBOT", "GAMER", "HELPER", "ANNOYING", "RANDOM", "AUTO"])
        self.personality_box.setCurrentText(self.settings.get("personality", "FRIENDLY"))

        self.chaos_slider = QSlider(Qt.Horizontal)
        self.chaos_slider.setRange(0, 100)
        self.chaos_slider.setValue(int(self.settings.get("chaos_level", 25)))

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.settings.get("voice_volume", 75)))

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow("AI Model", self.model_box)
        form.addRow("Personality", self.personality_box)
        form.addRow("Chaos Level", self.chaos_slider)
        form.addRow("Voice Volume", self.volume_slider)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_changes)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save_changes(self):
        self.settings.set("ai_model", self.model_box.currentText())
        self.settings.set("personality", self.personality_box.currentText())
        self.settings.set("chaos_level", self.chaos_slider.value())
        self.settings.set("voice_volume", self.volume_slider.value())
        self.accept()


class CreatureWindow(QMainWindow):
    def __init__(self, settings, monitor, memory_store, ollama, personality, voice, stats, achievements):
        super().__init__()
        self.settings = settings
        self.monitor = monitor
        self.memory_store = memory_store
        self.ollama = ollama
        self.personality = personality
        self.voice = voice
        self.stats = stats
        self.achievements = achievements
        self.current_mood = "curious"
        self.last_interaction = time.time()

        self.central = QWidget(self)
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.creature = CreatureWidget(self.settings, self.personality, self.monitor, self.memory_store)
        self.layout.addWidget(self.creature)

        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setVisible(False)
        self.chat_log.setMaximumHeight(180)
        self.layout.addWidget(self.chat_log)

        self.status_label = QLabel("ARCHER CREATURE")
        self.status_label.setVisible(False)
        self.layout.addWidget(self.status_label)

        self.model_status = QLabel("Model unknown")
        self.model_status.setVisible(False)
        self.layout.addWidget(self.model_status)

        self._setup_quick_actions()
        self._apply_window_style()
        self._bind_timers()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def _apply_window_style(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(int(self.settings.get("creature_size", 220)), int(self.settings.get("creature_size", 220)))
        self.move(self._default_position())

    def _default_position(self):
        screen = self.screen().availableSize()
        size = int(self.settings.get("creature_size", 220))
        x = max(0, screen.width() - size - 30)
        y = max(0, screen.height() - size - 60)
        return x, y

    def _setup_quick_actions(self):
        self.quick_action_names = ["Chat", "Talk", "Memory", "Personality", "Mood", "Settings", "Hide", "Sleep", "Exit"]
        self.buttons = []
        for name in self.quick_action_names:
            button = QPushButton(name)
            button.setVisible(False)
            self.layout.addWidget(button)
            self.buttons.append(button)

        self.buttons[0].clicked.connect(self.toggle_chat)
        self.buttons[1].clicked.connect(self.talk_now)
        self.buttons[2].clicked.connect(self.open_memory)
        self.buttons[3].clicked.connect(self.cycle_personality)
        self.buttons[4].clicked.connect(self.change_mood)
        self.buttons[5].clicked.connect(self.open_settings)
        self.buttons[6].clicked.connect(self.hide_widget)
        self.buttons[7].clicked.connect(self.sleep_widget)
        self.buttons[8].clicked.connect(self.close)

    def _bind_timers(self):
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self.on_tick)
        self.tick_timer.start(5000)

    def toggle_chat(self):
        visible = not self.chat_log.isVisible()
        self.chat_log.setVisible(visible)
        self.status_label.setVisible(visible)

    def show_context_menu(self, pos):
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.addAction("Chat", self.toggle_chat)
        menu.addAction("Talk", self.talk_now)
        menu.addAction("Memory", self.open_memory)
        menu.addAction("Personality", self.cycle_personality)
        menu.addAction("Mood", self.change_mood)
        menu.addAction("Settings", self.open_settings)
        menu.addAction("Hide", self.hide_widget)
        menu.addAction("Sleep", self.sleep_widget)
        menu.addAction("Exit", self.close)
        menu.exec(self.mapToGlobal(pos))

    def hide_widget(self):
        self.hide()

    def sleep_widget(self):
        self.creature.set_expression("sleepy")
        self.current_mood = "sleepy"
        self.creature.set_mood(self.current_mood)
        self.status_label.setText("Sleeping...")

    def talk_now(self):
        self.creature.set_expression("talking")
        prompt = "Tell me something useful and brief."
        response = self._ask_creature(prompt)
        self.chat_log.append(f"You: {prompt}\nCreature: {response}\n")

    def open_memory(self):
        dialog = MemoryDialog(self.memory_store)
        dialog.exec()

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self.ollama)
        if dialog.exec() == QDialog.Accepted:
            self.settings.set("ai_model", self.settings.get("ai_model", DEFAULT_MODEL))
            self.ollama.set_model(self.settings.get("ai_model", DEFAULT_MODEL))
            self.personality.set_personality(self.settings.get("personality", "FRIENDLY"))
            self.voice.volume = int(self.settings.get("voice_volume", 75))

    def cycle_personality(self):
        personalities = ["FRIENDLY", "CHAOTIC", "SARCASTIC", "ROBOT", "GAMER", "HELPER", "ANNOYING", "RANDOM"]
        current = self.settings.get("personality", "FRIENDLY")
        index = personalities.index(current) if current in personalities else 0
        new_personality = personalities[(index + 1) % len(personalities)]
        self.settings.set("personality", new_personality)
        self.personality.set_personality(new_personality)
        self.status_label.setText(f"Personality: {new_personality}")

    def change_mood(self):
        moods = ["happy", "excited", "bored", "sleepy", "curious", "angry", "confused", "mischievous", "focused"]
        old = self.current_mood if self.current_mood in moods else "curious"
        index = moods.index(old)
        self.current_mood = moods[(index + 1) % len(moods)]
        self.creature.set_mood(self.current_mood)
        self.status_label.setText(f"Mood: {self.current_mood}")

    def _ask_creature(self, prompt: str) -> str:
        self.stats.record_message()
        self.last_interaction = time.time()
        if not self.ollama.healthcheck():
            self.status_label.setText("Ollama is offline.")
            return "Ollama is offline."

        system_prompt = self.personality.build_system_prompt(
            self.current_mood,
            {
                "foreground_app": self.monitor.get_foreground_app(),
                "cpu_usage": self.monitor.snapshot().get("cpu_usage", 0),
                "ram_usage": self.monitor.snapshot().get("ram_usage", 0),
            },
        )
        try:
            answer = self.ollama.chat(prompt, system_prompt=system_prompt)
            return answer
        except Exception:
            return "Ollama is offline."

    def on_tick(self):
        snapshot = self.monitor.snapshot()
        mood = self._derive_mood(snapshot)
        self.current_mood = mood
        self.creature.set_mood(mood)
        self.stats.record_mood(mood)

        if snapshot.get("cpu_usage", 0) > 85:
            self.creature.set_expression("angry")
        elif snapshot.get("ram_usage", 0) > 80:
            self.creature.set_expression("confused")
        elif snapshot.get("idle_seconds", 0) > 300:
            self.creature.set_expression("sleepy")
        else:
            self.creature.set_expression("idle")

        self.model_status.setText(f"AI Model: {self.settings.get('ai_model', DEFAULT_MODEL)}")
        self.model_status.setVisible(True)

    def _derive_mood(self, snapshot):
        idle = snapshot.get("idle_seconds", 0)
        cpu = snapshot.get("cpu_usage", 0)
        ram = snapshot.get("ram_usage", 0)
        if idle > 600:
            return "sleepy"
        if cpu > 90:
            return "angry"
        if ram > 80:
            return "confused"
        if random.random() < 0.12:
            return "mischievous"
        return "curious"


class ArcherCreatureApp:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.settings = SettingsManager()
        self.memory_store = MemoryStore()
        self.ollama = OllamaClient(model=self.settings.get("ai_model", DEFAULT_MODEL))
        self.monitor = SystemMonitor(interval_seconds=5)
        self.personality = PersonalityEngine(self.settings.get("personality", "FRIENDLY"))
        self.voice = VoiceManager(voice_name=self.settings.get("voice_name", ""), volume=int(self.settings.get("voice_volume", 75)))
        self.stats = StatisticsTracker()
        self.achievements = AchievementTracker()
        self.window = CreatureWindow(
            self.settings,
            self.monitor,
            self.memory_store,
            self.ollama,
            self.personality,
            self.voice,
            self.stats,
            self.achievements,
        )

    def run(self):
        if self.settings.get("first_run", True):
            wizard = FirstRunWizard(self.settings, self.ollama)
            if wizard.exec() == QDialog.Accepted:
                values = wizard.selected_values()
                self.settings.update(values)
                self.settings.set("first_run", False)
                self.ollama.set_model(values["ai_model"])
                self.personality.set_personality(values["personality"])
                self.window.show()
            else:
                self.settings.set("first_run", False)
                self.window.show()
        else:
            self.window.show()

        self.window.model_status.setText(f"AI Model: {self.settings.get('ai_model', DEFAULT_MODEL)}")
        self.window.model_status.setVisible(True)
        sys.exit(self.app.exec())
