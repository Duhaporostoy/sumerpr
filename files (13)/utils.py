import storage
from constants import THEMES
from translations import TRANSLATIONS


def format_time(seconds: float) -> str:
    """
    Форматирует время в MM:SS.сс
    ИСПРАВЛЕНО: seconds < 0 вместо <= 0, чтобы 0.0 -> "00:00.00"
    """
    lang = storage.user_settings.get("language", "ru")
    no_data = TRANSLATIONS["no_data"].get(lang, "Нет данных")

    if seconds == float("inf") or seconds < 0:
        return no_data

    total_cs = int(seconds * 100)       # переводим в сотые секунды (целые)
    minutes  = total_cs // 6000
    secs     = (total_cs % 6000) // 100
    cs       = total_cs % 100
    return f"{minutes:02d}:{secs:02d}.{cs:02d}"


def get_translation(key: str) -> str:
    lang = storage.user_settings.get("language", "ru")
    if key not in TRANSLATIONS:
        return key
    entry = TRANSLATIONS[key]
    if lang in entry:
        return entry[lang]
    if "en" in entry:
        return entry["en"]
    return next(iter(entry.values()), key)


def get_current_colors() -> dict:
    theme = storage.user_settings.get("theme", "classic")
    return THEMES.get(theme, THEMES["classic"])
