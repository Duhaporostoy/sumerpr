import random, time, threading
import flet as ft

import storage
from constants import DEFAULT_CELL_SIZE, CELL_SIZE_MIN
from maze_logic import init_maze, generate_maze_dfs
from utils import get_translation, get_current_colors, format_time


def competitive_game_screen(page: ft.Page, maze_rows, maze_cols,
                             difficulty_level, seed=None):
    from screen_menu import main_menu

    colors = get_current_colors()

    # ── Управление игроков из настроек ───────────────────────────────────────
    s = storage.load_user_settings()
    ctrl_p1 = s.get("controls", {
        "up": "w", "down": "s", "left": "a", "right": "d", "pause": "escape"
    })
    ctrl_p2 = s.get("controls_p2", {
        "up": "Arrow Up", "down": "Arrow Down",
        "left": "Arrow Left", "right": "Arrow Right", "pause": "Enter"
    })

    base_cell_size = s.get("cell_size", DEFAULT_CELL_SIZE)
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
    p1x, p1y = 0, 0
    p2x, p2y = 0, 0
    ex, ey   = maze_cols - 1, maze_rows - 1

    if s.get("random_start", False):
        while True:
            p1x = random.randint(0, maze_cols-1); p1y = random.randint(0, maze_rows-1)
            if (p1x, p1y) != (ex, ey): break
        while True:
            p2x = random.randint(0, maze_cols-1); p2y = random.randint(0, maze_rows-1)
            if (p2x, p2y) != (ex, ey) and (p2x, p2y) != (p1x, p1y): break

    exit_cell = ft.Container(left=ex*cell_size, top=ey*cell_size,
                             width=cell_size, height=cell_size, bgcolor=colors["exit"])
    p1_color  = colors.get("player1_color", colors["player"])
    p2_color  = colors.get("player2_color", "#0000FF")
    player1   = ft.Container(left=p1x*cell_size, top=p1y*cell_size,
                             width=cell_size, height=cell_size, bgcolor=p1_color)
    player2   = ft.Container(left=p2x*cell_size, top=p2y*cell_size,
                             width=cell_size, height=cell_size, bgcolor=p2_color)
    canvas.controls += [exit_cell, player1, player2]

    # ── Состояние ─────────────────────────────────────────────────────────────
    gs = {
        "active": True, "paused": False, "winner": None,
        "p1_done": False, "p2_done": False,
        "p1_time": None,  "p2_time": None,
        "start":   time.time(), "paused_total": 0.0, "pause_at": 0.0,
    }
    def elapsed(): return time.time() - gs["start"] - gs["paused_total"]

    # ── UI ────────────────────────────────────────────────────────────────────
    timer_ref = ft.Ref[ft.Text]()
    timer_txt = ft.Text(f"{get_translation('time')}: 00:00.00",
                        size=24, color=colors["timer"], weight=ft.FontWeight.BOLD, ref=timer_ref)
    level_txt = ft.Text(f"{get_translation('level')}: {difficulty_level}",
                        size=20, color=colors["level"], weight=ft.FontWeight.BOLD)

    # Подсказки по управлению игроков
    p1_key_up   = ctrl_p1.get("up",   "W").upper()
    p1_key_down = ctrl_p1.get("down", "S").upper()
    p2_key_up   = ctrl_p2.get("up",   "↑").replace("Arrow Up","↑").replace("Arrow Down","↓")\
                                            .replace("Arrow Left","←").replace("Arrow Right","→")
    p2_keys = f"{ctrl_p2.get('up','↑').replace('Arrow Up','↑').replace('Arrow Down','↓').replace('Arrow Left','←').replace('Arrow Right','→')}"

    p1_label = ft.Text(
        f"{get_translation('player')} 1  [{ctrl_p1.get('up','').upper()}/{ctrl_p1.get('down','').upper()}/{ctrl_p1.get('left','').upper()}/{ctrl_p1.get('right','').upper()}]",
        size=16, color=p1_color, weight=ft.FontWeight.BOLD)
    p2_label = ft.Text(
        f"{get_translation('player')} 2  [↑↓←→ стрелки]" if "Arrow" in ctrl_p2.get("up","") else
        f"{get_translation('player')} 2  [{ctrl_p2.get('up','').upper()}/{ctrl_p2.get('down','').upper()}/{ctrl_p2.get('left','').upper()}/{ctrl_p2.get('right','').upper()}]",
        size=16, color=p2_color, weight=ft.FontWeight.BOLD)

    overlay_dark  = ft.Container(visible=False, expand=True, bgcolor=colors["overlay_dark"])
    result_dialog = ft.Container(visible=False, width=420, height=380,
                                 bgcolor=colors["dialog_bg"], border_radius=20,
                                 alignment=ft.alignment.Alignment(0, 0))
    pause_menu    = ft.Container(visible=False, width=400, height=270,
                                 bgcolor=colors["dialog_bg"], border_radius=20,
                                 alignment=ft.alignment.Alignment(0, 0))

    # ── Пауза ────────────────────────────────────────────────────────────────
    def pause_game():
        if not gs["active"] or gs["paused"]: return
        gs["paused"]   = True
        gs["pause_at"] = time.time()
        overlay_dark.visible = True
        pause_menu.visible   = True

        def _restart(e):
            gs["active"] = False
            competitive_game_screen(page, maze_rows, maze_cols, difficulty_level,
                                    seed=random.randint(1, 1_000_000))

        pause_menu.content = ft.Column([
            ft.Text(get_translation("pause"), size=32, color=colors["record_text"],
                    weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.FilledButton(get_translation("continue"), on_click=lambda e: resume_game(),
                width=260, height=45,
                style=ft.ButtonStyle(bgcolor=colors["button_easy"], color="#FFFFFF",
                                     shape=ft.RoundedRectangleBorder(radius=8))),
            ft.FilledButton(get_translation("restart_level"), on_click=_restart,
                width=260, height=45,
                style=ft.ButtonStyle(bgcolor=colors["button_medium"], color="#FFFFFF",
                                     shape=ft.RoundedRectangleBorder(radius=8))),
            ft.FilledButton(get_translation("exit_to_lobby"), on_click=lambda e: main_menu(page),
                width=260, height=45,
                style=ft.ButtonStyle(bgcolor=colors["button_exit"], color="#FFFFFF",
                                     shape=ft.RoundedRectangleBorder(radius=8))),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        overlay_dark.update(); pause_menu.update()

    def resume_game():
        gs["paused_total"] += time.time() - gs["pause_at"]
        gs["paused"]        = False
        overlay_dark.visible = False
        pause_menu.visible   = False
        overlay_dark.update(); pause_menu.update()

    # ── Финиш ────────────────────────────────────────────────────────────────
    def finish_game(winner):
        if gs["winner"]: return
        gs["winner"] = winner
        gs["active"] = False
        t = elapsed()
        if winner == "player1": gs["p1_time"] = t; gs["p1_done"] = True
        else:                   gs["p2_time"] = t; gs["p2_done"] = True

        w_num   = 1 if winner == "player1" else 2
        w_color = p1_color if winner == "player1" else p2_color

        p1_str = format_time(gs["p1_time"]) if gs["p1_time"] else get_translation("not_finished")
        p2_str = format_time(gs["p2_time"]) if gs["p2_time"] else get_translation("not_finished")

        def _restart(e):
            gs["active"] = False
            competitive_game_screen(page, maze_rows, maze_cols, difficulty_level,
                                    seed=random.randint(1, 1_000_000))

        result_dialog.content = ft.Column([
            ft.Text(get_translation("congratulations"), size=28,
                    color=colors["record_text"], weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER),
            ft.Text(f"🏆 {get_translation('winner')}: {get_translation('player')} {w_num}",
                    size=26, color=w_color, weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER),
            ft.Divider(),
            ft.Text(f"{get_translation('player')} 1: {p1_str}",
                    size=18, color=p1_color, text_align=ft.TextAlign.CENTER),
            ft.Text(f"{get_translation('player')} 2: {p2_str}",
                    size=18, color=p2_color, text_align=ft.TextAlign.CENTER),
            ft.Divider(),
            ft.FilledButton(get_translation("new_level"), on_click=_restart,
                width=260, height=45,
                style=ft.ButtonStyle(bgcolor=colors["button_easy"], color="#FFFFFF",
                                     shape=ft.RoundedRectangleBorder(radius=8))),
            ft.FilledButton(get_translation("to_menu"), on_click=lambda e: main_menu(page),
                width=260, height=45,
                style=ft.ButtonStyle(bgcolor=colors["button_exit"], color="#FFFFFF",
                                     shape=ft.RoundedRectangleBorder(radius=8))),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)

        overlay_dark.visible   = True
        result_dialog.visible  = True
        overlay_dark.update(); result_dialog.update(); page.update()

    # ── Движение ─────────────────────────────────────────────────────────────
    def move(pnum, dx, dy):
        if not gs["active"] or gs["paused"]: return
        nonlocal p1x, p1y, p2x, p2y
        if pnum == 1:
            if gs["p1_done"]: return
            cx, cy = p1x, p1y
        else:
            if gs["p2_done"]: return
            cx, cy = p2x, p2y

        nx, ny = cx + dx, cy + dy
        if not (0 <= nx < maze_cols and 0 <= ny < maze_rows): return
        if dx ==  1 and maze["vertical_walls"][cy][cx+1]:    return
        if dx == -1 and maze["vertical_walls"][cy][cx]:       return
        if dy ==  1 and maze["horizontal_walls"][cy+1][cx]:   return
        if dy == -1 and maze["horizontal_walls"][cy][cx]:      return

        if pnum == 1:
            p1x, p1y = nx, ny
            player1.left = p1x*cell_size; player1.top = p1y*cell_size; player1.update()
            if (p1x, p1y) == (ex, ey): gs["p1_time"] = elapsed(); finish_game("player1")
        else:
            p2x, p2y = nx, ny
            player2.left = p2x*cell_size; player2.top = p2y*cell_size; player2.update()
            if (p2x, p2y) == (ex, ey): gs["p2_time"] = elapsed(); finish_game("player2")

    # ── Таймер (ИСПРАВЛЕНО: page.update + учёт паузы) ─────────────────────────
    def timer_thread():
        while gs["active"]:
            try:
                if not gs["paused"] and timer_ref.current:
                    timer_ref.current.value = f"{get_translation('time')}: {format_time(elapsed())}"
                    page.update()
                time.sleep(0.05)
            except: break

    # ── Клавиши ───────────────────────────────────────────────────────────────
    def on_key(e: ft.KeyboardEvent):
        key = e.key
        key_lo = key.lower()

        # Пауза
        p1_pause = ctrl_p1.get("pause", "escape").lower()
        p2_pause = ctrl_p2.get("pause", "enter").lower()
        if key_lo == p1_pause or key_lo == p2_pause:
            resume_game() if gs["paused"] else pause_game()
            return

        if not gs["active"] or gs["paused"] or gs["winner"]: return

        # Игрок 1 (хранится в нижнем регистре)
        if key_lo == ctrl_p1.get("up",    "").lower(): move(1, 0, -1)
        elif key_lo == ctrl_p1.get("down",  "").lower(): move(1, 0,  1)
        elif key_lo == ctrl_p1.get("left",  "").lower(): move(1,-1,  0)
        elif key_lo == ctrl_p1.get("right", "").lower(): move(1, 1,  0)

        # Игрок 2 — стрелки приходят с заглавной буквы ("Arrow Up")
        elif key == ctrl_p2.get("up",    "Arrow Up"):    move(2, 0, -1)
        elif key == ctrl_p2.get("down",  "Arrow Down"):  move(2, 0,  1)
        elif key == ctrl_p2.get("left",  "Arrow Left"):  move(2,-1,  0)
        elif key == ctrl_p2.get("right", "Arrow Right"): move(2, 1,  0)
        # Если у p2 назначены обычные буквы — проверяем в нижнем регистре
        elif key_lo == ctrl_p2.get("up",    "").lower() and "arrow" not in ctrl_p2.get("up","").lower():   move(2, 0,-1)
        elif key_lo == ctrl_p2.get("down",  "").lower() and "arrow" not in ctrl_p2.get("down","").lower(): move(2, 0, 1)
        elif key_lo == ctrl_p2.get("left",  "").lower() and "arrow" not in ctrl_p2.get("left","").lower(): move(2,-1, 0)
        elif key_lo == ctrl_p2.get("right", "").lower() and "arrow" not in ctrl_p2.get("right","").lower():move(2, 1, 0)

    threading.Thread(target=timer_thread, daemon=True).start()
    page.on_keyboard_event = on_key

    page.add(
        ft.Row([p1_label, timer_txt, p2_label, level_txt],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Stack([
            ft.Container(content=canvas, alignment=ft.alignment.Alignment(0,0), expand=True),
            overlay_dark,
            ft.Container(content=result_dialog, alignment=ft.alignment.Alignment(0,0), expand=True),
            ft.Container(content=pause_menu,    alignment=ft.alignment.Alignment(0,0), expand=True),
        ]),
    )
