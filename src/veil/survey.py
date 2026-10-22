"""
survey.py

The Gaia DR3 survey layer (docs/data-sources/source-gaia-dr3.md): millions of
stars with precise parallaxes, used to show where the map rests on real data.

This is display data, not model input. The stars are not entities -- millions
of rows would swamp the entity table, and none of them drives a factor -- so
they live in their own arrays, cached in data/processed/ after the
coordinate transform, which is the slow step.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .coords import to_galactocentric

GAIA_COLUMNS = ["ra", "dec", "parallax", "phot_g_mean_mag", "bp_rp"]
SAMPLE_SEED = 20261022


@dataclass
class SurveySample:
    """Survey stars in galactocentric coordinates.

    Attributes:
        xyz: (N, 3) float32, kpc.
        g_mag: (N,) float32, Gaia G magnitude.
        bp_rp: (N,) float32, Gaia BP-RP color (NaN where missing).
    """
    xyz: np.ndarray
    g_mag: np.ndarray
    bp_rp: np.ndarray

    def __len__(self) -> int:
        return len(self.xyz)

    def sample(self, n: int, mask: np.ndarray | None = None) -> np.ndarray:
        """Up to n points (as an (n, 3) array), drawn reproducibly from the
        stars where mask is true."""
        index = np.flatnonzero(mask) if mask is not None else np.arange(len(self))
        if len(index) > n:
            index = np.random.default_rng(SAMPLE_SEED).choice(index, size=n, replace=False)
        return self.xyz[np.sort(index)]

    def in_patch(self, center, half_width_kpc: float) -> np.ndarray:
        """Boolean mask of stars whose (x, y) is inside a square patch."""
        return ((np.abs(self.xyz[:, 0] - center[0]) <= half_width_kpc)
                & (np.abs(self.xyz[:, 1] - center[1]) <= half_width_kpc))


def load_gaia(raw_csv: Path, cache: Path) -> SurveySample:
    """Read the Gaia download and transform it to galactocentric coordinates,
    reusing the cache when it is newer than the download. Distances are
    1000 / parallax (EQ-GEO-1): every star was selected with parallax
    measured to better than 10%, where the simple inverse is reliable."""
    if cache.exists() and cache.stat().st_mtime >= raw_csv.stat().st_mtime:
        with np.load(cache) as arrays:
            return SurveySample(arrays["xyz"], arrays["g_mag"], arrays["bp_rp"])

    raw = pd.read_csv(raw_csv, usecols=GAIA_COLUMNS, dtype="float64")
    raw = raw[raw["parallax"] > 0]
    x, y, z = to_galactocentric(raw["ra"], raw["dec"], 1000.0 / raw["parallax"])
    sample = SurveySample(
        xyz=np.stack([x, y, z], axis=-1).astype(np.float32),
        g_mag=raw["phot_g_mean_mag"].to_numpy(dtype=np.float32),
        bp_rp=raw["bp_rp"].to_numpy(dtype=np.float32),
    )
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez(cache, xyz=sample.xyz, g_mag=sample.g_mag, bp_rp=sample.bp_rp)
    return sample


def coverage_counts(xyz: np.ndarray, half_width_kpc: float, bins: int) -> tuple[np.ndarray, np.ndarray]:
    """Star counts on a bins x bins grid over +/-half_width_kpc in x and y.
    Returns (counts, centers): counts[iy, ix], and the cell-center coordinate
    shared by both axes."""
    edges = np.linspace(-half_width_kpc, half_width_kpc, bins + 1)
    counts, _, _ = np.histogram2d(xyz[:, 1], xyz[:, 0], bins=[edges, edges])
    centers = 0.5 * (edges[:-1] + edges[1:])
    return counts, centers
