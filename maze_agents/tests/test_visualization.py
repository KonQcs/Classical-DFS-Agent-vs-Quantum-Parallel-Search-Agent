"""Tests for matplotlib visualization helpers."""

from __future__ import annotations

import unittest

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from maze_agents.main import create_sample_maze, create_sample_maze_3d, run_agents
from maze_agents.visualization import (
    compare_paths,
    compare_paths_3d,
    draw_maze,
    draw_maze_3d,
    draw_path,
    draw_path_3d,
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

    def test_3d_visualization_helpers_render_figures(self) -> None:
        maze = create_sample_maze_3d()
        dfs_result, quantum_result = run_agents(maze)

        maze_figure, maze_axis = draw_maze_3d(maze)
        path_figure, path_axis = draw_path_3d(maze, dfs_result.path, "DFS 3D path")
        comparison_figure, comparison_axes = compare_paths_3d(
            maze,
            dfs_result.path,
            quantum_result.path,
        )

        for figure in (maze_figure, path_figure, comparison_figure):
            figure.canvas.draw()

        self.assertEqual(maze_axis.get_title(), "3D maze")
        self.assertEqual(path_axis.get_title(), "DFS 3D path")
        self.assertEqual(comparison_axes[0].get_title(), "DFS 3D path")
        self.assertEqual(comparison_axes[1].get_title(), "Quantum-inspired 3D path")

    def test_3d_visualization_can_hide_free_cell_volume(self) -> None:
        maze = create_sample_maze_3d()

        with_free_cells_figure, with_free_cells_axis = draw_maze_3d(
            maze,
            show_free_cells=True,
        )
        without_free_cells_figure, without_free_cells_axis = draw_maze_3d(
            maze,
            show_free_cells=False,
        )

        with_free_cells_figure.canvas.draw()
        without_free_cells_figure.canvas.draw()

        self.assertGreater(
            len(with_free_cells_axis.collections),
            len(without_free_cells_axis.collections),
        )

    def test_3d_visualization_can_hide_walls(self) -> None:
        maze = create_sample_maze_3d()

        with_walls_figure, with_walls_axis = draw_maze_3d(
            maze,
            show_walls=True,
        )
        without_walls_figure, without_walls_axis = draw_maze_3d(
            maze,
            show_walls=False,
        )

        with_walls_figure.canvas.draw()
        without_walls_figure.canvas.draw()

        self.assertGreater(
            len(with_walls_axis.collections),
            len(without_walls_axis.collections),
        )

    def test_3d_visualization_can_hide_free_cell_links(self) -> None:
        maze = create_sample_maze_3d()

        with_links_figure, with_links_axis = draw_maze_3d(
            maze,
            show_free_cell_links=True,
        )
        without_links_figure, without_links_axis = draw_maze_3d(
            maze,
            show_free_cell_links=False,
        )

        with_links_figure.canvas.draw()
        without_links_figure.canvas.draw()

        self.assertGreater(
            len(with_links_axis.collections),
            len(without_links_axis.collections),
        )


if __name__ == "__main__":
    unittest.main()
