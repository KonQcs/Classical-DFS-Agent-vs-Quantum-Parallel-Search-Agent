"""Executable demo for comparing maze-solving agents."""

from __future__ import annotations

import argparse

from maze_agents.agents import DFSAgent, QuantumInspiredAgent
from maze_agents.maze_generator import generate_random_maze
from maze_agents.maze import Maze, Position
from maze_agents.metrics import SearchMetrics, SearchResult, compare_results


def create_sample_maze() -> Maze:
    """Create a maze with walls, crossroads, dead ends, and one exit cell."""

    return Maze(
        [
            ["S", 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 1, 0],
            [1, 1, 0, 1, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, "E"],
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Compare DFS and quantum-inspired maze-solving agents."
    )
    parser.add_argument(
        "--maze-file",
        help="Optional text maze file using 0/space/./1/#/S/E characters.",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use the fixed demo maze instead of generating a random maze.",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Generate a random maze. This is the default when no maze file is used.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=20,
        help="Random maze width. Minimum: 5. Default: 15.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=20,
        help="Random maze height. Minimum: 5. Default: 15.",
    )
    parser.add_argument(
        "--complexity",
        type=float,
        default=0.7,
        help="Random maze complexity from 0.0 to 1.0. Higher means more walls/dead ends.",
    )
    parser.add_argument(
        "--loop-factor",
        type=float,
        default=0.0,
        help="Random maze loop factor from 0.0 to 1.0. Higher means more alternate paths.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional random seed. Use this to reproduce the same maze.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Print results without opening matplotlib visualizations.",
    )
    parser.add_argument(
        "--show-visited-order",
        action="store_true",
        help="Also show each agent's visited-order visualization.",
    )
    return parser


def load_maze(args: argparse.Namespace) -> Maze:
    """Load a maze from a file, the fixed sample, or random generation."""

    if args.sample and args.random:
        raise ValueError("Use either --sample or --random, not both")
    if args.maze_file and (args.sample or args.random):
        raise ValueError("Use either --maze-file, --sample, or --random, not together")
    if args.sample:
        return create_sample_maze()
    if args.maze_file is None:
        return generate_random_maze(
            width=args.width,
            height=args.height,
            complexity=args.complexity,
            loop_factor=args.loop_factor,
            seed=args.seed,
        )

    with open(args.maze_file, encoding="utf-8") as maze_file:
        return Maze.from_lines(maze_file)


def run_agents(maze: Maze) -> tuple[SearchResult, SearchResult]:
    """Run DFS first, then the quantum-inspired agent."""

    dfs_result = DFSAgent().solve(maze)
    quantum_result = QuantumInspiredAgent().solve(maze)
    return dfs_result, quantum_result


def print_result(result: SearchResult) -> None:
    """Print one agent's final path and metrics."""

    print(f"\n{result.agent_name}")
    print("-" * len(result.agent_name))
    print(f"Final path: {_format_path(result.path)}")
    print(_format_metrics(result.metrics))


def show_visualizations(
    maze: Maze,
    dfs_result: SearchResult,
    quantum_result: SearchResult,
    *,
    show_visited_order: bool,
) -> None:
    """Open matplotlib visualizations for the two agent results."""

    try:
        import matplotlib.pyplot as plt

        from maze_agents.visualization import (
            compare_paths,
            draw_path,
            draw_visited_order,
        )
    except ModuleNotFoundError as exc:
        if exc.name == "matplotlib":
            print(
                "\nVisualization skipped: matplotlib is not installed. "
                "Install it with: python -m pip install -r requirements.txt"
            )
            return
        raise

    draw_path(maze, dfs_result.path, "DFS path")
    draw_path(maze, quantum_result.path, "Quantum-inspired path")
    compare_paths(maze, dfs_result.path, quantum_result.path)

    if show_visited_order:
        draw_visited_order(maze, dfs_result.visited_order, "DFS visited order")
        draw_visited_order(
            maze,
            quantum_result.visited_order,
            "Quantum-inspired visited order",
        )

    plt.show()


def main() -> None:
    """Run the full comparison demo."""

    args = build_parser().parse_args()
    try:
        maze = load_maze(args)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    dfs_result, quantum_result = run_agents(maze)

    print(_format_maze_source(args))
    print_result(dfs_result)
    print_result(quantum_result)

    print("\nComparison")
    print("----------")
    print(compare_results(dfs_result, quantum_result))

    if not args.no_show:
        show_visualizations(
            maze,
            dfs_result,
            quantum_result,
            show_visited_order=args.show_visited_order,
        )


def _format_path(path: list[Position]) -> str:
    if not path:
        return "No path found"
    return " -> ".join(f"({row}, {col})" for row, col in path)


def _format_maze_source(args: argparse.Namespace) -> str:
    if args.maze_file:
        return f"Maze source: file ({args.maze_file})"
    if args.sample:
        return "Maze source: fixed sample"
    seed_text = "random" if args.seed is None else str(args.seed)
    return (
        "Maze source: random "
        f"(width={args.width}, height={args.height}, complexity={args.complexity}, "
        f"loop_factor={args.loop_factor}, seed={seed_text})"
    )


def _format_metrics(metrics: SearchMetrics) -> str:
    lines = [
        "Metrics:",
        f"  found path length: {metrics.path_length}",
        f"  explored_nodes: {metrics.explored_nodes}",
        f"  execution_time: {metrics.execution_time:.6f}s",
    ]

    if metrics.total_parallel_iterations == 0:
        lines.extend(
            [
                f"  total_steps: {metrics.total_steps}",
                f"  max_stack_size: {metrics.max_stack_size}",
                f"  dead_ends: {metrics.dead_ends}",
            ]
        )

    if metrics.max_active_paths:
        lines.extend(
            [
                f"  total_parallel_iterations: {metrics.total_parallel_iterations}",
                f"  max_active_paths: {metrics.max_active_paths}",
            ]
        )

    return "\n".join(lines)


if __name__ == "__main__":
    main()
