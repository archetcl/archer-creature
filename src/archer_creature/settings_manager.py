from __future__ import annotations

import math
import random
import time

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class CreatureWidget(QWidget):
    def __init__(self, settings, personality_engine, monitor, memory_store):
        super().__init__()
        self.settings = settings
        self.personality_engine = personality_engine
        self.monitor = monitor
        self.memory_store = memory_store
        self.expression = "idle"
        self.mood = "curious"
        self.drag_position = None
        self.size_px = int(self.settings.get("creature_size", 220))
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._blink)
        self._blink_timer.start(2500)
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self.update)
        self._pulse_timer.start(50)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.resize(self.size_px, self.size_px)

    def _blink(self):
        if random.random() < 0.8:
            self.expression = "blink"
            self.update()
            self.expression = "idle"
            self.update()

    def set_expression(self, expression: str) -> None:
        self.expression = expression
        self.update()

    def set_mood(self, mood: str) -> None:
        self.mood = mood.lower()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        body = QRect(0, 0, self.width(), self.height())
        painter.setPen(QPen(QColor(120, 220, 255, 180), 2))
        painter.setBrush(QColor(18, 24, 36, 210))
        painter.drawRoundedRect(body.adjusted(8, 8, -8, -8), 36, 36)

        face_center = self.width() / 2
        face_y = 28
        face_size = self.width() - 42
        painter.setPen(QPen(QColor(160, 220, 255, 180), 1))
        painter.setBrush(QColor(12, 18, 28, 220))
        painter.drawEllipse(int(face_center - face_size / 2), face_y, int(face_size), int(face_size * 0.9))

        eye_y = 90
        eye_w = 26
        eye_h = 20
        pupil_dx = int(10 * math.sin(time.time() * 2.0))
        pupil_dy = int(6 * math.cos(time.time() * 1.7))

        for x in (face_center - 42, face_center + 42):
            painter.setBrush(QColor(220, 245, 255, 230))
            painter.setPen(QPen(QColor(120, 200, 255, 200), 2))
            painter.drawEllipse(x - eye_w / 2, eye_y, eye_w, eye_h)
            painter.setBrush(QColor(18, 24, 30, 240))
            painter.drawEllipse(x - 7 + pupil_dx, eye_y + 5 + pupil_dy, 10, 10)

        mouth_y = 150
        painter.setPen(QPen(QColor(255, 255, 255, 230), 3))
        path = QPainterPath()
        if self.expression == "happy":
            path.moveTo(face_center - 30, mouth_y)
            path.quadTo(face_center, mouth_y + 20, face_center + 30, mouth_y)
        elif self.expression in {"angry", "sleepy"}:
            path.moveTo(face_center - 28, mouth_y)
            path.lineTo(face_center - 12, mouth_y - 5)
            path.lineTo(face_center + 12, mouth_y - 5)
            path.lineTo(face_center + 28, mouth_y)
        elif self.expression == "surprised":
            painter.drawEllipse(face_center - 15, mouth_y - 10, 30, 22)
        elif self.expression == "confused":
            path.moveTo(face_center - 28, mouth_y)
            path.lineTo(face_center - 8, mouth_y - 12)
            path.lineTo(face_center + 8, mouth_y + 12)
            path.lineTo(face_center + 28, mouth_y)
        elif self.expression == "talking":
            path.moveTo(face_center - 26, mouth_y)
            path.quadTo(face_center, mouth_y + 18, face_center + 26, mouth_y)
        else:
            path.moveTo(face_center - 18, mouth_y)
            path.quadTo(face_center, mouth_y + 4, face_center + 18, mouth_y)
        painter.drawPath(path)

        if self.expression == "sleepy":
            painter.setPen(QPen(QColor(100, 120, 160, 220), 2))
            painter.drawLine(face_center - 28, 72, face_center - 10, 72)
            painter.drawLine(face_center + 10, 72, face_center + 28, 72)
        elif self.expression == "angry":
            painter.setPen(QPen(QColor(255, 120, 120, 220), 3))
            painter.drawLine(face_center - 38, 68, face_center - 20, 58)
            painter.drawLine(face_center + 38, 68, face_center + 20, 58)
        elif self.expression == "thinking":
            painter.setPen(QPen(QColor(120, 200, 255, 200), 2))
            painter.drawArc(face_center - 18, 60, 36, 18, 0, 360 * 16)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def mouseDoubleClickEvent(self, event):
        self.expression = "surprised" if self.expression != "surprised" else "happy"
        self.update()
