import random, time, threading
import flet as ft

import storage
from constants import DEFAULT_CELL_SIZE, CELL_SIZE_MIN
from maze_logic import init_maze, generate_maze_dfs
from utils import get_translation, get_current_colors, format_time


def game_screen(page: ft.Page, maze_rows, maze_cols, difficulty_level,
                seed=None, show_timer=True):
    from screen_menu import main_menu

    restart_seed = seed if seed is not None else random.randint(1, 1_000_000)
    colors   = get_current_colors()
    controls = storage.user_settings.get("controls",
        {"up": "w", "down": "s", "left": "a", "right": "d", "pause": "escape"})

    base_cell_size = storage.load_user_settings().get("cell_size", DEFAULT_CELL_SIZE)
    page.bgcolor = colors["bg_game"]
    page.window.maximized = True
    page.clean()

    # ── Лабиринт ─────────────────────────────────────────────────────────────
    maze = init_maze(maze_rows, maze_cols)
    if seed is not None: random.seed(seed)
    generate_maze_dfs(maze, maze_rows, maze_cols)
    if seed is not None: random.seed()

    size_factor = max(maze_rows, maze_cols)
    cell_size = max(CELL_SIZE_MIN, base_cell_size - (size_factor - 20) // 3) \
                if size_factor > 20 else base_cell_size
    if cell_size * maze_cols > 1400 or cell_size * maze_rows > 750:
        cw = 1400 // maze_cols if maze_cols else cell_size
        ch = 750  // maze_rows if maze_rows else cell_size
        cell_size = max(CELL_SIZE_MIN, int(min(cw, ch, cell_size)))

    canvas = ft.Stack(width=cell_size * maze_cols, height=cell_size * maze_rows)

    # ── Отрисовка лабиринта ───────────────────────────────────────────────────
    for y in range(maze_rows):
        for x in range(maze_cols):
            if maze["cells"][y][x]:
                canvas.controls.append(ft.Container(
                    left=x*cell_size, top=y*cell_size,
                    width=cell_size, height=cell_size, bgcolor=colors["path"]))
    for y in range(maze_rows + 1):
        for x in range(maze_cols):
            if maze["horizontal_walls"][y][x]:
                canvas.controls.append(ft.Container(
                    left=x*cell_size, top=y*cell_size-1,
                    width=cell_size, height=2, bgcolor=colors["wall"]))
    for y in range(maze_rows):
        for x in range(maze_cols + 1):
            if maze["vertical_walls"][y][x]:
                canvas.controls.append(ft.Container(
                    left=x*cell_size-1, top=y*cell_size,
                    width=2, height=cell_size, bgcolor=colors["wall"]))

    # ── Позиции ───────────────────────────────────────────────────────────────
    px, py = 0, 0
    exit_x, exit_y = maze_cols - 1, maze_rows - 1
    if storage.user_settings.get("random_start", False):
        while True:
            px = random.randint(0, maze_cols - 1)
            py = random.randint(0, maze_rows - 1)
            if (px, py) != (exit_x, exit_y): break

    exit_cell = ft.Container(left=exit_x*cell_size, top=exit_y*cell_size,
                             width=cell_size, height=cell_size, bgcolor=colors["exit"])
    player    = ft.Container(left=px*cell_size, top=py*cell_size,
                             width=cell_size, height=cell_size, bgcolor=colors["player"])
    canvas.controls += [exit_cell, player]

    # ── Состояние и UI ────────────────────────────────────────────────────────
    game_active   = [True]
    game_paused   = [False]
    timer_active  = [True]
    start_time    = time.time()
    paused_time   = [0.0]
    pause_started = [0.0]

    timer_ref  = ft.Ref[ft.Text]()
    timer_text = ft.Text(f"{get_translation('time')}: 00:00.00",
                         size=24, color=colors["timer"], weight=ft.FontWeight.BOLD,
                         ref=timer_ref, visible=show_timer)
    level_text = ft.Text(f"{get_translation('level')}: {difficulty_level}",
                         size=20, color=colors["level"], weight=ft.FontWeight.BOLD)

    overlay_dark = ft.Container(visible=False, expand=True, bgcolor=colors["overlay_dark"])
    time_text    = ft.Text("", size=18, color=colors["record_text"], text_align=ft.TextAlign.CENTER)
    record_text  = ft.Text("", size=16, color=colors["record_new"],  text_align=ft.TextAlign.CENTER)

    def elapsed(): return time.time() - start_time - paused_time[0]

    def _restart_same(e):
        timer_active[0] = False
        game_screen(page, maze_rows, maze_cols, difficulty_level,
                    seed=restart_seed, show_timer=show_timer)
    def _restart_new(e):
        timer_active[0] = False
        game_screen(page, maze_rows, maze_cols, difficulty_level,
                    seed=random.randint(1, 1_000_000), show_timer=show_timer)

    def _fbtn(text, color, handler):
        return ft.FilledButton(text, on_click=handler, width=180, height=45,
            style=ft.ButtonStyle(bgcolor=color, color="#FFFFFF",
                                 shape=ft.RoundedRectangleBorder(radius=8)))

    victory_dialog = ft.Container(
        visible=False, width=400, height=320,
        bgcolor=colors["dialog_bg"], border_radius=20,
        alignment=ft.alignment.Alignment(0, 0),
        content=ft.Column([
            ft.Text(get_translation("congratulations"), size=32,
                    color=colors["record_text"], weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER),
            ft.Text(get_translation("you_won"), size=20, color=colors["text_default"],
                    text_align=ft.TextAlign.CENTER),
            ft.Text(f"{get_translation('level')}: {difficulty_level}", size=16,
                    color=colors["record_text"], text_align=ft.TextAlign.CENTER),
            time_text, record_text,
            ft.Row([_fbtn(get_translation("restart_level"), colors["button_medium"], _restart_same)],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                _fbtn(get_translation("new_level"), colors["button_easy"],  _restart_new),
                _fbtn(get_translation("to_menu"),   colors["button_exit"],  lambda e: main_menu(page)),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
    )

    pause_menu = ft.Container(
        visible=False, width=400, height=260,
        bgcolor=colors["dialog_bg"], border_radius=20,
        alignment=ft.alignment.Alignment(0, 0),
        content=ft.Column([
            ft.Text(get_translation("pause"), size=32, color=colors["record_text"],
                    weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.FilledButton(get_translation("continue"), on_click=lambda e: resume_game(),
                width=250, height=45,
                style=ft.ButtonStyle(bgcolor=colors["button_easy"], color="#FFFFFF",
                                     shape=ft.RoundedRectangleBorder(radius=8))),
            ft.FilledButton(get_translation("restart_level"), on_click=_restart_same,
                width=250, height=45,
                style=ft.ButtonStyle(bgcolor=colors["button_medium"], color="#FFFFFF",
                                     shape=ft.RoundedRectangleBorder(radius=8))),
            ft.FilledButton(get_translation("exit_to_lobby"), on_click=lambda e: main_menu(page),
                width=250, height=45,
                style=ft.ButtonStyle(bgcolor=colors["button_exit"], color="#FFFFFF",
                                     shape=ft.RoundedRectangleBorder(radius=8))),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

    # ── Логика ────────────────────────────────────────────────────────────────
    def move(dx, dy):
        if not game_active[0] or game_paused[0]: return
        nonlocal px, py
        nx, ny = px + dx, py + dy
        if not (0 <= nx < maze_cols and 0 <= ny < maze_rows): return
        if dx ==  1 and maze["vertical_walls"][py][px + 1]:   return
        if dx == -1 and maze["vertical_walls"][py][px]:        return
        if dy ==  1 and maze["horizontal_walls"][py + 1][px]:  return
        if dy == -1 and maze["horizontal_walls"][py][px]:       return
        px, py = nx, ny
        player.left = px * cell_size
        player.top  = py * cell_size
        player.update()
        if (px, py) == (exit_x, exit_y):
            timer_active[0] = False
            ft = elapsed()
            game_active[0]  = False
            is_rec = ft < storage.best_times[difficulty_level]
            if is_rec:
                storage.best_times[difficulty_level] = ft
                storage.save_best_times(storage.best_times)
            time_text.value   = f"{get_translation('your_time')}: {format_time(ft)}"
            record_text.value = (get_translation("new_record") if is_rec else
                f"{get_translation('best_time')} ({difficulty_level}): "
                f"{format_time(storage.best_times[difficulty_level])}")
            overlay_dark.visible   = True
            victory_dialog.visible = True
            time_text.update(); record_text.update()
            overlay_dark.update(); victory_dialog.update()

    def pause_game():
        if not game_active[0]: return
        game_paused[0]   = True
        timer_active[0]  = False
        pause_started[0] = time.time()
        overlay_dark.visible = True
        pause_menu.visible   = True
        overlay_dark.update(); pause_menu.update()

    def resume_game():
        paused_time[0]  += time.time() - pause_started[0]
        game_paused[0]   = False
        timer_active[0]  = True
        overlay_dark.visible = False
        pause_menu.visible   = False
        overlay_dark.update(); pause_menu.update()
        threading.Thread(target=timer_thread, daemon=True).start()

    def timer_thread():
        while timer_active[0]:
            try:
                if not game_paused[0] and show_timer and timer_ref.current:
                    timer_ref.current.value = f"{get_translation('time')}: {format_time(elapsed())}"
                    page.update()
                time.sleep(0.05)
            except: break

    def on_key(e: ft.KeyboardEvent):
        key = e.key.lower()
        if key == controls.get("pause", "escape").lower():
            resume_game() if game_paused[0] else pause_game()
            return
        if game_paused[0]: return
        mapping = {
            controls.get("up",    "w").lower(): (0, -1),
            controls.get("down",  "s").lower(): (0,  1),
            controls.get("left",  "a").lower(): (-1, 0),
            controls.get("right", "d").lower(): (1,  0),
        }
        if key in mapping: move(*mapping[key])

    threading.Thread(target=timer_thread, daemon=True).start()
    page.on_keyboard_event = on_key
    page.add(
        ft.Row([timer_text, level_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Stack([
            ft.Container(content=canvas, alignment=ft.alignment.Alignment(0, 0), expand=True),
            overlay_dark,
            ft.Container(content=victory_dialog, alignment=ft.alignment.Alignment(0, 0), expand=True),
            ft.Container(content=pause_menu,     alignment=ft.alignment.Alignment(0, 0), expand=True),
        ]),
    )
