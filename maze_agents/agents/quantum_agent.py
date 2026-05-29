"""Quantum-inspired parallel branch expansion maze agent."""

from __future__ import annotations

from time import perf_counter

from maze_agents.maze import Maze, Position
from maze_agents.metrics import SearchMetrics, SearchResult


class QuantumInspiredAgent:
    """Explore all active maze paths as simultaneous branch expansions.

    This is not real quantum computing. It is a quantum-inspired simulation
    where every active path advances one step per iteration. Paths are kept
    independent, and cycles are avoided by preventing a path from revisiting
    cells already contained in that same path.
    """

    name = "Quantum-inspired parallel"

    def solve(self, maze: Maze) -> SearchResult:
        """Find a shortest unweighted path using parallel path expansion."""

        started_at = perf_counter()
        active_paths: list[list[Position]] = [[maze.start]]
        visited_order: list[Position] = [maze.start]
        explored_nodes: set[Position] = {maze.start}
        max_active_paths = len(active_paths)
        total_parallel_iterations = 0

        while active_paths:
            next_active_paths: list[list[Position]] = []
            total_parallel_iterations += 1

            for path in active_paths:
                current_position = path[-1]
                if maze.is_exit(current_position):
                    return self._build_result(
                        path=path,
                        found=True,
                        visited_order=visited_order,
                        explored_nodes=explored_nodes,
                        total_parallel_iterations=total_parallel_iterations - 1,
                        max_active_paths=max_active_paths,
                        started_at=started_at,
                    )

                for neighbor in maze.get_neighbors(current_position):
                    if neighbor in path:
                        continue

                    expanded_path = [*path, neighbor]
                    visited_order.append(neighbor)
                    explored_nodes.add(neighbor)

                    if maze.is_exit(neighbor):
                        return self._build_result(
                            path=expanded_path,
                            found=True,
                            visited_order=visited_order,
                            explored_nodes=explored_nodes,
                            total_parallel_iterations=total_parallel_iterations,
                            max_active_paths=max_active_paths,
                            started_at=started_at,
                        )

                    next_active_paths.append(expanded_path)

            active_paths = next_active_paths
            max_active_paths = max(max_active_paths, len(active_paths))

        return self._build_result(
            path=[],
            found=False,
            visited_order=visited_order,
            explored_nodes=explored_nodes,
            total_parallel_iterations=total_parallel_iterations,
            max_active_paths=max_active_paths,
            started_at=started_at,
        )

    def _build_result(
        self,
        *,
        path: list[Position],
        found: bool,
        visited_order: list[Position],
        explored_nodes: set[Position],
        total_parallel_iterations: int,
        max_active_paths: int,
        started_at: float,
    ) -> SearchResult:
        """Build a shared search result with quantum-specific metrics."""

        return SearchResult(
            path=path,
            found=found,
            metrics=SearchMetrics(
                explored_nodes=len(explored_nodes),
                execution_time=perf_counter() - started_at,
                path_length=max(0, len(path) - 1),
                total_steps=len(visited_order),
                total_parallel_iterations=total_parallel_iterations,
                max_active_paths=max_active_paths,
            ),
            visited_order=visited_order,
            agent_name=self.name,
            metadata={"strategy": "parallel active-path expansion"},
        )


QuantumInspiredParallelSearchAgent = QuantumInspiredAgent
