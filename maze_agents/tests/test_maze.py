"""Tests for maze validation and traversal."""

from __future__ import annotations

import unittest

from maze_agents.maze import Maze


class MazeTests(unittest.TestCase):
    def test_sample_maze_has_start_exit_and_dimensions(self) -> None:
        maze = Maze.sample()

        self.assertEqual(maze.start, (0, 0))
        self.assertEqual(maze.exit, (4, 5))
        self.assertEqual(maze.height, 5)
        self.assertEqual(maze.width, 6)

    def test_get_neighbors_returns_only_walkable_cells(self) -> None:
        maze = Maze(
            [
                ["S", 0, 1],
                [1, 0, "E"],
            ]
        )

        self.assertEqual(maze.get_neighbors((0, 0)), [(0, 1)])
        self.assertEqual(set(maze.get_neighbors((0, 1))), {(1, 1), (0, 0)})

    def test_supports_four_direction_movement(self) -> None:
        maze = Maze(
            [
                [0, 0, 0],
                [0, "S", 0],
                [0, "E", 0],
            ]
        )

        self.assertEqual(
            set(maze.get_neighbors((1, 1))),
            {(0, 1), (1, 2), (2, 1), (1, 0)},
        )

    def test_in_bounds_identifies_valid_positions(self) -> None:
        maze = Maze([["S", 0], [1, "E"]])

        self.assertTrue(maze.in_bounds((0, 0)))
        self.assertTrue(maze.in_bounds((1, 1)))
        self.assertFalse(maze.in_bounds((-1, 0)))
        self.assertFalse(maze.in_bounds((0, 2)))

    def test_is_walkable_rejects_walls_and_out_of_bounds(self) -> None:
        maze = Maze([["S", 1], [0, "E"]])

        self.assertTrue(maze.is_walkable((0, 0)))
        self.assertTrue(maze.is_walkable((1, 1)))
        self.assertFalse(maze.is_walkable((0, 1)))
        self.assertFalse(maze.is_walkable((2, 0)))

    def test_is_exit_identifies_exit_cell(self) -> None:
        maze = Maze([["S", 0], [0, "E"]])

        self.assertTrue(maze.is_exit((1, 1)))
        self.assertFalse(maze.is_exit((0, 0)))

    def test_rejects_non_rectangular_grid(self) -> None:
        with self.assertRaisesRegex(ValueError, "rectangular"):
            Maze([["S", 0], [0, "E", 0]])

    def test_rejects_missing_start(self) -> None:
        with self.assertRaisesRegex(ValueError, "'S'"):
            Maze([[0, 0], [0, "E"]])

    def test_rejects_missing_exit(self) -> None:
        with self.assertRaisesRegex(ValueError, "'E'"):
            Maze([["S", 0], [0, 0]])

    def test_rejects_multiple_starts(self) -> None:
        with self.assertRaisesRegex(ValueError, "'S'"):
            Maze([["S", 0], [0, "S"], [0, "E"]])

    def test_rejects_multiple_exits(self) -> None:
        with self.assertRaisesRegex(ValueError, "'E'"):
            Maze([["S", "E"], [0, "E"]])

    def test_from_lines_parses_text_maze(self) -> None:
        maze = Maze.from_lines(["S.1", "001", "00E"])

        self.assertEqual(maze.grid[0], ("S", 0, 1))
        self.assertEqual(maze.exit, (2, 2))


if __name__ == "__main__":
    unittest.main()
