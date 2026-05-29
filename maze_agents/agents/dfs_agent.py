"""Classical depth-first search maze agent."""

from __future__ import annotations

from time import perf_counter

from maze_agents.metrics import SearchMetrics, SearchResult
from maze_agents.search_types import SearchableMaze, SearchPosition


class DFSAgent:
    """Solve a maze with a classical DFS frontier stack."""

    name = "Classical DFS"

    def solve(self, maze: SearchableMaze) -> SearchResult:
        """Find a path from start to exit using stack-backed DFS."""

        started_at = perf_counter()
        stack: list[tuple[SearchPosition, list[SearchPosition]]] = []
        visited: set[SearchPosition] = set()
        visited_order: list[SearchPosition] = []
        dead_ends = 0
        max_stack_size = 0
        position = maze.start
        path = [maze.start]

        while True:
            if position in visited:
                backtracked = self._pop_unvisited_state(stack, visited)
                if backtracked is None:
                    break
                position, path = backtracked
                continue

            visited.add(position)
            visited_order.append(position)

            if maze.is_exit(position):
                return SearchResult(
                    path=path,
                    found=True,
                    metrics=self._build_metrics(
                        started_at=started_at,
                        path=path,
                        visited_order=visited_order,
                        max_stack_size=max_stack_size,
                        dead_ends=dead_ends,
                    ),
                    visited_order=visited_order,
                    agent_name=self.name,
                    metadata={"strategy": "LIFO stack with saved crossroads"},
                )

            unexplored_neighbors = [
                neighbor for neighbor in maze.get_neighbors(position) if neighbor not in visited
            ]
            if unexplored_neighbors:
                next_position = unexplored_neighbors[0]
                alternatives = unexplored_neighbors[1:]
                for alternative in reversed(alternatives):
                    stack.append((alternative, [*path, alternative]))
                max_stack_size = max(max_stack_size, len(stack))
                path = [*path, next_position]
                position = next_position
                continue

            dead_ends += 1
            backtracked = self._pop_unvisited_state(stack, visited)
            if backtracked is None:
                break
            position, path = backtracked

        return SearchResult(
            path=[],
            found=False,
            metrics=self._build_metrics(
                started_at=started_at,
                path=[],
                visited_order=visited_order,
                max_stack_size=max_stack_size,
                dead_ends=dead_ends,
            ),
            visited_order=visited_order,
            agent_name=self.name,
            metadata={"strategy": "LIFO stack with saved crossroads"},
        )

    @staticmethod
    def _pop_unvisited_state(
        stack: list[tuple[SearchPosition, list[SearchPosition]]],
        visited: set[SearchPosition],
    ) -> tuple[SearchPosition, list[SearchPosition]] | None:
        """Return the next saved DFS state that has not already been explored."""

        while stack:
            position, path = stack.pop()
            if position not in visited:
                return position, path
        return None

    @staticmethod
    def _build_metrics(
        *,
        started_at: float,
        path: list[SearchPosition],
        visited_order: list[SearchPosition],
        max_stack_size: int,
        dead_ends: int,
    ) -> SearchMetrics:
        return SearchMetrics(
            explored_nodes=len(set(visited_order)),
            execution_time=perf_counter() - started_at,
            path_length=max(0, len(path) - 1),
            total_steps=len(visited_order),
            max_stack_size=max_stack_size,
            dead_ends=dead_ends,
        )
