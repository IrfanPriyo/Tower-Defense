from collections import deque
from settings import ROWS, COLS, START, END
import random

def bfs(grid, start, end):
    """BFS algorithm to find shortest path from start to end"""
    queue = deque()
    queue.append(start)
    visited = {start: None}
    while queue:
        current = queue.popleft()
        if current == end:
            path = []
            while current is not None:
                path.append(current)
                current = visited[current]
            path.reverse()
            return path
        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < ROWS and 0 <= nc < COLS
                    and (nr, nc) not in visited
                    and grid[nr][nc] != 1
                    and grid[nr][nc] != 2):
                visited[(nr, nc)] = current
                queue.append((nr, nc))
    return None

def generate_obstacles(grid):
    """Generate random obstacles that still allow a path from START to END"""
    obstacle_count = random.randint(20, 35)
    attempts = 0
    placed = 0
    while placed < obstacle_count and attempts < 500:
        attempts += 1
        r = random.randint(0, ROWS - 1)
        c = random.randint(1, COLS - 2)
        if abs(r - START[0]) <= 1 and c <= 1:
            continue
        if abs(r - END[0]) <= 1 and c >= COLS - 2:
            continue
        if (r, c) == START or (r, c) == END:
            continue
        if grid[r][c] != 0:
            continue
        grid[r][c] = 2
        test_path = bfs(grid, START, END)
        if test_path is None:
            grid[r][c] = 0
        else:
            placed += 1
    return grid