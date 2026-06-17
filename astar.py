import heapq
from settings import ROWS, COLS


def heuristic(a, b):
    """Manhattan distance — admissible heuristic for 4-directional grid movement."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, end):
    """A* pathfinding with Manhattan distance heuristic.

    Same interface as bfs(): returns a list of (row, col) tuples representing
    the shortest path from start to end, or None if the goal is unreachable.

    Grid cell values: 0 = passable grass, 1 = tower (blocked), 2 = obstacle (blocked).

    A* maintains two scores per node:
      g(n) = actual cost from start to n (each step costs 1)
      f(n) = g(n) + h(n)  where h is the Manhattan heuristic

    The closed set prevents re-expanding already-settled nodes.
    Because h is admissible (never overestimates), A* is guaranteed to find
    an optimal path — identical length to BFS on this unweighted grid.
    """
    open_set = []
    counter = 0  # tie-breaker to keep heap comparisons stable
    heapq.heappush(open_set, (heuristic(start, end), counter, start))

    came_from = {start: None}
    g_score = {start: 0}
    closed = set()

    while open_set:
        _, _, current = heapq.heappop(open_set)

        if current in closed:
            continue
        closed.add(current)

        if current == end:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < ROWS and 0 <= nc < COLS
                    and (nr, nc) not in closed
                    and grid[nr][nc] != 1
                    and grid[nr][nc] != 2):
                neighbor = (nr, nc)
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, end)
                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))

    return None
