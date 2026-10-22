"""
grid.py

Evaluation grids for the two Phase 0 regimes (ADR-004). Each grid is a
square patch of the plane z = center z, returned as a (ny, nx, 3)
array of galactocentric points in kpc -- the shape every Field and
Factor already accepts.

    galactic : +/-20 kpc around the galactic center, 300 x 300 cells.
               Smooth factors only; point hazards are far below one cell.
    local    : +/-0.2 kpc around a chosen point, 200 x 200 cells (~2 pc).
               Fine enough to resolve a 10 pc supernova kill radius.
"""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class GridSpec:
    half_width_kpc: float
    cells: int

    def __post_init__(self):
        if self.half_width_kpc <= 0:
            raise ValueError("half_width_kpc must be positive")
        if self.cells < 2:
            raise ValueError("cells must be at least 2")


GRID_SPECS = {
    "galactic": GridSpec(half_width_kpc=20.0, cells=300),
    "local": GridSpec(half_width_kpc=0.2, cells=200),
}


@dataclass
class Grid:
    """
    Attributes:
        kind: "galactic", "local", or "custom".
        x, y: 1D axis coordinates (kpc), lengths nx and ny.
        X, Y: 2D meshgrids, shape (ny, nx), for plotting.
        points: (ny, nx, 3) galactocentric points to evaluate fields on.
    """

    kind: str
    x: np.ndarray
    y: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    points: np.ndarray

    @property
    def R(self) -> np.ndarray:
        """Galactocentric cylindrical radius at each cell, (ny, nx)."""
        return np.hypot(self.points[..., 0], self.points[..., 1])

    @property
    def extent(self) -> tuple[float, float, float, float]:
        """(xmin, xmax, ymin, ymax), as matplotlib's imshow wants it."""
        return (self.x[0], self.x[-1], self.y[0], self.y[-1])


def make_grid(kind: str, center=(0.0, 0.0, 0.0), spec: GridSpec | None = None) -> Grid:
    """
    Build a grid of one of the GRID_SPECS kinds, or pass spec to
    override the size (kind is then just a label).
    """
    if spec is None:
        if kind not in GRID_SPECS:
            raise ValueError(f"unknown grid kind '{kind}' -- must be one of {sorted(GRID_SPECS)}")
        spec = GRID_SPECS[kind]

    cx, cy, cz = np.asarray(center, dtype=float)
    offsets = np.linspace(-spec.half_width_kpc, spec.half_width_kpc, spec.cells)
    x, y = cx + offsets, cy + offsets
    X, Y = np.meshgrid(x, y)
    points = np.stack([X, Y, np.full_like(X, cz)], axis=-1)
    return Grid(kind, x, y, X, Y, points)
