"""
benchmark.py — BFS vs A* pathfinding benchmark on grid graphs of increasing size.

Usage:
    python benchmark.py

Output:
    benchmark_results.csv   — timing, nodes explored, path length per size
    benchmark_plot.png      — log-log runtime and nodes-explored plots
                              (requires matplotlib; skipped if not installed)

This script is fully standalone: it does NOT import pygame or any game module.
It implements its own BFS and A* with node-count instrumentation, and generates
synthetic grids with a guaranteed path (centre row is always clear).

Benchmark parameters
--------------------
SEED            : 42        (fixed for reproducibility)
RUNS_PER_SIZE   : 5         (average over 5 independent random grids)
OBSTACLE_RATIO  : 0.20      (20 % of non-path cells become obstacles)
SIZES           : five grid dimensions spanning ≈ three orders of magnitude
                  10×10=100, 32×32=1 024, 100×100=10 000,
                  200×200=40 000, 316×316=99 856
"""

import csv
import heapq
import os
import random
import time
from collections import deque

# ── benchmark parameters ──────────────────────────────────────────────────────

SEED = 42
RUNS_PER_SIZE = 5
OBSTACLE_RATIO = 0.20

SIZES = [
    (10,  10),   #     100 cells
    (32,  32),   #   1 024 cells
    (100, 100),  #  10 000 cells
    (200, 200),  #  40 000 cells
    (316, 316),  #  99 856 cells
]

# ── grid generator ────────────────────────────────────────────────────────────

def _make_grid(rows, cols, seed):
    """Return (grid, start, end) with a guaranteed clear centre-row path.

    The centre row (rows//2, all columns) is always kept passable so that
    a valid path always exists without needing a BFS validation loop.
    Obstacles (cell value 2) are scattered randomly at density OBSTACLE_RATIO
    in all other rows, avoiding the leftmost and rightmost columns.
    """
    rng = random.Random(seed)
    grid = [[0] * cols for _ in range(rows)]
    mid = rows // 2
    start = (mid, 0)
    end   = (mid, cols - 1)
    for r in range(rows):
        if r == mid:
            continue           # keep the centre row clear
        for c in range(1, cols - 1):
            if rng.random() < OBSTACLE_RATIO:
                grid[r][c] = 2
    return grid, start, end

# ── BFS with node-count instrumentation ──────────────────────────────────────

def _bfs(grid, start, end, rows, cols):
    """Standard BFS; returns (path, nodes_explored)."""
    queue   = deque([start])
    visited = {start: None}
    explored = 0

    while queue:
        cur = queue.popleft()
        explored += 1
        if cur == end:
            path = []
            while cur is not None:
                path.append(cur)
                cur = visited[cur]
            path.reverse()
            return path, explored
        r, c = cur
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in visited
                    and grid[nr][nc] != 1
                    and grid[nr][nc] != 2):
                visited[(nr, nc)] = cur
                queue.append((nr, nc))
    return None, explored

# ── A* with node-count instrumentation ───────────────────────────────────────

def _h(a, b):
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _astar(grid, start, end, rows, cols):
    """A* with Manhattan heuristic; returns (path, nodes_explored).

    Uses a closed set (nodes whose optimal cost is finalized) to avoid
    re-expanding settled nodes.  Because the heuristic is admissible
    (Manhattan distance never overestimates unit-cost grid steps), the
    algorithm is guaranteed to find an optimal path identical in length
    to BFS on this unweighted grid.
    """
    heap    = []
    counter = 0
    heapq.heappush(heap, (_h(start, end), counter, start))

    came_from = {start: None}
    g         = {start: 0}
    closed    = set()
    explored  = 0

    while heap:
        _, _, cur = heapq.heappop(heap)
        if cur in closed:
            continue
        closed.add(cur)
        explored += 1

        if cur == end:
            path = []
            while cur is not None:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            return path, explored

        r, c = cur
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in closed
                    and grid[nr][nc] != 1
                    and grid[nr][nc] != 2):
                nbr = (nr, nc)
                ng  = g[cur] + 1
                if nbr not in g or ng < g[nbr]:
                    g[nbr]         = ng
                    came_from[nbr] = cur
                    f              = ng + _h(nbr, end)
                    counter       += 1
                    heapq.heappush(heap, (f, counter, nbr))

    return None, explored

# ── main benchmark ────────────────────────────────────────────────────────────

def run_benchmark():
    results = []

    hdr = (f"{'Grid':>10} {'Cells':>8} {'BFS ms':>9} {'A* ms':>9} "
           f"{'BFS nodes':>11} {'A* nodes':>11} {'Path len':>10} {'Match':>6}")
    sep = "-" * len(hdr)
    print(hdr)
    print(sep)

    for rows, cols in SIZES:
        n_cells = rows * cols
        bfs_times,   astar_times   = [], []
        bfs_nodes_l, astar_nodes_l = [], []
        all_match = True
        last_bfs_plen = None

        for run in range(RUNS_PER_SIZE):
            seed  = SEED + run
            grid, start, end = _make_grid(rows, cols, seed)

            t0 = time.perf_counter()
            bfs_path, bfs_nodes = _bfs(grid, start, end, rows, cols)
            bfs_times.append(time.perf_counter() - t0)
            bfs_nodes_l.append(bfs_nodes)

            t0 = time.perf_counter()
            ast_path, ast_nodes = _astar(grid, start, end, rows, cols)
            astar_times.append(time.perf_counter() - t0)
            astar_nodes_l.append(ast_nodes)

            bfs_len  = len(bfs_path)  if bfs_path  else -1
            ast_len  = len(ast_path)  if ast_path  else -1
            if bfs_len != ast_len:
                all_match = False
            if bfs_path:
                last_bfs_plen = bfs_len

        avg_bfs_ms   = sum(bfs_times)   / RUNS_PER_SIZE * 1000
        avg_ast_ms   = sum(astar_times) / RUNS_PER_SIZE * 1000
        avg_bfs_n    = sum(bfs_nodes_l) / RUNS_PER_SIZE
        avg_ast_n    = sum(astar_nodes_l) / RUNS_PER_SIZE
        match_str    = "YES" if all_match else "NO"
        plen_str     = str(last_bfs_plen) if last_bfs_plen is not None else "N/A"
        grid_str     = f"{rows}x{cols}"

        print(f"{grid_str:>10} {n_cells:>8,} {avg_bfs_ms:>9.2f} {avg_ast_ms:>9.2f} "
              f"{avg_bfs_n:>11.0f} {avg_ast_n:>11.0f} {plen_str:>10} {match_str:>6}")

        results.append({
            "grid":        grid_str,
            "cells":       n_cells,
            "rows":        rows,
            "cols":        cols,
            "bfs_ms":      round(avg_bfs_ms,  4),
            "astar_ms":    round(avg_ast_ms,  4),
            "bfs_nodes":   round(avg_bfs_n,   1),
            "astar_nodes": round(avg_ast_n,   1),
            "path_len":    last_bfs_plen,
            "path_match":  match_str,
        })

    # ── write CSV ─────────────────────────────────────────────────────────────
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "benchmark_results.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved: {csv_path}")

    # ── plot (optional) ───────────────────────────────────────────────────────
    try:
        import matplotlib.pyplot as plt

        cells    = [r["cells"]       for r in results]
        bfs_ms   = [r["bfs_ms"]      for r in results]
        ast_ms   = [r["astar_ms"]    for r in results]
        bfs_n    = [r["bfs_nodes"]   for r in results]
        ast_n    = [r["astar_nodes"] for r in results]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        fig.suptitle("BFS vs A* on Random Grid Graphs (avg of 5 runs, seed=42)",
                     fontsize=13, fontweight="bold")

        # Runtime plot
        ax1.loglog(cells, bfs_ms, "o-b", label="BFS",  linewidth=2, markersize=7)
        ax1.loglog(cells, ast_ms, "s-r", label="A*",   linewidth=2, markersize=7)
        ax1.set_xlabel("Grid size (cells)")
        ax1.set_ylabel("Average runtime (ms)")
        ax1.set_title("Runtime vs Grid Size (log–log)")
        ax1.legend()
        ax1.grid(True, which="both", alpha=0.35)

        # Nodes-explored plot
        ax2.loglog(cells, bfs_n, "o-b", label="BFS",  linewidth=2, markersize=7)
        ax2.loglog(cells, ast_n, "s-r", label="A*",   linewidth=2, markersize=7)
        ax2.set_xlabel("Grid size (cells)")
        ax2.set_ylabel("Nodes explored")
        ax2.set_title("Nodes Explored vs Grid Size (log–log)")
        ax2.legend()
        ax2.grid(True, which="both", alpha=0.35)

        plt.tight_layout()
        plot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "benchmark_plot.png")
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        print(f"Plot saved: {plot_path}")
        plt.show()

    except ImportError:
        print("matplotlib not installed — skipping plot generation.")
        print("Install with:  pip install matplotlib")


if __name__ == "__main__":
    print(f"Tower Defense — BFS vs A* Benchmark")
    print(f"Seed: {SEED}  |  Runs/size: {RUNS_PER_SIZE}  "
          f"|  Obstacle ratio: {OBSTACLE_RATIO:.0%}\n")
    run_benchmark()
