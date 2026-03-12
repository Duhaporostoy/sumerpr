import time
import threading
import flet as ft

import storage
from constants import DEFAULT_CELL_SIZE, CELL_SIZE_MIN, CELL_SIZE_MAX, THEME_NAMES, SUPPORTED_LANGUAGES
from utils import get_translation, get_current_colors


# ─── Главная страница настроек ───────────────────────────────────────────────
def settings_main(page: ft.Page):
    from screen_menu import main_menu
    colors = get_current_colors()
    page.title   = f"{get_translation('game_title')} - {get_translation('settings_title')}"
    page.bgcolor = colors["bg_main_menu"]
    page.window.maximized = True
    page.clean()
    page.scroll = ft.ScrollMode.AUTO

    categories = [
        ("category_appearance", settings_appearance),
        ("category_controls",   settings_controls),
        ("category_gameplay",   settings_gameplay),
    ]
    tab_buttons = [
        ft.FilledButton(
            get_translation(key),
            on_click=lambda e, f=func: f(page),
            style=ft.ButtonStyle(
                bgcolor=colors["button_start"], color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=5),
                padding=ft.Padding(10, 10, 10, 10),
            ),
        )
        for key, func in categories
    ]
    page.add(ft.Column([
        ft.Divider(height=1, color=colors["primary"]),
        ft.Row(tab_buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=ft.Column([
                ft.Text(get_translation("settings_title"), size=32,
                        color=colors["primary"], weight=ft.FontWeight.BOLD),
                ft.Text(get_translation("select_mode"), size=20, color=colors["text_default"]),
            ], alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
            alignment=ft.alignment.Alignment(0, 0), expand=True,
        ),
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.Row([ft.FilledButton(
            get_translation("back_to_menu"), icon=ft.Icons.ARROW_BACK,
            on_click=lambda e: main_menu(page),
            style=ft.ButtonStyle(bgcolor=colors["button_exit"], color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=10)),
        )], alignment=ft.MainAxisAlignment.START),
    ], alignment=ft.MainAxisAlignment.START,
       horizontal_alignment=ft.CrossAxisAlignment.STRETCH, expand=True))


# ─── Внешний вид ─────────────────────────────────────────────────────────────
def settings_appearance(page: ft.Page):
    storage.user_settings = storage.load_user_settings()
    colors = get_current_colors()
    page.bgcolor = colors["bg_main_menu"]
    page.clean()
    page.scroll = ft.ScrollMode.AUTO

    cur_size = storage.user_settings.get("cell_size", DEFAULT_CELL_SIZE)
    preview  = ft.Container(width=float(cur_size), height=float(cur_size),
                            bgcolor=colors["path"],
                            border=ft.Border.all(1, colors["wall"]))
    size_txt = ft.Text(f"{cur_size}px", size=16, color=colors["settings_label"])

    def on_slider(e):
        v = int(e.control.value)
        size_txt.value = f"{v}px"
        preview.width  = float(v)
        preview.height = float(v)
        size_txt.update(); preview.update()

    slider = ft.Slider(min=CELL_SIZE_MIN, max=CELL_SIZE_MAX, value=cur_size,
                       label="{value}px", on_change=on_slider, width=300)

    cur_theme    = storage.user_settings.get("theme", "classic")
    theme_opts   = [
        ft.dropdown.Option(key=k, text=get_translation(f"theme_{k}"),
                           content=ft.Text(get_translation(f"theme_{k}"),
                                           color=colors["dropdown_text_color"], size=16))
        for k in THEME_NAMES
    ]
    theme_dd = ft.Dropdown(label=get_translation("theme_label"), options=theme_opts,
                           value=cur_theme, width=300,
                           color=colors["dropdown_text_color"],
                           bgcolor=colors["dropdown_bg_color"])

    def save(e):
        storage.user_settings["cell_size"] = int(slider.value)
        storage.user_settings["theme"]     = theme_dd.value
        storage.save_user_settings(storage.user_settings)
        settings_main(page)

    page.add(ft.Column([
        ft.Text(get_translation("appearance_title"), size=32,
                color=colors["primary"], weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Text(get_translation("cell_size_label"), size=20, color=colors["primary"]),
        ft.Row([slider, ft.Column([preview, size_txt],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)],
               alignment=ft.MainAxisAlignment.CENTER,
               vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Divider(),
        ft.Text(get_translation("theme_label"), size=20, color=colors["primary"]),
        theme_dd,
        ft.Divider(height=30),
        _btn_save(colors, save),
        _btn_cancel(colors, lambda e: settings_main(page)),
    ], alignment=ft.MainAxisAlignment.START,
       horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20))


# ─── Геймплей ────────────────────────────────────────────────────────────────
def settings_gameplay(page: ft.Page):
    storage.user_settings = storage.load_user_settings()
    colors = get_current_colors()
    page.bgcolor = colors["bg_main_menu"]
    page.clean()
    page.scroll = ft.ScrollMode.AUTO

    lang_opts = [
        ft.dropdown.Option(key=code, text=name,
                           content=ft.Text(name, color=colors["dropdown_text_color"], size=16))
        for code, name in SUPPORTED_LANGUAGES.items()
    ]
    lang_dd = ft.Dropdown(label=get_translation("language"), options=lang_opts,
                          value=storage.user_settings.get("language", "ru"), width=300,
                          color=colors["dropdown_text_color"],
                          bgcolor=colors["dropdown_bg_color"])

    def save(e):
        storage.user_settings["language"] = lang_dd.value
        storage.save_user_settings(storage.user_settings)
        settings_main(page)

    page.add(ft.Column([
        ft.Text(get_translation("gameplay_title"), size=32,
                color=colors["primary"], weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Text(get_translation("language"), size=20, color=colors["primary"]),
        lang_dd,
        ft.Divider(height=30),
        _btn_save(colors, save),
        _btn_cancel(colors, lambda e: settings_main(page)),
    ], alignment=ft.MainAxisAlignment.START,
       horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20))


# ─── Управление (общий экран: выбор игрока 1 или 2) ─────────────────────────
def settings_controls(page: ft.Page):
    colors = get_current_colors()
    page.bgcolor = colors["bg_main_menu"]
    page.clean()
    page.scroll = ft.ScrollMode.AUTO

    def _btn(label, func):
        return ft.FilledButton(
            label, on_click=lambda e: func(page), width=300, height=55,
            style=ft.ButtonStyle(bgcolor=colors["button_start"], color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=10)))

    page.add(ft.Column([
        ft.Text(get_translation("controls_title"), size=32,
                color=colors["primary"], weight=ft.FontWeight.BOLD),
        ft.Divider(height=20),
        ft.Text("Выберите игрока:", size=20, color=colors["text_default"]),
        _btn(get_translation("controls_player1"), lambda p: _controls_editor(p, player=1)),
        _btn(get_translation("controls_player2"), lambda p: _controls_editor(p, player=2)),
        ft.Divider(height=20),
        _btn_cancel(colors, lambda e: settings_main(page)),
    ], alignment=ft.MainAxisAlignment.CENTER,
       horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20))


def _controls_editor(page: ft.Page, player: int):
    """Редактор клавиш для игрока 1 или 2."""
    storage.user_settings = storage.load_user_settings()
    colors = get_current_colors()
    page.bgcolor = colors["bg_main_menu"]
    page.clean()
    page.scroll = ft.ScrollMode.AUTO

    settings_key = "controls" if player == 1 else "controls_p2"
    title_key    = "controls_player1" if player == 1 else "controls_player2"
    cur_controls = storage.user_settings.get(settings_key, {}).copy()

    actions = [("up","move_up"),("down","move_down"),
               ("left","move_left"),("right","move_right"),("pause","pause_game")]

    widgets = {}
    state   = {"waiting": False, "action": None}

    def update_display(action, key_name):
        txt = key_name.upper() if key_name else get_translation("key_not_set")
        if action in widgets:
            widgets[action]["text"].value = txt
            widgets[action]["text"].update()

    def is_used(key, exclude=None):
        return any(a != exclude and v == key for a, v in cur_controls.items())

    def on_key_event(e: ft.KeyboardEvent):
        if not (state["waiting"] and state["action"]):
            return
        key = e.key.lower()
        if key in {"shift","control","alt","meta","capslock","numlock","scrolllock"}:
            return
        action = state["action"]
        if is_used(key, exclude=action):
            err = widgets[action]["error"]
            err.value = get_translation("key_already_used")
            err.visible = True; err.update()
            def _hide():
                time.sleep(2)
                err.visible = False; err.update()
            threading.Thread(target=_hide, daemon=True).start()
        else:
            cur_controls[action] = key
            update_display(action, key)
            widgets[action]["hint"].visible = False
            widgets[action]["hint"].update()
        state["waiting"] = False; state["action"] = None
        page.on_keyboard_event = None
        page.update()

    def start_assign(e, action):
        if state["waiting"]: return
        state["waiting"] = True; state["action"] = action
        widgets[action]["hint"].visible = True; widgets[action]["hint"].update()
        update_display(action, "...")
        page.on_keyboard_event = on_key_event
        page.update()

    rows_list = []
    for action, t_key in actions:
        kname = cur_controls.get(action, "")
        display = kname.upper() if kname else get_translation("key_not_set")
        key_txt  = ft.Text(display, size=16, color=colors["text_default"])
        hint_txt = ft.Text(get_translation("press_key_to_assign"), size=12,
                           color=colors["primary"], visible=False)
        err_txt  = ft.Text("", size=12, color=colors["button_exit"], visible=False)
        btn = ft.FilledButton(
            "...", on_click=lambda e, a=action: start_assign(e, a),
            width=100, height=40,
            style=ft.ButtonStyle(bgcolor=colors["button_start"], color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=5)))
        widgets[action] = {"text": key_txt, "hint": hint_txt, "error": err_txt}
        rows_list.append(ft.Row([
            ft.Text(get_translation(t_key), size=18, color=colors["primary"], width=160),
            ft.Column([ft.Row([key_txt, btn]), hint_txt, err_txt], spacing=2),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
           vertical_alignment=ft.CrossAxisAlignment.START))

    def save(e):
        storage.user_settings[settings_key] = cur_controls.copy()
        storage.save_user_settings(storage.user_settings)
        settings_controls(page)

    def reset(e):
        from storage import _DEFAULT_CONTROLS, _DEFAULT_CONTROLS_P2
        defaults = _DEFAULT_CONTROLS.copy() if player == 1 else _DEFAULT_CONTROLS_P2.copy()
        cur_controls.clear(); cur_controls.update(defaults)
        for a, _ in actions:
            update_display(a, cur_controls.get(a, ""))
            for wk in ("hint", "error"):
                widgets[a][wk].visible = False; widgets[a][wk].update()
        state["waiting"] = False; state["action"] = None
        page.on_keyboard_event = None

    page.add(ft.Column(
        [ft.Text(get_translation(title_key), size=28,
                 color=colors["primary"], weight=ft.FontWeight.BOLD),
         ft.Divider()] + rows_list + [
         ft.Divider(height=20),
         ft.FilledButton(get_translation("reset_to_defaults"), icon=ft.Icons.RESTORE,
                         on_click=reset, width=300, height=50,
                         style=ft.ButtonStyle(bgcolor=colors["button_medium"], color="#FFFFFF",
                                              shape=ft.RoundedRectangleBorder(radius=10))),
         _btn_save(colors, save),
         _btn_cancel(colors, lambda e: settings_controls(page)),
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15))
    page.update()


# ─── Вспомогательные кнопки ──────────────────────────────────────────────────
def _btn_save(colors, on_click):
    return ft.FilledButton(
        get_translation("save"), icon=ft.Icons.SAVE, on_click=on_click,
        width=300, height=50,
        style=ft.ButtonStyle(bgcolor=colors["button_start"], color="#FFFFFF",
                             shape=ft.RoundedRectangleBorder(radius=10)))

def _btn_cancel(colors, on_click):
    return ft.FilledButton(
        get_translation("cancel"), icon=ft.Icons.CANCEL, on_click=on_click,
        width=300, height=50,
        style=ft.ButtonStyle(bgcolor=colors["button_exit"], color="#FFFFFF",
                             shape=ft.RoundedRectangleBorder(radius=10)))
