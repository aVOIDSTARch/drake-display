"""
interactive.py

Plotly rendering (plan-phase0 6.10): a self-contained HTML page with

    1. the galactic-scale veil -- rotatable/zoomable surface, entities
       hoverable on top of it
    2. the local-zoom veil around the Sun with a time slider, so each
       massive star's dip deepens toward collapse, spikes, and decays

Height is H; surface color is confidence_here on the canonical
blue (1.0) -> purple (0.5) -> red (0.0) scale (ADR-011,
schema-field-definition.md section 5). The H axis is fixed to [0, 1] in
every frame so dips are comparable across time.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from fields.grid import Grid
from fields.log_odds_field import LogOddsField

from .registry import evaluate_at_entities

CONFIDENCE_COLORSCALE = [[0.0, "rgb(200,30,30)"], [0.5, "rgb(130,40,160)"], [1.0, "rgb(40,70,200)"]]
MARKER_LIFT = 0.015  # draw entities just above the surface so they aren't buried in it

# Star kinds drawn as point clouds: kind -> (legend name, color). Clouds carry no
# per-point tooltip, so tens of thousands of points stay light in the page.
STAR_CLOUD_STYLES = {
    "star_main_sequence": ("Stars: main sequence (HYG)", "rgb(225,150,20)"),
    "star_giant": ("Stars: giants (HYG)", "rgb(215,70,35)"),
    "star_supergiant": ("Stars: supergiants (HYG)", "rgb(140,0,20)"),
    "white_dwarf": ("Stars: white dwarfs (HYG)", "rgb(80,80,95)"),
}
CLOUD_POINT_SIZE = 0.8  # opaque but small: transparency makes WebGL sort every point

# entity group -> (legend name, marker color, size, symbol)
MARKER_STYLES = {
    "sun": ("Sun", "gold", 7, "diamond"),
    "hazard": ("Massive progenitors (FAC-SN)", "black", 7, "x"),
    "system": ("Exoplanet systems", "rgb(20,160,120)", 2.5, "circle"),
}


def _is_missing(value) -> bool:
    return value is None or (isinstance(value, float) and np.isnan(value))


def _fmt(entity: pd.Series, field: str, spec: str, unit: str = "") -> str:
    """A value with its provenance, e.g. '18.00 Msun [Speculative 0.30]'."""
    value = entity[field]
    if _is_missing(value):
        return "unknown"
    text = f"{value:{spec}}{unit}"
    tier, conf = entity.get(f"{field}__tier"), entity.get(f"{field}__conf")
    if not _is_missing(conf):
        text += f" [{tier} {conf:.2f}]"
    return text


def lowest_confidence(entity: pd.Series) -> tuple[str, float] | None:
    """(field, confidence) of the least-trusted present value on this entity."""
    confs = {name[:-len("__conf")]: value for name, value in entity.items()
             if name.endswith("__conf") and not _is_missing(value)}
    if not confs:
        return None
    field = min(confs, key=confs.get)
    return field, confs[field]


def hover_text(entity: pd.Series, here: pd.Series, t: float) -> str:
    lines = [
        f"<b>{entity['name'] if isinstance(entity['name'], str) else entity['id']}</b>",
        entity["kind"],
        f"distance {_fmt(entity, 'distance_pc', '.1f', ' pc')}",
        f"R {_fmt(entity, 'r_gal_kpc', '.2f', ' kpc')}, z {entity['z_gal_kpc'] * 1000:+.0f} pc",
        f"mass {_fmt(entity, 'mass_msun', '.2f', ' Msun')}",
        f"[Fe/H] {_fmt(entity, 'feh', '+.2f')}",
    ]
    if entity["kind"] == "planetary_system":
        lines.append(f"planets {int(entity['num_planets'])}, in HZ {int(entity['num_planets_in_hz'])}")
    if not _is_missing(entity.get("age_myr")):
        lines.append(f"age {_fmt(entity, 'age_myr', ',.0f', ' Myr')}")
    if not _is_missing(entity.get("num_members")):
        lines.append(f"members {int(entity['num_members']):,}")
    if not _is_missing(entity.get("t_collapse_myr")):
        remaining = entity["t_collapse_myr"] - t
        status = f"collapse in {remaining:.2f} Myr" if remaining > 0 else f"collapsed {-remaining:.2f} Myr ago"
        lines.append(f"{status} [clock: {entity['t_collapse_myr__tier']} "
                     f"{entity['t_collapse_myr__conf']:.2f}]")
    weakest = lowest_confidence(entity)
    if weakest is not None:
        lines.append(f"least certain: {weakest[0]} ({weakest[1]:.2f})")
    lines.append(f"<b>H here {here['habitability_here']:.3f}</b>, confidence {here['confidence_here']:.2f}")
    lines.append(f"<i>{entity['data_source']}</i>")
    return "<br>".join(lines)


def _surface(grid: Grid, field: LogOddsField, t: float, showscale: bool = True) -> go.Surface:
    sample = field(grid.points, t)
    return go.Surface(
        x=grid.x, y=grid.y,
        z=sample.height.astype(np.float32),
        surfacecolor=sample.confidence.astype(np.float32),
        colorscale=CONFIDENCE_COLORSCALE, cmin=0.0, cmax=1.0,
        colorbar=dict(title="confidence", len=0.4, y=0.2, yanchor="middle") if showscale else None,
        showscale=showscale,
        hovertemplate="x %{x:.3f} kpc<br>y %{y:.3f} kpc<br>H %{z:.3f}<extra>veil</extra>",
        name="veil",
    )


def _markers(group: str, entities: pd.DataFrame, field: LogOddsField, t: float) -> go.Scatter3d:
    label, color, size, symbol = MARKER_STYLES[group]
    here = evaluate_at_entities(field, entities, t)
    return go.Scatter3d(
        x=entities["x_gal_kpc"], y=entities["y_gal_kpc"],
        z=(here["habitability_here"] + MARKER_LIFT).astype(np.float32),
        mode="markers",
        marker=dict(size=size, color=color, symbol=symbol),
        hovertext=[hover_text(e, h, t) for (_, e), (_, h) in zip(entities.iterrows(), here.iterrows())],
        hoverinfo="text",
        name=label,
    )


def point_cloud(label: str, xyz: np.ndarray, field: LogOddsField, t: float, color: str,
                size: float = CLOUD_POINT_SIZE) -> go.Scatter3d:
    """Many points, drawn on the veil at their own H, with a one-line tooltip.
    xyz is (N, 3) galactocentric kpc; works for entities and survey samples alike."""
    xyz = np.asarray(xyz, dtype=float)
    z = field(xyz, t).height + MARKER_LIFT
    return go.Scatter3d(
        x=xyz[:, 0].astype(np.float32), y=xyz[:, 1].astype(np.float32), z=z.astype(np.float32),
        mode="markers",
        marker=dict(size=size, color=color),
        name=f"{label} ({len(xyz):,})",
        hovertemplate=f"{label}<br>x %{{x:.3f}} kpc, y %{{y:.3f}} kpc<br>H %{{z:.2f}}<extra></extra>",
    )


CLUSTER_AGE_RANGE_LOG_MYR = (0.5, 4.0)  # ~3 Myr to 10 Gyr


def cluster_markers(entities: pd.DataFrame, field: LogOddsField, t: float) -> go.Scatter3d:
    """Star clusters, hoverable, colored by log10 age (young = dark, old = bright).
    Clusters under ~50 Myr still hold stars that will go supernova."""
    here = evaluate_at_entities(field, entities, t)
    lo, hi = CLUSTER_AGE_RANGE_LOG_MYR
    return go.Scatter3d(
        x=entities["x_gal_kpc"], y=entities["y_gal_kpc"],
        z=(here["habitability_here"] + MARKER_LIFT).astype(np.float32),
        mode="markers",
        marker=dict(size=3.5, symbol="diamond-open", color=np.log10(entities["age_myr"]).astype(np.float32),
                    colorscale="Plasma", cmin=lo, cmax=hi,
                    colorbar=dict(title="cluster age<br>log₁₀ Myr", x=-0.06, len=0.4, y=0.2,
                                  yanchor="middle")),
        hovertext=[hover_text(e, h, t) for (_, e), (_, h) in zip(entities.iterrows(), here.iterrows())],
        hoverinfo="text",
        name=f"Star clusters, colored by age ({len(entities):,})",
    )


def star_clouds(entities: pd.DataFrame, field: LogOddsField, t: float) -> list[go.Scatter3d]:
    """One point cloud per star kind in STAR_CLOUD_STYLES present in entities."""
    clouds = []
    for kind, (label, color) in STAR_CLOUD_STYLES.items():
        rows = entities[entities["kind"] == kind]
        if len(rows):
            xyz = rows[["x_gal_kpc", "y_gal_kpc", "z_gal_kpc"]].to_numpy(dtype=float)
            clouds.append(point_cloud(label, xyz, field, t, color))
    return clouds


def _scene(grid: Grid) -> dict:
    return dict(
        xaxis=dict(title="x (kpc)", range=[grid.x[0], grid.x[-1]]),
        yaxis=dict(title="y (kpc)", range=[grid.y[0], grid.y[-1]]),
        zaxis=dict(title="H", range=[0.0, 1.0]),
        aspectmode="manual", aspectratio=dict(x=1, y=1, z=0.45),
    )


def galactic_figure(field: LogOddsField, grid: Grid, groups: dict[str, pd.DataFrame],
                    clouds: list[go.Scatter3d] = ()) -> go.Figure:
    """clouds are prebuilt point_cloud traces, drawn beneath the hoverable markers."""
    traces = [_surface(grid, field, t=0.0), *clouds]
    traces += [_markers(group, entities, field, t=0.0) for group, entities in groups.items()]
    fig = go.Figure(traces)
    fig.update_layout(title="Galactic-scale veil (smooth factors only, t = 0)",
                      scene=_scene(grid), height=750, legend=dict(itemsizing="constant"))
    return fig


def local_figure(field: LogOddsField, grid: Grid, animated: dict[str, pd.DataFrame],
                 static: dict[str, pd.DataFrame], times: np.ndarray,
                 projected: bool = False, clouds: list[go.Scatter3d] = ()) -> go.Figure:
    """animated groups are re-evaluated in every frame; static groups and
    clouds (prebuilt point_cloud traces) are drawn once at times[0] (their
    H is for that time), which keeps the page small when they are numerous."""
    trace_ids = list(range(len(animated) + 1))

    def frame_traces(t):
        return [_surface(grid, field, t)] + [_markers(g, e, field, t) for g, e in animated.items()]

    frames = [go.Frame(name=f"{t:.2f}", data=frame_traces(t), traces=trace_ids) for t in times]
    static_traces = [_markers(g, e, field, times[0]) for g, e in static.items()]
    for trace in static_traces:
        trace.name += f" (H at t = {times[0]:g})"
    fig = go.Figure(data=list(frames[0].data) + static_traces + list(clouds), frames=frames)

    step_args = lambda name: [[name], dict(mode="immediate", frame=dict(duration=0, redraw=True),
                                            transition=dict(duration=0))]
    fig.update_layout(
        title="Local zoom around the Sun — drag the slider to advance time"
              + (" (hazards projected onto the plane)" if projected else ""),
        scene=_scene(grid), height=800, legend=dict(itemsizing="constant"),
        sliders=[dict(
            active=0, currentvalue=dict(prefix="t = ", suffix=" Myr from now"),
            pad=dict(t=40),
            steps=[dict(label=f"{t:g}", method="animate", args=step_args(f"{t:.2f}")) for t in times],
        )],
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.0, y=0.0, xanchor="right", yanchor="top",
            buttons=[dict(label="Play", method="animate",
                          args=[None, dict(frame=dict(duration=400, redraw=True), fromcurrent=True)])],
        )],
    )
    return fig


SLICE_NOTE = ("The local view is a slice through the Sun's plane, so hazard stars more than "
              "~50 pc above or below it show no dip there.")
PROJECTED_NOTE = ("In the local view, hazards are projected onto the Sun's plane: every star's dip "
                  "is shown, but the reach of stars far above or below the plane is overstated.")


def intro_html(projected: bool = False) -> str:
    return f"""
<h1>The Drake Display — Phase 0 veil</h1>
<p>Height is habitability <i>H</i> (log-odds factor model); color is confidence
(blue = well established, purple = mixed, red = speculative). Hover any marker for its data
and provenance.</p>
<p><b>Honesty notes.</b> The metallicity band is a placeholder (EQ-CHEM-3). Massive stars come
from two catalogs (Wolf-Rayet and ALS III) plus a short hand-made list. Their masses are estimated
from spectral type, and because their ages are unknown, each collapse time is one random draw
from a plausible range — a statistical scenario, not a prediction.
{PROJECTED_NOTE if projected else SLICE_NOTE}</p>
"""


def write_html(figures: list[go.Figure], out_path: Path, projected: bool = False) -> None:
    """One self-contained page: plotly.js is inlined once, no server or network needed."""
    # auto_play=False: plotly otherwise starts animating any figure with frames on load,
    # so the slider would open part-way through time instead of at t = 0
    parts = [fig.to_html(full_html=False, include_plotlyjs=(i == 0), auto_play=False)
             for i, fig in enumerate(figures)]
    out_path.write_text(
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>The Drake Display — Phase 0</title>"
        "<style>body{font-family:system-ui,sans-serif;margin:16px;max-width:1300px}</style>"
        "</head><body>" + intro_html(projected) + "".join(parts) + "</body></html>",
        encoding="utf-8",
    )
