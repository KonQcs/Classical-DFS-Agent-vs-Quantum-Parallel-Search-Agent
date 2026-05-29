"""Matplotlib visualization helpers for maze-solving results."""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure

from maze_agents.maze import Maze, Position
from maze_agents.metrics import SearchResult


def draw_maze(maze: Maze) -> tuple[Figure, Axes]:
    """Draw the maze with walls, free cells, start, and exit."""

    figure, axis = plt.subplots(figsize=_figure_size(maze))
    _draw_base_maze(axis, maze, title="Maze")
    figure.tight_layout()
    return figure, axis


def draw_path(maze: Maze, path: Sequence[Position], title: str) -> tuple[Figure, Axes]:
    """Draw a maze with a final path overlaid."""

    figure, axis = plt.subplots(figsize=_figure_size(maze))
    _draw_base_maze(axis, maze, title=title)
    _draw_path_overlay(axis, path, color="#f28e2b", label="Path")
    figure.tight_layout()
    return figure, axis


def draw_visited_order(
    maze: Maze,
    visited_order: Sequence[Position],
    title: str,
) -> tuple[Figure, Axes]:
    """Draw the order in which cells were visited."""

    figure, axis = plt.subplots(figsize=_figure_size(maze))
    _draw_base_maze(axis, maze, title=title)
    _draw_visited_overlay(axis, visited_order)
    figure.tight_layout()
    return figure, axis


def compare_paths(
    maze: Maze,
    dfs_path: Sequence[Position],
    quantum_path: Sequence[Position],
) -> tuple[Figure, tuple[Axes, Axes]]:
    """Draw DFS and quantum-inspired final paths side by side."""

    figure, axes = plt.subplots(1, 2, figsize=(12, 6), squeeze=False)
    dfs_axis = cast(Axes, axes[0][0])
    quantum_axis = cast(Axes, axes[0][1])

    _draw_base_maze(dfs_axis, maze, title="DFS path")
    _draw_path_overlay(dfs_axis, dfs_path, color="#f28e2b", label="DFS")

    _draw_base_maze(quantum_axis, maze, title="Quantum-inspired path")
    _draw_path_overlay(quantum_axis, quantum_path, color="#4e79a7", label="Quantum")

    figure.tight_layout()
    return figure, (dfs_axis, quantum_axis)


def show_comparison(maze: Maze, results: Sequence[SearchResult]) -> None:
    """Display a visual comparison for existing SearchResult callers."""

    if len(results) < 2:
        for result in results:
            draw_path(maze, result.path, result.agent_name)
        plt.show()
        return

    compare_paths(maze, results[0].path, results[1].path)
    plt.show()


def _draw_base_maze(axis: Axes, maze: Maze, *, title: str) -> None:
    axis.imshow(maze.to_numeric_grid(), cmap=ListedColormap(["white", "black"]))
    axis.set_title(title)
    axis.set_xticks(range(maze.width))
    axis.set_yticks(range(maze.height))
    axis.set_xticks([col - 0.5 for col in range(1, maze.width)], minor=True)
    axis.set_yticks([row - 0.5 for row in range(1, maze.height)], minor=True)
    axis.grid(which="minor", color="#d0d0d0", linewidth=0.8)
    axis.tick_params(
        which="both",
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False,
    )

    _scatter_cells(axis, [maze.start], color="#59a14f", marker="o", size=170)
    _scatter_cells(axis, [maze.exit], color="#e15759", marker="*", size=260)


def _draw_path_overlay(
    axis: Axes,
    path: Sequence[Position],
    *,
    color: str,
    label: str,
) -> None:
    if not path:
        return

    rows = [row for row, _ in path]
    cols = [col for _, col in path]
    axis.plot(cols, rows, color=color, linewidth=3, label=label)
    _scatter_cells(axis, path, color=color, marker="o", size=48)
    axis.legend(loc="upper right")


def _draw_visited_overlay(axis: Axes, visited_order: Sequence[Position]) -> None:
    if not visited_order:
        return

    _scatter_cells(axis, visited_order, color="#9ecae1", marker="s", size=150)
    for index, (row, col) in enumerate(visited_order, start=1):
        axis.text(
            col,
            row,
            str(index),
            ha="center",
            va="center",
            fontsize=8,
            color="#1f2933",
        )


def _scatter_cells(
    axis: Axes,
    positions: Sequence[Position],
    *,
    color: str,
    marker: str,
    size: int,
) -> None:
    if not positions:
        return

    rows = [row for row, _ in positions]
    cols = [col for _, col in positions]
    axis.scatter(cols, rows, c=color, marker=marker, s=size)


def _figure_size(maze: Maze) -> tuple[float, float]:
    width = max(5.0, maze.width * 0.9)
    height = max(5.0, maze.height * 0.9)
    return width, height
