import random
import flet as ft
import storage
from constants import DIFFICULTY_SETTINGS
from utils import get_translation, get_current_colors


def difficulty_selection_screen(page: ft.Page):
    from screen_menu import mode_selection_screen
    from screen_game import game_screen

    storage.user_settings = storage.load_user_settings()
    colors = get_current_colors()
    page.title   = f"{get_translation('game_title')} - {get_translation('difficulty_selection_title')}"
    page.bgcolor = colors["bg_main_menu"]
    page.clean()

    random_switch = ft.Switch(
        label=get_translation("random_start_position"),
        value=storage.user_settings.get("random_start", False),
        active_color=colors["button_start"],
    )
    timer_switch = ft.Switch(
        label=get_translation("show_timer"),
        value=True,
        active_color=colors["button_start"],
    )

    def start(difficulty):
        storage.user_settings["random_start"] = random_switch.value
        storage.save_user_settings(storage.user_settings)
        s = DIFFICULTY_SETTINGS[difficulty]
        game_screen(page, s["rows"], s["cols"], difficulty,
                    seed=random.randint(1, 1_000_000),
                    show_timer=timer_switch.value)

    def _diff_btn(label, color, diff):
        return ft.FilledButton(label, on_click=lambda e: start(diff), width=300, height=60,
            style=ft.ButtonStyle(bgcolor=color, color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=10)))

    page.add(ft.Column([
        ft.Text(get_translation("select_difficulty"), size=36,
                weight=ft.FontWeight.BOLD, color=colors["primary"]),
        ft.Row([
            ft.Container(content=ft.Column([
                _diff_btn(get_translation("easy_level"),   colors["button_easy"],   "Легкий"),
                _diff_btn(get_translation("medium_level"), colors["button_medium"], "Средний"),
                _diff_btn(get_translation("hard_level"),   colors["button_hard"],   "Высокий"),
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.Alignment(1, 0), expand=True),
            ft.Container(content=ft.Column([random_switch, timer_switch],
                spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.Alignment(-1, 0), expand=True),
        ], alignment=ft.MainAxisAlignment.CENTER,
           vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
        ft.Container(content=ft.FilledButton(
            get_translation("back"), on_click=lambda e: mode_selection_screen(page),
            width=300, height=50,
            style=ft.ButtonStyle(bgcolor=colors["button_exit"], color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=10))),
        alignment=ft.alignment.Alignment(0, 0), padding=ft.Padding.only(top=30)),
    ], alignment=ft.MainAxisAlignment.CENTER,
       horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30, expand=True))


def competitive_difficulty_selection_screen(page: ft.Page):
    from screen_menu import mode_selection_screen
    from screen_competitive import competitive_game_screen

    colors = get_current_colors()
    page.title   = f"{get_translation('game_title')} - {get_translation('competitive')}"
    page.bgcolor = colors["bg_main_menu"]
    page.clean()

    def start(difficulty):
        s = DIFFICULTY_SETTINGS[difficulty]
        competitive_game_screen(page, s["rows"], s["cols"], difficulty,
                                seed=random.randint(1, 1_000_000))

    def _diff_btn(label, color, diff):
        return ft.FilledButton(label, on_click=lambda e: start(diff), width=300, height=60,
            style=ft.ButtonStyle(bgcolor=color, color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=10)))

    page.add(ft.Column([
        ft.Text(f"{get_translation('select_difficulty')} — {get_translation('competitive')}",
                size=32, weight=ft.FontWeight.BOLD, color=colors["primary"]),
        _diff_btn(get_translation("easy_level"),   colors["button_easy"],   "Легкий"),
        _diff_btn(get_translation("medium_level"), colors["button_medium"], "Средний"),
        _diff_btn(get_translation("hard_level"),   colors["button_hard"],   "Высокий"),
        ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
        ft.FilledButton(get_translation("back"), on_click=lambda e: mode_selection_screen(page),
            width=300, height=50,
            style=ft.ButtonStyle(bgcolor=colors["button_exit"], color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=10))),
    ], alignment=ft.MainAxisAlignment.CENTER,
       horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30))
