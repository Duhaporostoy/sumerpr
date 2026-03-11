import unittest
import os
import json
import tempfile
import shutil

# Импортируем из отдельных модулей вместо test.py
import storage
import utils
import maze_logic
from constants import DEFAULT_CELL_SIZE, THEMES
from translations import TRANSLATIONS


class TestMazeGame(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self._orig_record   = storage.RECORD_FILE
        self._orig_settings = storage.SETTINGS_FILE
        storage.RECORD_FILE   = os.path.join(self.test_dir, "test_records.json")
        storage.SETTINGS_FILE = os.path.join(self.test_dir, "test_settings.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        storage.RECORD_FILE   = self._orig_record
        storage.SETTINGS_FILE = self._orig_settings

    # ── format_time ────────────────────────────────────────────────────────
    def test_format_time_valid(self):
        storage.user_settings = {"language": "ru"}
        self.assertEqual(utils.format_time(0),        "00:00.00")   # 0 — корректное время
        self.assertEqual(utils.format_time(61.5),     "01:01.50")
        self.assertEqual(utils.format_time(3661.99),  "61:01.99")

        storage.user_settings = {"language": "en"}
        self.assertEqual(utils.format_time(61.5), "01:01.50")

    def test_format_time_invalid(self):
        storage.user_settings = {"language": "ru"}
        self.assertEqual(utils.format_time(float("inf")), "Нет данных")
        self.assertEqual(utils.format_time(-1),           "Нет данных")
        self.assertEqual(utils.format_time(0),            "00:00.00")

        storage.user_settings = {"language": "en"}
        self.assertEqual(utils.format_time(float("inf")), "No Data")
        self.assertEqual(utils.format_time(-1),           "No Data")

    # ── Рекорды ────────────────────────────────────────────────────────────
    def test_best_times_io(self):
        if os.path.exists(storage.RECORD_FILE):
            os.remove(storage.RECORD_FILE)

        loaded = storage.load_best_times()
        self.assertEqual(loaded, {"Легкий": float("inf"), "Средний": float("inf"), "Высокий": float("inf")})

        test_times = {"Легкий": 123.45, "Средний": 456.78, "Высокий": 789.01}
        storage.save_best_times(test_times)
        self.assertEqual(storage.load_best_times(), test_times)

        partial = {"Легкий": 100.0}
        with open(storage.RECORD_FILE, "w") as f:
            json.dump(partial, f)
        loaded2 = storage.load_best_times()
        self.assertEqual(loaded2["Легкий"],  100.0)
        self.assertEqual(loaded2["Средний"], float("inf"))
        self.assertEqual(loaded2["Высокий"], float("inf"))

    # ── Настройки ──────────────────────────────────────────────────────────
    def test_user_settings_io(self):
        if os.path.exists(storage.SETTINGS_FILE):
            os.remove(storage.SETTINGS_FILE)

        loaded = storage.load_user_settings()
        expected_defaults = {
            "cell_size": DEFAULT_CELL_SIZE,
            "theme":     "classic",
            "language":  "ru",
            "random_start": False,
            "controls": {"up": "w", "down": "s", "left": "a", "right": "d", "pause": "escape"},
            "music_enabled": True,
            "music_volume":  0.5,
        }
        for key, value in expected_defaults.items():
            self.assertEqual(loaded.get(key), value, f"Default mismatch for '{key}'")

        custom = {
            "cell_size": 30, "theme": "dark", "language": "en", "random_start": True,
            "controls": {"up": "UP", "down": "DOWN", "left": "LEFT", "right": "RIGHT", "pause": "p"},
            "music_enabled": False, "music_volume": 0.8, "extra": "val",
        }
        storage.save_user_settings(custom)
        reloaded = storage.load_user_settings()
        for key, value in custom.items():
            self.assertEqual(reloaded.get(key), value, f"Custom mismatch for '{key}'")

        # Частичные контролы — должны добиться дефолтами
        with open(storage.SETTINGS_FILE, "w") as f:
            json.dump({"cell_size": 35, "controls": {"up": "I"}}, f)
        loaded3 = storage.load_user_settings()
        self.assertEqual(loaded3["controls"]["up"],    "I")
        self.assertEqual(loaded3["controls"]["down"],  "s")
        self.assertEqual(loaded3["controls"]["left"],  "a")
        self.assertEqual(loaded3["controls"]["right"], "d")
        self.assertEqual(loaded3["controls"]["pause"], "escape")

    # ── Лабиринт ───────────────────────────────────────────────────────────
    def test_maze_generation_validity(self):
        rows, cols = 5, 7
        maze = maze_logic.init_maze(rows, cols)
        self.assertEqual(len(maze["cells"]),              rows)
        self.assertEqual(len(maze["cells"][0]),           cols)
        self.assertEqual(len(maze["vertical_walls"]),     rows)
        self.assertEqual(len(maze["vertical_walls"][0]),  cols + 1)
        self.assertEqual(len(maze["horizontal_walls"]),   rows + 1)
        self.assertEqual(len(maze["horizontal_walls"][0]), cols)

        for row in maze["cells"]:
            for cell in row:
                self.assertFalse(cell)

        maze_logic.generate_maze_dfs(maze, rows, cols)
        accessible = sum(1 for row in maze["cells"] for cell in row if cell)
        self.assertGreater(accessible, 0)
        self.assertTrue(maze["cells"][0][0])

    # ── Переводы ────────────────────────────────────────────────────────────
    def test_get_translation(self):
        storage.user_settings = {"language": "ru"}
        self.assertEqual(utils.get_translation("start_game"),       "Начать игру")
        self.assertEqual(utils.get_translation("non_existent_key"), "non_existent_key")

        storage.user_settings = {"language": "en"}
        self.assertEqual(utils.get_translation("start_game"), "Start Game")

        TRANSLATIONS["_test_en_only"] = {"en": "English Only"}
        self.assertEqual(utils.get_translation("_test_en_only"), "English Only")
        del TRANSLATIONS["_test_en_only"]

        storage.user_settings = {"language": "xx"}
        TRANSLATIONS["_test_key"] = {"en": "English", "ru": "Русский"}
        self.assertEqual(utils.get_translation("_test_key"), "English")
        del TRANSLATIONS["_test_key"]

    # ── Темы ────────────────────────────────────────────────────────────────
    def test_get_current_colors(self):
        storage.user_settings = {"theme": "classic"}
        self.assertEqual(utils.get_current_colors(), THEMES["classic"])

        storage.user_settings = {"theme": "dark"}
        self.assertEqual(utils.get_current_colors(), THEMES["dark"])

        storage.user_settings = {"theme": "non_existent"}
        self.assertEqual(utils.get_current_colors(), THEMES["classic"])


if __name__ == "__main__":
    storage.best_times    = storage.load_best_times()
    storage.user_settings = storage.load_user_settings()
    unittest.main()
