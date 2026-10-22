"""
render.py

Static matplotlib rendering for validating the veil (Phase 0 spec
section 6.9): the fastest way to see the field looks right before
building anything interactive. Requires the "render" extra
(pip install -e '.[render]').

Each figure shows three panels side by side:
    height H as a heatmap, confidence as a heatmap, and H as a 3D surface.
"""

from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")  # file output only; never needs a display
import matplotlib.pyplot as plt

from .grid import Grid
from .log_odds_field import VeilSample


@dataclass
class Marker:
    """A labelled point to overplot, e.g. the Sun or a hazard star."""
    x: float
    y: float
    label: str


def static_validate(sample: VeilSample, grid: Grid, title: str, out_path: str,
                    markers: list[Marker] | None = None) -> None:
    """Render one veil sample to out_path (PNG)."""
    markers = markers or []
    fig = plt.figure(figsize=(17, 5.2))

    panels = [
        (sample.height, "Habitability H", "viridis"),
        (sample.confidence, "Confidence", "coolwarm_r"),  # red = low trust, blue = high
    ]
    for i, (values, label, cmap) in enumerate(panels):
        ax = fig.add_subplot(1, 3, i + 1)
        image = ax.imshow(values, origin="lower", extent=grid.extent, cmap=cmap,
                          vmin=0.0, vmax=1.0)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
        for m in markers:
            ax.plot(m.x, m.y, marker="*", color="white", markeredgecolor="black", markersize=12)
            ax.annotate(m.label, (m.x, m.y), textcoords="offset points", xytext=(6, 6),
                        color="white", fontsize=8)
        ax.set_title(label)
        ax.set_xlabel("x (kpc)")
        ax.set_ylabel("y (kpc)")

    ax3d = fig.add_subplot(1, 3, 3, projection="3d")
    ax3d.plot_surface(grid.X, grid.Y, sample.height, cmap="viridis", vmin=0.0, vmax=1.0,
                      rstride=2, cstride=2, linewidth=0)
    ax3d.set_title("Veil surface")
    ax3d.set_xlabel("x (kpc)")
    ax3d.set_ylabel("y (kpc)")
    ax3d.set_zlabel("H")

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
