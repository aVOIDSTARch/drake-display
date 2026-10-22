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

# entity group -> (legend name, marker color, size, symbol)
MARKER_STYLES = {
    "sun": ("Sun", "gold", 7, "diamond"),
    "hazard": ("Massive progenitors (FAC-SN)", "black", 5, "x"),
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
    if entity["kind"] == "star_massive_progenitor":
        remaining = entity["t_collapse_myr"] - t
        status = f"collapse in {remaining:.2f} Myr" if remaining > 0 else f"collapsed {-remaining:.2f} Myr ago"
        lines.append(f"{status} [scenario clock: {entity['t_collapse_myr__tier']} "
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
        colorbar=dict(title="confidence", len=0.6) if showscale else None,
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


def _scene(grid: Grid) -> dict:
    return dict(
        xaxis=dict(title="x (kpc)", range=[grid.x[0], grid.x[-1]]),
        yaxis=dict(title="y (kpc)", range=[grid.y[0], grid.y[-1]]),
        zaxis=dict(title="H", range=[0.0, 1.0]),
        aspectmode="manual", aspectratio=dict(x=1, y=1, z=0.45),
    )


def galactic_figure(field: LogOddsField, grid: Grid, groups: dict[str, pd.DataFrame]) -> go.Figure:
    traces = [_surface(grid, field, t=0.0)]
    traces += [_markers(group, entities, field, t=0.0) for group, entities in groups.items()]
    fig = go.Figure(traces)
    fig.update_layout(title="Galactic-scale veil (smooth factors only, t = 0)",
                      scene=_scene(grid), height=750, legend=dict(itemsizing="constant"))
    return fig


def local_figure(field: LogOddsField, grid: Grid, animated: dict[str, pd.DataFrame],
                 static: dict[str, pd.DataFrame], times: np.ndarray) -> go.Figure:
    """animated groups are re-evaluated in every frame; static groups are
    drawn once at times[0] (their hover H is for that time), which keeps
    the page small when they are numerous."""
    trace_ids = list(range(len(animated) + 1))

    def frame_traces(t):
        return [_surface(grid, field, t)] + [_markers(g, e, field, t) for g, e in animated.items()]

    frames = [go.Frame(name=f"{t:.2f}", data=frame_traces(t), traces=trace_ids) for t in times]
    static_traces = [_markers(g, e, field, times[0]) for g, e in static.items()]
    for trace in static_traces:
        trace.name += f" (H at t = {times[0]:g})"
    fig = go.Figure(data=list(frames[0].data) + static_traces, frames=frames)

    step_args = lambda name: [[name], dict(mode="immediate", frame=dict(duration=0, redraw=True),
                                            transition=dict(duration=0))]
    fig.update_layout(
        title="Local zoom around the Sun — drag the slider to advance time",
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


INTRO = """
<h1>The Drake Display — Phase 0 veil</h1>
<p>Height is habitability <i>H</i> (log-odds factor model); color is confidence
(blue = well established, purple = mixed, red = speculative). Hover any marker for its data
and provenance.</p>
<p><b>Honesty notes.</b> The metallicity band is a placeholder (EQ-CHEM-3). Massive-star masses
and collapse times are hand-assigned scenario values, not predictions. The local view is a slice
through the Sun's plane, so hazard stars more than ~50 pc above or below it show no dip there.</p>
"""


def write_html(figures: list[go.Figure], out_path: Path) -> None:
    """One self-contained page: plotly.js is inlined once, no server or network needed."""
    parts = [fig.to_html(full_html=False, include_plotlyjs=(i == 0)) for i, fig in enumerate(figures)]
    out_path.write_text(
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>The Drake Display — Phase 0</title>"
        "<style>body{font-family:system-ui,sans-serif;margin:16px;max-width:1300px}</style>"
        "</head><body>" + INTRO + "".join(parts) + "</body></html>",
        encoding="utf-8",
    )
