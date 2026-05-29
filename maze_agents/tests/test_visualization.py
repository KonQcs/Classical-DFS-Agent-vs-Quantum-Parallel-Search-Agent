"""Tests for matplotlib visualization helpers."""

from __future__ import annotations

import unittest

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from maze_agents.main import create_sample_maze, run_agents
from maze_agents.visualization import (
    compare_paths,
    draw_maze,
    draw_path,
    draw_visited_order,
)


class VisualizationTests(unittest.TestCase):
    def tearDown(self) -> None:
        plt.close("all")

    def test_visualization_helpers_render_figures(self) -> None:
        maze = create_sample_maze()
        dfs_result, quantum_result = run_agents(maze)

        maze_figure, maze_axis = draw_maze(maze)
        path_figure, path_axis = draw_path(maze, dfs_result.path, "DFS path")
        visited_figure, visited_axis = draw_visited_order(
            maze,
            dfs_result.visited_order,
            "DFS visited order",
        )
        comparison_figure, comparison_axes = compare_paths(
            maze,
            dfs_result.path,
            quantum_result.path,
        )

        for figure in (maze_figure, path_figure, visited_figure, comparison_figure):
            figure.canvas.draw()

        self.assertEqual(maze_axis.get_title(), "Maze")
        self.assertEqual(path_axis.get_title(), "DFS path")
        self.assertEqual(visited_axis.get_title(), "DFS visited order")
        self.assertEqual(comparison_axes[0].get_title(), "DFS path")
        self.assertEqual(comparison_axes[1].get_title(), "Quantum-inspired path")


if __name__ == "__main__":
    unittest.main()
