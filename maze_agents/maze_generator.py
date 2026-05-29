"""Random maze generation utilities."""

from __future__ import annotations

import random
from collections import deque

from maze_agents.maze import CellValue, Maze, Position


def generate_random_maze(
    *,
    width: int = 50,
    height: int = 50,
    complexity: float = 0.9,
    loop_factor: float = 0.5,
    seed: int | None = None,
) -> Maze:
    """Generate a solvable random maze.

    ``complexity`` ranges from 0.0 to 1.0. Higher values keep more walls and
    dead ends. Lower values open more connectors and make the maze easier.

    ``loop_factor`` also ranges from 0.0 to 1.0. Higher values open additional
    connectors between paths, creating more alternate routes.
    """

    _validate_generation_args(width, height, complexity, loop_factor)

    rng = random.Random(seed)
    grid: list[list[CellValue]] = [[1 for _ in range(width)] for _ in range(height)]
    start = (1, 1)
    _carve_perfect_maze(grid, start, rng)
    _open_extra_connectors(grid, complexity=complexity, loop_factor=loop_factor, rng=rng)

    exit_position = _find_farthest_walkable_cell(grid, start)
    start_row, start_col = start
    exit_row, exit_col = exit_position
    grid[start_row][start_col] = "S"
    grid[exit_row][exit_col] = "E"
    return Maze(grid)


def _validate_generation_args(
    width: int,
    height: int,
    complexity: float,
    loop_factor: float,
) -> None:
    if width < 5 or height < 5:
        raise ValueError("Random maze width and height must be at least 5")
    if not 0.0 <= complexity <= 1.0:
        raise ValueError("complexity must be between 0.0 and 1.0")
    if not 0.0 <= loop_factor <= 1.0:
        raise ValueError("loop_factor must be between 0.0 and 1.0")


def _carve_perfect_maze(
    grid: list[list[CellValue]],
    start: Position,
    rng: random.Random,
) -> None:
    height = len(grid)
    width = len(grid[0])
    stack = [start]
    start_row, start_col = start
    grid[start_row][start_col] = 0

    while stack:
        row, col = stack[-1]
        candidates: list[tuple[Position, Position]] = []
        for delta_row, delta_col in ((-2, 0), (0, 2), (2, 0), (0, -2)):
            next_row = row + delta_row
            next_col = col + delta_col
            if not (1 <= next_row < height - 1 and 1 <= next_col < width - 1):
                continue
            if grid[next_row][next_col] == 1:
                wall = (row + delta_row // 2, col + delta_col // 2)
                candidates.append((wall, (next_row, next_col)))

        if not candidates:
            stack.pop()
            continue

        wall_position, next_position = rng.choice(candidates)
        wall_row, wall_col = wall_position
        next_row, next_col = next_position
        grid[wall_row][wall_col] = 0
        grid[next_row][next_col] = 0
        stack.append(next_position)


def _open_extra_connectors(
    grid: list[list[CellValue]],
    *,
    complexity: float,
    loop_factor: float,
    rng: random.Random,
) -> None:
    height = len(grid)
    width = len(grid[0])
    open_probability = min(0.65, loop_factor + (1.0 - complexity) * 0.25)

    for row in range(1, height - 1):
        for col in range(1, width - 1):
            if grid[row][col] != 1:
                continue
            if not _connects_existing_paths(grid, (row, col)):
                continue
            if rng.random() <= open_probability:
                grid[row][col] = 0


def _connects_existing_paths(grid: list[list[CellValue]], position: Position) -> bool:
    row, col = position
    vertical = grid[row - 1][col] != 1 and grid[row + 1][col] != 1
    horizontal = grid[row][col - 1] != 1 and grid[row][col + 1] != 1
    return vertical or horizontal


def _find_farthest_walkable_cell(grid: list[list[CellValue]], start: Position) -> Position:
    queue: deque[tuple[Position, int]] = deque([(start, 0)])
    visited = {start}
    farthest = start
    farthest_distance = 0

    while queue:
        position, distance = queue.popleft()
        if distance > farthest_distance:
            farthest = position
            farthest_distance = distance

        row, col = position
        for neighbor in ((row - 1, col), (row, col + 1), (row + 1, col), (row, col - 1)):
            neighbor_row, neighbor_col = neighbor
            if not (0 <= neighbor_row < len(grid) and 0 <= neighbor_col < len(grid[0])):
                continue
            if neighbor in visited or grid[neighbor_row][neighbor_col] == 1:
                continue
            visited.add(neighbor)
            queue.append((neighbor, distance + 1))

    return farthest
