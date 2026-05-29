"""Tests for random maze generation."""

from __future__ import annotations

import unittest

from maze_agents.agents import DFSAgent, QuantumInspiredAgent
from maze_agents.maze_generator import generate_random_maze


def _wall_count(maze_grid: tuple[tuple[int | str, ...], ...]) -> int:
    return sum(1 for row in maze_grid for cell in row if cell == 1)


class MazeGeneratorTests(unittest.TestCase):
    def test_random_maze_has_requested_dimensions_and_is_solvable(self) -> None:
        maze = generate_random_maze(width=11, height=9, complexity=0.9, seed=42)

        self.assertEqual(maze.width, 11)
        self.assertEqual(maze.height, 9)

        for agent in (DFSAgent(), QuantumInspiredAgent()):
            result = agent.solve(maze)
            self.assertTrue(result.found)
            self.assertEqual(result.path[0], maze.start)
            self.assertEqual(result.path[-1], maze.exit)

    def test_same_seed_produces_same_maze(self) -> None:
        first = generate_random_maze(width=13, height=13, seed=123)
        second = generate_random_maze(width=13, height=13, seed=123)

        self.assertEqual(first.grid, second.grid)

    def test_different_seeds_can_produce_different_mazes(self) -> None:
        first = generate_random_maze(width=13, height=13, seed=123)
        second = generate_random_maze(width=13, height=13, seed=456)

        self.assertNotEqual(first.grid, second.grid)

    def test_lower_complexity_opens_more_cells_for_same_seed(self) -> None:
        simple = generate_random_maze(width=15, height=15, complexity=0.0, seed=7)
        complex_maze = generate_random_maze(width=15, height=15, complexity=1.0, seed=7)

        self.assertLessEqual(_wall_count(simple.grid), _wall_count(complex_maze.grid))

    def test_loop_factor_opens_more_cells_for_same_seed(self) -> None:
        no_loops = generate_random_maze(width=15, height=15, loop_factor=0.0, seed=7)
        with_loops = generate_random_maze(width=15, height=15, loop_factor=0.5, seed=7)

        self.assertLessEqual(_wall_count(with_loops.grid), _wall_count(no_loops.grid))

    def test_rejects_invalid_generation_arguments(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 5"):
            generate_random_maze(width=4, height=5)
        with self.assertRaisesRegex(ValueError, "complexity"):
            generate_random_maze(complexity=1.5)
        with self.assertRaisesRegex(ValueError, "loop_factor"):
            generate_random_maze(loop_factor=-0.1)


if __name__ == "__main__":
    unittest.main()
