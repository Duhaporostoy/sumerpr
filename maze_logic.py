import random


def init_maze(rows: int, cols: int) -> dict:
    return {
        "cells":            [[False] * cols for _ in range(rows)],
        "vertical_walls":   [[True]  * (cols + 1) for _ in range(rows)],
        "horizontal_walls": [[True]  * cols for _ in range(rows + 1)],
    }


def generate_maze_dfs(maze: dict, rows: int, cols: int) -> None:
    visited = [[False] * cols for _ in range(rows)]

    def carve(x, y):
        visited[y][x] = True
        maze["cells"][y][x] = True
        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx]:
                if   dx ==  1: maze["vertical_walls"][y][x + 1]   = False
                elif dx == -1: maze["vertical_walls"][y][x]        = False
                elif dy ==  1: maze["horizontal_walls"][y + 1][x]  = False
                elif dy == -1: maze["horizontal_walls"][y][x]      = False
                carve(nx, ny)

    carve(0, 0)
