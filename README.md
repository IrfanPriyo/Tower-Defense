# Tower Defense — BFS vs A* Pathfinding

EF234405 Design & Analysis of Algorithms — Final Exam Capstone Project

## Description

A tower-defense game that demonstrates and empirically compares two pathfinding algorithms on a dynamic grid:

- **BFS (Breadth-First Search)** — explores every cell at distance *d* before *d+1*; guaranteed shortest path, O(V+E).
- **A\* (A-star)** — priority-guided search using the Manhattan distance heuristic; also finds the optimal path but explores far fewer nodes, O(E log V) in practice.

Enemies navigate from the left edge to the right edge of the grid. When the player places or removes a tower, every living enemy recalculates its path on-the-fly using whichever algorithm was selected at the menu.

## Requirements

- **Python 3.12.6** (tested; 3.9+ should work)
- pygame

```
pip install pygame
```

For benchmark plots (optional):

```
pip install matplotlib
```

## How to Run

```bash
python main.py
```

### Algorithm selection

The main menu presents two start buttons:

| Button | Algorithm |
|--------|-----------|
| **BFS Mode** | Breadth-First Search |
| **A\* Mode** | A\* with Manhattan heuristic |

The active algorithm is shown in the game header.

### Controls

| Key / Mouse | Action |
|---|---|
| Left click | Place a tower |
| Right click | Remove a tower |
| **P** | Toggle path visualisation |
| **R** | Restart (after game over) |
| Settings → Restart | Restart with same algorithm |

## Run the Benchmark

```bash
python benchmark.py
```

This single command:
1. Generates random grids at **5 sizes** spanning ≈ 3 orders of magnitude  
   (`10×10` → `316×316`, i.e. 100 → ~100 000 cells)
2. Runs BFS and A* on each grid **5 times** (fixed seeds 42–46)
3. Records average runtime (ms) and nodes explored
4. Cross-checks that both algorithms return **identical path lengths**
5. Writes `benchmark_results.csv`
6. Saves `benchmark_plot.png` (runtime + nodes-explored, log–log axes) if matplotlib is installed

No pygame or game code is needed; the benchmark is fully standalone.

## Project Structure

```
.
├── main.py          # Entry point — initialises pygame, loops menu → game
├── game.py          # Main game loop; selects pathfinding function
├── bfs.py           # Algorithm B: Breadth-First Search + obstacle generator
├── astar.py         # Algorithm A: A* with Manhattan distance heuristic
├── enemy.py         # Enemy entity; stores and uses selected pathfind_fn
├── tower.py         # Tower and Bullet entities
├── ui.py            # draw_grid, draw_header, draw_settings_popup
├── menu.py          # Main menu with BFS / A* selection
├── settings.py      # Grid constants, colours, pygame init helpers
├── benchmark.py     # Standalone BFS vs A* benchmark (no pygame)
├── images/
│   └── burning_baby.jpeg
└── sounds/
    ├── shoot.mp3
    ├── lives_lost.mp3
    └── game_over.mp3
```

## Algorithms

### A — A\* (astar.py)

Uses a min-heap ordered by **f(n) = g(n) + h(n)** where:
- `g(n)` = steps from start to *n* (each step costs 1)
- `h(n)` = Manhattan distance to goal (admissible — never overestimates)

Because *h* is admissible, A\* is guaranteed to find an optimal path. On this unweighted grid the optimal length equals BFS's result — verified by the benchmark cross-check.

Worst-case time: **O(E log V)** — each of the ≤ E heap pushes costs O(log V).  
Space: **O(V)**.

### B — BFS (bfs.py)

Standard FIFO-queue BFS on the 4-connected grid. Expands nodes in order of hop-distance, so the first time the goal is reached the path is guaranteed shortest.

Time: **O(V + E)** — each vertex and edge visited at most once.  
Space: **O(V)**.

### Trade-off

On an obstacle-free grid A\* explores only the narrow corridor toward the goal (proportional to path length), while BFS fans out in all directions. As obstacle density increases, A\*'s advantage shrinks because it must explore detours, but it still visits significantly fewer nodes than BFS in practice (confirmed empirically in `benchmark_plot.png`).

## Attribution

- **pygame** — https://www.pygame.org/ (LGPL 2.1)
- **matplotlib** — https://matplotlib.org/ (PSF-compatible)
- Sound effects: royalty-free assets
- `burning_baby.jpeg`: original artwork
