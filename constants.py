RECORD_FILE = "maze_records.json"
SETTINGS_FILE = "user_settings.json"

DIFFICULTY_SETTINGS = {
    "Легкий":  {"rows": 10, "cols": 10},
    "Средний": {"rows": 20, "cols": 20},
    "Высокий": {"rows": 25, "cols": 40},
}

DEFAULT_CELL_SIZE = 40
CELL_SIZE_MIN = 15
CELL_SIZE_MAX = 80

THEMES = {
    "classic": {
        "bg_main_menu": "#E6F3FF", "bg_game": "#000000", "primary": "#2E86AB",
        "button_start": "#5DA7DB", "button_exit": "#FF6B6B",
        "button_easy": "#4CAF50", "button_medium": "#FF9800", "button_hard": "#F44336",
        "player": "#ff0000", "player2": "#0000ff", "exit": "#00ff00",
        "wall": "#ffffff", "path": "#0000ff", "timer": "#FFFFFF", "level": "#FFFF00",
        "record_new": "#4CAF50", "record_text": "#2E86AB",
        "text_default": "#333333", "text_on_light_bg": "#333333", "text_on_dark_bg": "#FFFFFF",
        "overlay_dark": "#00000099", "dialog_bg": "#FFFFFF", "settings_label": "#555555",
        "dropdown_text_color": "#000000", "dropdown_bg_color": "#FFFFFF",
        "switch_label_color": "#000000", "player1_color": "#ff0000", "player2_color": "#0000ff",
    },
    "dark": {
        "bg_main_menu": "#1E1E1E", "bg_game": "#000000", "primary": "#4A90E2",
        "button_start": "#3A7BC8", "button_exit": "#C44536",
        "button_easy": "#3A7C3A", "button_medium": "#C97C3A", "button_hard": "#C44536",
        "player": "#ff4d4d", "player2": "#4d4dff", "exit": "#4dff4d",
        "wall": "#aaaaaa", "path": "#333399", "timer": "#FFFFFF", "level": "#FFFF99",
        "record_new": "#4dff4d", "record_text": "#4A90E2",
        "text_default": "#CCCCCC", "text_on_light_bg": "#333333", "text_on_dark_bg": "#FFFFFF",
        "overlay_dark": "#000000CC", "dialog_bg": "#2D2D2D", "settings_label": "#AAAAAA",
        "dropdown_text_color": "#FFFFFF", "dropdown_bg_color": "#3E3E3E",
        "switch_label_color": "#FFFFFF", "player1_color": "#ff4d4d", "player2_color": "#4d4dff",
    },
    "high_contrast": {
        "bg_main_menu": "#FFFFFF", "bg_game": "#000000", "primary": "#000000",
        "button_start": "#0066CC", "button_exit": "#CC0000",
        "button_easy": "#009900", "button_medium": "#FF9900", "button_hard": "#CC0000",
        "player": "#FF0000", "player2": "#0000FF", "exit": "#00FF00",
        "wall": "#FFFFFF", "path": "#0000FF", "timer": "#FFFFFF", "level": "#FFFF00",
        "record_new": "#00FF00", "record_text": "#000000",
        "text_default": "#000000", "text_on_light_bg": "#000000", "text_on_dark_bg": "#FFFFFF",
        "overlay_dark": "#000000CC", "dialog_bg": "#EEEEEE", "settings_label": "#333333",
        "dropdown_text_color": "#000000", "dropdown_bg_color": "#FFFFFF",
        "switch_label_color": "#000000", "player1_color": "#FF0000", "player2_color": "#0000FF",
    },
    "ocean": {
        "bg_main_menu": "#B0D8FF", "bg_game": "#001f3f", "primary": "#0074D9",
        "button_start": "#39CCCC", "button_exit": "#FF4136",
        "button_easy": "#2ECC40", "button_medium": "#FFDC00", "button_hard": "#B10DC9",
        "player": "#FF4136", "player2": "#39CCCC", "exit": "#2ECC40",
        "wall": "#AAAAAA", "path": "#0074D9", "timer": "#FFFFFF", "level": "#FFDC00",
        "record_new": "#2ECC40", "record_text": "#001f3f",
        "text_default": "#111111", "text_on_light_bg": "#111111", "text_on_dark_bg": "#FFFFFF",
        "overlay_dark": "#00000099", "dialog_bg": "#FFFFFF", "settings_label": "#333333",
        "dropdown_text_color": "#000000", "dropdown_bg_color": "#FFFFFF",
        "switch_label_color": "#000000", "player1_color": "#FF4136", "player2_color": "#39CCCC",
    },
    "forest": {
        "bg_main_menu": "#A8E6CF", "bg_game": "#1B5E20", "primary": "#4CAF50",
        "button_start": "#8BC34A", "button_exit": "#F44336",
        "button_easy": "#009688", "button_medium": "#FFC107", "button_hard": "#795548",
        "player": "#F44336", "player2": "#FFC107", "exit": "#FFEB3B",
        "wall": "#8D6E63", "path": "#4CAF50", "timer": "#FFFFFF", "level": "#FF9800",
        "record_new": "#FFEB3B", "record_text": "#1B5E20",
        "text_default": "#222222", "text_on_light_bg": "#222222", "text_on_dark_bg": "#FFFFFF",
        "overlay_dark": "#00000099", "dialog_bg": "#FFFFFF", "settings_label": "#444444",
        "dropdown_text_color": "#000000", "dropdown_bg_color": "#FFFFFF",
        "switch_label_color": "#000000", "player1_color": "#F44336", "player2_color": "#FFC107",
    },
    "sunset": {
        "bg_main_menu": "#FFD1DC", "bg_game": "#4A235A", "primary": "#FF6B35",
        "button_start": "#F79F1F", "button_exit": "#EA2027",
        "button_easy": "#006266", "button_medium": "#EE5A24", "button_hard": "#5758BB",
        "player": "#EA2027", "player2": "#F79F1F", "exit": "#009432",
        "wall": "#6D214F", "path": "#12CBC4", "timer": "#FFFFFF", "level": "#0652DD",
        "record_new": "#009432", "record_text": "#4A235A",
        "text_default": "#333333", "text_on_light_bg": "#333333", "text_on_dark_bg": "#FFFFFF",
        "overlay_dark": "#00000099", "dialog_bg": "#FFFFFF", "settings_label": "#555555",
        "dropdown_text_color": "#000000", "dropdown_bg_color": "#FFFFFF",
        "switch_label_color": "#000000", "player1_color": "#EA2027", "player2_color": "#F79F1F",
    },
}

THEME_NAMES = {
    "classic":       "Классическая",
    "dark":          "Темная",
    "high_contrast": "Высококонтрастная",
    "ocean":         "Океан",
    "forest":        "Лес",
    "sunset":        "Закат",
}

SUPPORTED_LANGUAGES = {
    "ru": "Русский",
    "en": "English",
}
