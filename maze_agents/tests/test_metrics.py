"""Tests for search metrics and result comparison."""

from __future__ import annotations

import unittest

from maze_agents.agents import DFSAgent, QuantumInspiredAgent
from maze_agents.maze import Maze
from maze_agents.metrics import SearchMetrics, SearchResult, compare_results


class MetricsTests(unittest.TestCase):
    def test_search_result_uses_search_metrics(self) -> None:
        result = SearchResult(
            path=[(0, 0), (0, 1)],
            found=True,
            metrics=SearchMetrics(
                explored_nodes=2,
                execution_time=0.001,
                path_length=1,
                max_stack_size=1,
            ),
            visited_order=[(0, 0), (0, 1)],
            agent_name="Example",
        )

        self.assertEqual(result.path_length, 1)
        self.assertEqual(result.explored_count, 2)
        self.assertEqual(result.frontier_peak, 1)

    def test_compare_results_includes_required_fields(self) -> None:
        maze = Maze.sample()
        dfs_result = DFSAgent().solve(maze)
        quantum_result = QuantumInspiredAgent().solve(maze)

        comparison = compare_results(dfs_result, quantum_result)

        self.assertIn("Found", comparison)
        self.assertIn("Path length", comparison)
        self.assertIn("Explored nodes", comparison)
        self.assertIn("Execution time", comparison)
        self.assertIn("max_stack_size", comparison)
        self.assertIn("max_active_paths", comparison)


if __name__ == "__main__":
    unittest.main()
