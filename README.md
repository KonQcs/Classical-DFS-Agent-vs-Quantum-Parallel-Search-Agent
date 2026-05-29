# Classical DFS Agent vs Quantum-Inspired Parallel Search Agent

## Goal

This project compares two maze-solving strategies on the same 2D grid maze:

- a classical depth-first search agent
- a quantum-inspired parallel branch exploration agent

The goal is to make the behavioral difference visible and measurable. DFS commits to one route and backtracks when needed, while the quantum-inspired agent keeps many possible routes active at the same time.

## Maze Representation

The maze is represented as a 2D grid:

- `0`: free cell
- `1`: wall
- `"S"`: start cell
- `"E"`: exit cell

By default, the project generates a new random maze on each run. The generated maze includes walls, crossroads, dead ends, and exactly one valid exit. A fixed sample maze is also available with `--sample`.

## Classical DFS Agent

The classical DFS agent follows one path as deeply as possible before trying alternatives.

At each crossroad, it stores unexplored alternatives in a stack. If the current path reaches a dead end, the agent pops the most recent saved state from the stack and continues searching from there. This models a traditional depth-first traversal with stack-based backtracking.

DFS is memory-efficient because it usually keeps only a limited stack of alternatives, but it may find a longer path if it explores an unlucky branch first.

## Quantum-Inspired Parallel Search Agent

The quantum-inspired agent simulates parallel branch exploration.

It maintains a list of active paths. In each iteration, every currently active path expands by one step. If any expanded path reaches the exit, the search stops and returns that path.

Because it expands paths level by level, it can find a shortest path in an unweighted maze. It may use more memory than DFS because it keeps multiple active paths at once.

## Not Real Quantum Computing

This project does not perform real quantum computing.

The quantum-inspired agent is a classical simulation inspired by the idea of exploring many branches in parallel. It does not use qubits, superposition, interference, quantum gates, Qiskit, or a quantum backend.

## Installation

Use Python 3.11 or newer.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

The only runtime external dependency is `matplotlib`.

For development and pytest support, install:

```bash
python -m pip install -r requirements-dev.txt
```

## Running the Project

From the project root, run:

```bash
python main.py
```

This generates a new random maze, prints both agents' final paths, their metrics, a comparison table, and then opens matplotlib visualizations.

Run without opening plots:

```bash
python main.py --no-show
```

Use the fixed demo maze:

```bash
python main.py --sample
```

Control the random maze size and complexity:

```bash
python main.py --width 21 --height 21 --complexity 0.9 --loop-factor 0.05
```

Use a seed when you want the same random maze again:

```bash
python main.py --width 21 --height 21 --complexity 0.9 --seed 42
```

Random maze options:

- `--width`: maze width, minimum `5`
- `--height`: maze height, minimum `5`
- `--complexity`: value from `0.0` to `1.0`; higher means more walls and dead ends
- `--loop-factor`: value from `0.0` to `1.0`; higher opens more alternate routes
- `--seed`: optional integer for reproducible maze generation

Also show visited-order visualizations:

```bash
python main.py --show-visited-order
```

Run with a custom text maze:

```bash
python main.py --maze-file path/to/maze.txt
```

Supported custom maze characters:

- `0`, `.`, or space: free cell
- `1` or `#`: wall
- `S`: start
- `E`: exit

## Metrics Compared

The project compares:

- `found`: whether the exit was reached
- `path_length`: number of moves from `S` to `E`
- `explored_nodes`: number of unique cells explored
- `execution_time`: runtime in seconds or milliseconds
- memory proxy:
  - DFS: `max_stack_size`
  - Quantum-inspired: `max_active_paths`

DFS also tracks:

- `total_steps`
- `dead_ends`

The quantum-inspired agent also tracks:

- `total_parallel_iterations`

## Visual Results and Benchmark Snapshots

The following plots were generated from random mazes and saved in the `plots/` directory. They show the final DFS path on the left and the quantum-inspired path on the right.

Because these runs used `seed=random`, the exact maze and timings will vary on future executions unless a fixed `--seed` value is provided.

### 20x20 Maze, Complexity 0.7

![20x20 DFS vs quantum-inspired path comparison](plots/maze_20x20_comparison.png)

Command style:

```bash
python main.py --width 20 --height 20 --complexity 0.7
```

Summary:

| Metric | DFS | Quantum-inspired |
|---|---:|---:|
| Found | yes | yes |
| Path length | 43 | 35 |
| Explored nodes | 46 | 171 |
| Execution time | 0.257 ms | 10.164 ms |
| Memory proxy | max_stack_size=14 | max_active_paths=274 |
| Extra metric | dead_ends=1 | total_parallel_iterations=35 |

In this medium-size maze, the quantum-inspired search found a shorter route, but it kept many more active paths in memory.

### 30x30 Maze, Complexity 0.9

![30x30 DFS vs quantum-inspired path comparison](plots/maze_30x30_comparison.png)

Command style:

```bash
python main.py --width 30 --height 30 --complexity 0.9
```

Summary:

| Metric | DFS | Quantum-inspired |
|---|---:|---:|
| Found | yes | yes |
| Path length | 150 | 120 |
| Explored nodes | 380 | 397 |
| Execution time | 1.638 ms | 177.654 ms |
| Memory proxy | max_stack_size=15 | max_active_paths=425 |
| Extra metric | dead_ends=25 | total_parallel_iterations=120 |

This run shows the core trade-off clearly: DFS is much faster and uses little stack memory, while the quantum-inspired method finds a shorter path by expanding many candidate paths in parallel.

### 50x50 Maze, Complexity 0.7

![50x50 DFS vs quantum-inspired path comparison](plots/maze_50x50_comparison.png)

Command style:

```bash
python main.py --width 50 --height 50 --complexity 0.7
```

Summary:

| Metric | DFS | Quantum-inspired |
|---|---:|---:|
| Found | yes | yes |
| Path length | 380 | 132 |
| Explored nodes | 621 | 1212 |
| Execution time | 2.991 ms | 128073.791 ms |
| Memory proxy | max_stack_size=48 | max_active_paths=813940 |
| Extra metric | dead_ends=33 | total_parallel_iterations=132 |

The 50x50 example demonstrates the memory explosion of the quantum-inspired simulation. It found a much shorter path, but the active path count grew to more than 800,000, making execution dramatically slower.

## Example Terminal Output

For large mazes, the full final path can be very long. The project prints the complete path in the terminal, but this README focuses on the summary table:

```text
Comparison
----------
Metric               DFS                Quantum-inspired
-------------------  -----------------  --------------------
Found                yes                yes
Path length          150                120
Explored nodes       380                397
Execution time (ms)  1.638              177.654
Memory proxy         max_stack_size=15  max_active_paths=425
```

## Tests

Run the test suite:

```bash
python -m unittest discover -s maze_agents/tests
```

Or run the same tests with pytest:

```bash
python -m pytest
```

## Future Extensions

Possible next steps:

- Add Qiskit experiments that encode small maze states into quantum circuits.
- Explore Grover-style search for finding marked exit states.
- Model maze traversal with discrete-time or continuous-time quantum walks.
- Compare classical BFS, A*, Dijkstra, and heuristic agents against the current agents.
- Add randomized maze generation and benchmark results across many maze shapes.
- Export animations showing DFS backtracking and parallel path expansion over time.
