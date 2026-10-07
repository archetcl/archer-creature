from __future__ import annotations

import subprocess
import sys
import time
from typing import Any

import psutil


class SystemMonitor:
    def __init__(self, interval_seconds: int = 5):
        self.interval_seconds = interval_seconds
        self._snapshot: dict[str, Any] = {}

    def snapshot(self) -> dict[str, Any]:
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        battery = None
        try:
            battery = psutil.sensors_battery()
        except Exception:
            battery = None

        snapshot = {
            "timestamp": time.time(),
            "cpu_usage": float(cpu),
            "ram_usage": float(memory.percent),
            "ram_used_mb": float(memory.used / (1024 * 1024)),
            "ram_total_mb": float(memory.total / (1024 * 1024)),
            "foreground_app": self.get_foreground_app(),
            "idle_seconds": self.get_idle_seconds(),
            "battery_percent": battery.percent if battery else None,
            "battery_plugged": bool(battery.power_plugged) if battery else None,
            "gpu_name": self.get_gpu_name(),
            "gpu_usage": self.get_gpu_usage(),
            "screen_resolution": self.get_resolution(),
            "network_connected": self.network_connected(),
            "running_apps": self.list_process_names(),
        }
        self._snapshot = snapshot
        return snapshot

    def get_foreground_app(self) -> str:
        try:
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                title = win32gui.GetWindowText(hwnd)
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process = psutil.Process(pid)
                    return process.name() or title or "desktop"
                except Exception:
                    return title or "desktop"
        except Exception:
            pass
        return "desktop"

    def get_idle_seconds(self) -> float:
        if sys.platform.startswith("win"):
            try:
                import ctypes

                class LASTINPUTINFO(ctypes.Structure):
                    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_ulong)]

                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                    current_tick = ctypes.windll.kernel32.GetTickCount()
                    return float((current_tick - lii.dwTime) / 1000.0)
            except Exception:
                pass
        return 0.0

    def get_resolution(self) -> str:
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            return f"{width}x{height}"
        except Exception:
            return "unknown"

    def get_gpu_name(self) -> str | None:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().splitlines()[0]
        except Exception:
            pass
        return None

    def get_gpu_usage(self) -> float | None:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                value = result.stdout.strip().splitlines()[0].strip()
                return float(value.replace("%", ""))
        except Exception:
            pass
        return None

    def list_process_names(self) -> list[str]:
        names = []
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info.get("name")
                if name:
                    names.append(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return sorted(set(names))[:50]

    def network_connected(self) -> bool:
        try:
            return bool(psutil.net_if_stats())
        except Exception:
            return False
