import flet as ft
import storage
from utils import get_translation, get_current_colors, format_time


def main_menu(page: ft.Page):
    from screen_settings import settings_main
    from screen_difficulty import difficulty_selection_screen, competitive_difficulty_selection_screen

    storage.best_times    = storage.load_best_times()
    storage.user_settings = storage.load_user_settings()
    colors = get_current_colors()

    page.title    = f"{get_translation('game_title')} - {get_translation('main_menu_title')}"
    page.bgcolor  = colors["bg_main_menu"]
    try:
        page.window.maximized = True
    except Exception:
        pass
    page.vertical_alignment   = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.clean()

    records = ft.Column([
        ft.Text(get_translation("records"), size=20,
                color=colors["record_text"], weight=ft.FontWeight.BOLD),
        ft.Text(f"{get_translation('easy')}: {format_time(storage.best_times['Легкий'])}",
                size=16, color=colors["text_default"]),
        ft.Text(f"{get_translation('medium')}: {format_time(storage.best_times['Средний'])}",
                size=16, color=colors["text_default"]),
        ft.Text(f"{get_translation('hard')}: {format_time(storage.best_times['Высокий'])}",
                size=16, color=colors["text_default"]),
    ], spacing=5)

    def _btn(text, color, on_click):
        return ft.FilledButton(text, on_click=on_click, width=250, height=50,
            style=ft.ButtonStyle(bgcolor=color, color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=10)))

    page.add(ft.Column([
        ft.Text(get_translation("game_title"), size=48,
                weight=ft.FontWeight.BOLD, color=colors["primary"]),
        records,
        _btn(get_translation("start_game"), colors["button_start"],
             lambda e: mode_selection_screen(page)),
        _btn(get_translation("settings"),   colors["button_start"],
             lambda e: settings_main(page)),
    ], alignment=ft.MainAxisAlignment.CENTER,
       horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30))


def mode_selection_screen(page: ft.Page):
    from screen_difficulty import difficulty_selection_screen, competitive_difficulty_selection_screen
    colors = get_current_colors()
    page.title   = f"{get_translation('game_title')} - {get_translation('mode_selection_title')}"
    page.bgcolor = colors["bg_main_menu"]
    page.clean()

    def _btn(text, color, on_click):
        return ft.FilledButton(text, on_click=on_click, width=300, height=60,
            style=ft.ButtonStyle(bgcolor=color, color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=10)))

    page.add(ft.Column([
        ft.Text(get_translation("select_mode"), size=36,
                weight=ft.FontWeight.BOLD, color=colors["primary"]),
        _btn(get_translation("single_player"), colors["button_start"],
             lambda e: difficulty_selection_screen(page)),
        _btn(get_translation("competitive"),   colors["button_medium"],
             lambda e: competitive_difficulty_selection_screen(page)),
        _btn(get_translation("back"),          colors["button_exit"],
             lambda e: main_menu(page)),
    ], alignment=ft.MainAxisAlignment.CENTER,
       horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30))