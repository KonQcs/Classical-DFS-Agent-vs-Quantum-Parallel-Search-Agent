"""Search result dataclasses and comparison reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from maze_agents.search_types import SearchPosition


@dataclass(frozen=True)
class SearchMetrics:
    """Metrics collected by a maze-solving agent."""

    explored_nodes: int
    execution_time: float
    path_length: int
    total_steps: int = 0
    max_stack_size: int = 0
    dead_ends: int = 0
    total_parallel_iterations: int = 0
    max_active_paths: int = 0

    @property
    def memory_proxy(self) -> int:
        """Return the agent-specific memory pressure indicator."""

        return max(self.max_stack_size, self.max_active_paths)


@dataclass(frozen=True)
class SearchResult:
    """Outcome returned by a maze-solving agent."""

    path: list[SearchPosition]
    found: bool
    metrics: SearchMetrics
    visited_order: list[SearchPosition]
    agent_name: str = "Unknown agent"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def path_length(self) -> int:
        """Number of moves in the solution path."""

        return self.metrics.path_length

    @property
    def explored_count(self) -> int:
        """Number of unique cells explored by the agent."""

        return self.metrics.explored_nodes

    @property
    def frontier_peak(self) -> int:
        """Maximum stack size or active path count reached."""

        return self.metrics.memory_proxy

    @property
    def elapsed_seconds(self) -> float:
        """Search execution time in seconds."""

        return self.metrics.execution_time


def compare_results(dfs_result: SearchResult, quantum_result: SearchResult) -> str:
    """Return a readable comparison table for DFS and quantum-inspired search."""

    rows = [
        ["Metric", "DFS", "Quantum-inspired"],
        ["Found", _yes_no(dfs_result.found), _yes_no(quantum_result.found)],
        [
            "Path length",
            str(dfs_result.metrics.path_length),
            str(quantum_result.metrics.path_length),
        ],
        [
            "Explored nodes",
            str(dfs_result.metrics.explored_nodes),
            str(quantum_result.metrics.explored_nodes),
        ],
        [
            "Execution time (ms)",
            f"{dfs_result.metrics.execution_time * 1000:.3f}",
            f"{quantum_result.metrics.execution_time * 1000:.3f}",
        ],
        [
            "Memory proxy",
            f"max_stack_size={dfs_result.metrics.max_stack_size}",
            f"max_active_paths={quantum_result.metrics.max_active_paths}",
        ],
    ]
    return _format_table(rows)


def format_metrics(results: list[SearchResult]) -> str:
    """Return a simple aligned metrics table for one or more agents."""

    rows = [["Agent", "Found", "Path", "Explored", "Memory proxy", "Time (ms)"]]
    for result in results:
        rows.append(
            [
                result.agent_name,
                _yes_no(result.found),
                str(result.metrics.path_length),
                str(result.metrics.explored_nodes),
                str(result.metrics.memory_proxy),
                f"{result.metrics.execution_time * 1000:.3f}",
            ]
        )
    return _format_table(rows)


def _format_table(rows: list[list[str]]) -> str:
    columns = list(zip(*rows, strict=True))
    widths = [max(len(value) for value in column) for column in columns]

    def format_row(values: list[str]) -> str:
        return "  ".join(value.ljust(width) for value, width in zip(values, widths))

    separator = "  ".join("-" * width for width in widths)
    formatted_rows = [format_row(row) for row in rows[1:]]
    return "\n".join([format_row(rows[0]), separator, *formatted_rows])


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"
