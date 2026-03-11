import json
import os
from constants import (
    RECORD_FILE, SETTINGS_FILE, DEFAULT_CELL_SIZE,
    THEMES, SUPPORTED_LANGUAGES
)
from translations import TRANSLATIONS

# --- Глобальное состояние ---
best_times = {}
user_settings = {}

_DEFAULT_CONTROLS = {
    "up": "w", "down": "s", "left": "a", "right": "d", "pause": "escape"
}
_DEFAULT_CONTROLS_P2 = {
    "up": "Arrow Up", "down": "Arrow Down",
    "left": "Arrow Left", "right": "Arrow Right", "pause": "Enter"
}


def load_best_times():
    default = {"Легкий": float("inf"), "Средний": float("inf"), "Высокий": float("inf")}
    try:
        if os.path.exists(RECORD_FILE):
            with open(RECORD_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                data = json.loads(content)
                return {**default, **data}
    except Exception as e:
        print(f"Ошибка загрузки рекордов: {e}")
    return default


def save_best_times(times):
    try:
        with open(RECORD_FILE, "w", encoding="utf-8") as f:
            json.dump(times, f, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения рекордов: {e}")


def load_user_settings():
    default = {
        "cell_size": DEFAULT_CELL_SIZE,
        "theme": "classic",
        "language": "ru",
        "random_start": False,
        "controls": _DEFAULT_CONTROLS.copy(),
        "controls_p2": _DEFAULT_CONTROLS_P2.copy(),
        "music_enabled": True,
        "music_volume": 0.5,
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                return default.copy()
            data = json.loads(content)
            merged = default.copy()
            merged.update(data)
            # Добираем недостающие ключи в controls
            merged["controls"] = {**_DEFAULT_CONTROLS, **merged.get("controls", {})}
            merged["controls_p2"] = {**_DEFAULT_CONTROLS_P2, **merged.get("controls_p2", {})}
            return merged
    except Exception as e:
        print(f"Ошибка загрузки настроек: {e}")
    return default.copy()


def save_user_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")


# --- Инициализация при старте ---
best_times = load_best_times()
user_settings = load_user_settings()
