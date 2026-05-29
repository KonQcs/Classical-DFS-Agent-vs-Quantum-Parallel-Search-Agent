"""Executable demo for comparing maze-solving agents."""

from __future__ import annotations

import argparse
from typing import cast

from maze_agents.agents import DFSAgent, QuantumInspiredAgent
from maze_agents.maze import Maze, Position
from maze_agents.maze3d import Maze3D, Position3D
from maze_agents.maze_generator import generate_random_maze, generate_random_maze_3d
from maze_agents.metrics import SearchMetrics, SearchResult, compare_results
from maze_agents.search_types import SearchPosition, SearchableMaze


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


def create_sample_maze_3d() -> Maze3D:
    """Create a compact fixed 3D demo maze."""

    return Maze3D.sample()


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
        "--dimension",
        choices=("2d", "3d"),
        default="2d",
        help="Choose whether to run a 2D or 3D maze. Default: 2d.",
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
        "--depth",
        type=int,
        default=20,
        help="Random 3D maze depth/levels. Minimum: 3. Used only with --dimension 3d.",
    )
    parser.add_argument(
        "--complexity",
        type=float,
        default=0.85,
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
    parser.add_argument(
        "--interactive-3d",
        action="store_true",
        help=(
            "For 3D runs, try to open a native matplotlib window "
            "with mouse rotate, pan, and zoom support."
        ),
    )
    parser.add_argument(
        "--hide-3d-free-cells",
        action="store_true",
        help="For 3D runs, hide the translucent free-cell map volume.",
    )
    parser.add_argument(
        "--hide-3d-free-cell-links",
        action="store_true",
        help="For 3D runs, hide the thin lines connecting neighboring free cells.",
    )
    parser.add_argument(
        "--hide-3d-walls",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--show-3d-walls",
        action="store_true",
        help="For 3D runs, show wall markers. Hidden by default.",
    )
    return parser


def load_maze(args: argparse.Namespace) -> Maze | Maze3D:
    """Load a maze from a file, the fixed sample, or random generation."""

    if args.sample and args.random:
        raise ValueError("Use either --sample or --random, not both")
    if args.maze_file and (args.sample or args.random):
        raise ValueError("Use either --maze-file, --sample, or --random, not together")
    if args.maze_file and args.dimension == "3d":
        raise ValueError("--maze-file currently supports only 2D text mazes")
    if args.sample:
        if args.dimension == "3d":
            return create_sample_maze_3d()
        return create_sample_maze()
    if args.maze_file is None:
        if args.dimension == "3d":
            return generate_random_maze_3d(
                width=args.width,
                height=args.height,
                depth=args.depth,
                complexity=args.complexity,
                loop_factor=args.loop_factor,
                seed=args.seed,
            )
        return generate_random_maze(
            width=args.width,
            height=args.height,
            complexity=args.complexity,
            loop_factor=args.loop_factor,
            seed=args.seed,
        )

    with open(args.maze_file, encoding="utf-8") as maze_file:
        return Maze.from_lines(maze_file)


def run_agents(maze: SearchableMaze) -> tuple[SearchResult, SearchResult]:
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
    maze: Maze | Maze3D,
    dfs_result: SearchResult,
    quantum_result: SearchResult,
    *,
    show_visited_order: bool,
    interactive_3d: bool,
    show_3d_free_cells: bool,
    show_3d_walls: bool,
    show_3d_free_cell_links: bool,
) -> None:
    """Open matplotlib visualizations for the two agent results."""

    try:
        if interactive_3d and isinstance(maze, Maze3D):
            _enable_interactive_matplotlib_backend()
        import matplotlib.pyplot as plt

        from maze_agents.visualization import (
            compare_paths,
            compare_paths_3d,
            draw_path,
            draw_path_3d,
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

    if isinstance(maze, Maze3D):
        dfs_path_3d = cast(list[Position3D], dfs_result.path)
        quantum_path_3d = cast(list[Position3D], quantum_result.path)
        draw_path_3d(
            maze,
            dfs_path_3d,
            "DFS 3D path",
            show_free_cells=show_3d_free_cells,
            show_walls=show_3d_walls,
            show_free_cell_links=show_3d_free_cell_links,
        )
        draw_path_3d(
            maze,
            quantum_path_3d,
            "Quantum-inspired 3D path",
            show_free_cells=show_3d_free_cells,
            show_walls=show_3d_walls,
            show_free_cell_links=show_3d_free_cell_links,
        )
        compare_paths_3d(
            maze,
            dfs_path_3d,
            quantum_path_3d,
            show_free_cells=show_3d_free_cells,
            show_walls=show_3d_walls,
            show_free_cell_links=show_3d_free_cell_links,
        )
        if show_visited_order:
            print("\nVisited-order plots are currently shown only for 2D mazes.")
        if interactive_3d:
            print(
                "\nInteractive 3D requested. In the native matplotlib window, "
                "drag to rotate and use the toolbar/mouse wheel for pan and zoom."
            )
        plt.show()
        return

    dfs_path_2d = cast(list[Position], dfs_result.path)
    quantum_path_2d = cast(list[Position], quantum_result.path)
    draw_path(maze, dfs_path_2d, "DFS path")
    draw_path(maze, quantum_path_2d, "Quantum-inspired path")
    compare_paths(maze, dfs_path_2d, quantum_path_2d)

    if show_visited_order:
        dfs_visited_2d = cast(list[Position], dfs_result.visited_order)
        quantum_visited_2d = cast(list[Position], quantum_result.visited_order)
        draw_visited_order(maze, dfs_visited_2d, "DFS visited order")
        draw_visited_order(
            maze,
            quantum_visited_2d,
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
            interactive_3d=args.interactive_3d,
            show_3d_free_cells=not args.hide_3d_free_cells,
            show_3d_walls=args.show_3d_walls and not args.hide_3d_walls,
            show_3d_free_cell_links=not args.hide_3d_free_cell_links,
        )


def _format_path(path: list[SearchPosition]) -> str:
    if not path:
        return "No path found"
    return " -> ".join(_format_position(position) for position in path)


def _format_maze_source(args: argparse.Namespace) -> str:
    if args.maze_file:
        return f"Maze source: file ({args.maze_file})"
    if args.sample:
        return f"Maze source: fixed {args.dimension.upper()} sample"
    seed_text = "random" if args.seed is None else str(args.seed)
    if args.dimension == "3d":
        return (
            "Maze source: random 3D "
            f"(width={args.width}, height={args.height}, depth={args.depth}, "
            f"complexity={args.complexity}, loop_factor={args.loop_factor}, "
            f"seed={seed_text})"
        )
    return (
        "Maze source: random 2D "
        f"(width={args.width}, height={args.height}, complexity={args.complexity}, "
        f"loop_factor={args.loop_factor}, seed={seed_text})"
    )


def _format_position(position: SearchPosition) -> str:
    return "(" + ", ".join(str(value) for value in position) + ")"


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


def _enable_interactive_matplotlib_backend() -> None:
    try:
        import matplotlib

        matplotlib.use("TkAgg", force=True)
    except (ImportError, ModuleNotFoundError, RuntimeError) as exc:
        print(
            "\nCould not enable the TkAgg interactive backend. "
            "Falling back to the current matplotlib backend. "
            f"Reason: {exc}"
        )


if __name__ == "__main__":
    main()
