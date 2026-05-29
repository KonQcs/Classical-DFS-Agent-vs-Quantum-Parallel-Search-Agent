"""Maze model and validation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, TypeAlias

Position: TypeAlias = tuple[int, int]
CellValue: TypeAlias = int | str
GridInput: TypeAlias = Sequence[Sequence[CellValue]]


@dataclass(frozen=True)
class Maze:
    """Immutable 2D maze grid.

    Cell values:
        0: free cell
        1: wall
        "S": start
        "E": exit
    """

    grid: tuple[tuple[CellValue, ...], ...]
    start: Position
    exit: Position

    def __init__(self, grid: GridInput) -> None:
        normalized = self._normalize_grid(grid)
        start = self._find_unique(normalized, "S")
        exit_ = self._find_unique(normalized, "E")

        object.__setattr__(self, "grid", normalized)
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "exit", exit_)

    @property
    def height(self) -> int:
        """Number of rows in the maze."""

        return len(self.grid)

    @property
    def width(self) -> int:
        """Number of columns in the maze."""

        return len(self.grid[0])

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Maze:
        """Create a maze from text lines.

        Spaces are treated as free cells. Supported characters are:
        ``0``/space for free cells, ``1``/``#`` for walls, ``S`` for start,
        and ``E`` for exit.
        """

        mapping: dict[str, CellValue] = {
            "0": 0,
            " ": 0,
            ".": 0,
            "1": 1,
            "#": 1,
            "S": "S",
            "E": "E",
        }
        parsed: list[list[CellValue]] = []
        for line in lines:
            row: list[CellValue] = []
            for char in line.rstrip("\r\n"):
                if char not in mapping:
                    raise ValueError(f"Unsupported maze character: {char!r}")
                row.append(mapping[char])
            if row:
                parsed.append(row)
        return cls(parsed)

    @classmethod
    def sample(cls) -> Maze:
        """Return a small sample maze for demos and tests."""

        return cls(
            [
                ["S", 0, 1, 0, 0, 0],
                [1, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 1, 0],
                [0, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, "E"],
            ]
        )

    def in_bounds(self, position: Position) -> bool:
        """Return whether a position is inside the grid."""

        row, col = position
        return 0 <= row < self.height and 0 <= col < self.width

    def is_wall(self, position: Position) -> bool:
        """Return whether a position contains a wall."""

        self._ensure_in_bounds(position)
        row, col = position
        return self.grid[row][col] == 1

    def is_exit(self, position: Position) -> bool:
        """Return whether a position is the maze exit."""

        return position == self.exit

    def is_walkable(self, position: Position) -> bool:
        """Return whether a position can be traversed."""

        return self.in_bounds(position) and not self.is_wall(position)

    def get_neighbors(self, position: Position) -> list[Position]:
        """Return traversable orthogonal neighbors in deterministic order."""

        row, col = position
        candidates = [
            (row - 1, col),
            (row, col + 1),
            (row + 1, col),
            (row, col - 1),
        ]
        return [candidate for candidate in candidates if self.is_walkable(candidate)]

    def is_open(self, position: Position) -> bool:
        """Return whether a position can be traversed.

        Kept as a compatibility alias for callers that use the earlier API.
        """

        return self.is_walkable(position)

    def neighbors(self, position: Position) -> list[Position]:
        """Return traversable orthogonal neighbors.

        Kept as a compatibility alias for callers that use the earlier API.
        """

        return self.get_neighbors(position)

    def to_numeric_grid(self) -> list[list[int]]:
        """Return a numeric grid useful for visualization."""

        numeric: list[list[int]] = []
        for row in self.grid:
            numeric.append([1 if cell == 1 else 0 for cell in row])
        return numeric

    def _ensure_in_bounds(self, position: Position) -> None:
        if not self.in_bounds(position):
            raise IndexError(f"Position out of maze bounds: {position}")

    @staticmethod
    def _normalize_grid(grid: GridInput) -> tuple[tuple[CellValue, ...], ...]:
        if not grid:
            raise ValueError("Maze grid must not be empty")

        width = len(grid[0])
        if width == 0:
            raise ValueError("Maze rows must not be empty")

        allowed: set[CellValue] = {0, 1, "S", "E"}
        normalized: list[tuple[CellValue, ...]] = []
        for row_index, row in enumerate(grid):
            if len(row) != width:
                raise ValueError("Maze grid must be rectangular")
            row_tuple = tuple(row)
            invalid = [cell for cell in row_tuple if cell not in allowed]
            if invalid:
                raise ValueError(
                    f"Invalid cell value at row {row_index}: {invalid[0]!r}"
                )
            normalized.append(row_tuple)

        return tuple(normalized)

    @staticmethod
    def _find_unique(grid: tuple[tuple[CellValue, ...], ...], target: str) -> Position:
        matches: list[Position] = []
        for row_index, row in enumerate(grid):
            for col_index, value in enumerate(row):
                if value == target:
                    matches.append((row_index, col_index))

        if len(matches) != 1:
            raise ValueError(
                f"Maze must contain exactly one {target!r} cell; found {len(matches)}"
            )
        return matches[0]
