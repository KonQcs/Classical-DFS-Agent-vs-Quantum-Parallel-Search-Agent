"""Tests for DFS and quantum-inspired agents."""

from __future__ import annotations

import unittest

from maze_agents.agents import (
    DFSAgent,
    QuantumInspiredAgent,
    QuantumInspiredParallelSearchAgent,
)
from maze_agents.main import create_sample_maze
from maze_agents.maze import Maze, Position


def assert_valid_path(test_case: unittest.TestCase, maze: Maze, path: list[Position]) -> None:
    test_case.assertTrue(path)
    test_case.assertEqual(path[0], maze.start)
    test_case.assertEqual(path[-1], maze.exit)

    for current, next_position in zip(path, path[1:]):
        test_case.assertIn(next_position, maze.get_neighbors(current))


class AgentTests(unittest.TestCase):
    def test_dfs_finds_a_valid_path(self) -> None:
        maze = Maze.sample()
        result = DFSAgent().solve(maze)

        self.assertTrue(result.found)
        assert_valid_path(self, maze, result.path)
        self.assertGreaterEqual(result.explored_count, len(result.path))
        self.assertEqual(result.metrics.explored_nodes, result.explored_count)
        self.assertGreaterEqual(result.metrics.execution_time, 0)

    def test_dfs_uses_stack_based_backtracking(self) -> None:
        maze = Maze(
            [
                ["S", 0, 1],
                [0, 1, 1],
                [0, 0, "E"],
            ]
        )

        result = DFSAgent().solve(maze)

        self.assertTrue(result.found)
        assert_valid_path(self, maze, result.path)
        self.assertNotIn((0, 1), result.path)
        self.assertIn((0, 1), result.visited_order)
        self.assertLess(
            result.visited_order.index((0, 1)),
            result.visited_order.index((1, 0)),
        )
        self.assertGreaterEqual(result.metrics.max_stack_size, 1)
        self.assertGreaterEqual(result.metrics.dead_ends, 1)

    def test_quantum_agent_finds_a_valid_path(self) -> None:
        maze = Maze.sample()
        result = QuantumInspiredAgent().solve(maze)

        self.assertTrue(result.found)
        assert_valid_path(self, maze, result.path)
        self.assertGreater(result.frontier_peak, 0)
        self.assertEqual(result.metrics.path_length, result.path_length)
        self.assertGreater(result.metrics.total_parallel_iterations, 0)

    def test_quantum_agent_finds_shortest_path_in_unweighted_maze(self) -> None:
        maze = Maze(
            [
                ["S", 0, 0, 0, "E"],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 0, 0],
            ]
        )

        result = QuantumInspiredAgent().solve(maze)

        self.assertTrue(result.found)
        assert_valid_path(self, maze, result.path)
        self.assertEqual(result.path_length, 4)
        self.assertEqual(result.metrics.path_length, 4)
        self.assertGreaterEqual(result.metrics.max_active_paths, 2)

    def test_agents_report_no_path_when_exit_is_unreachable(self) -> None:
        maze = Maze(
            [
                ["S", 1],
                [1, "E"],
            ]
        )

        for agent in (DFSAgent(), QuantumInspiredParallelSearchAgent()):
            result = agent.solve(maze)
            self.assertFalse(result.found)
            self.assertEqual(result.path, [])

    def test_agents_return_valid_paths_for_demo_maze(self) -> None:
        maze = create_sample_maze()

        for agent in (DFSAgent(), QuantumInspiredAgent()):
            result = agent.solve(maze)
            self.assertTrue(result.found)
            assert_valid_path(self, maze, result.path)


if __name__ == "__main__":
    unittest.main()
