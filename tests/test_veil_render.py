import numpy as np
import pytest

pd = pytest.importorskip("pandas")
pytest.importorskip("plotly")
pytest.importorskip("astropy")

from test_veil_pipeline import paths  # noqa: E402,F401  (fixture)
from fields.grid import GridSpec, make_grid  # noqa: E402
from veil import interactive  # noqa: E402
from veil.ingest import load_entities  # noqa: E402
from veil.main import check_sun  # noqa: E402
from veil.registry import build_fields  # noqa: E402

from pathlib import Path  # noqa: E402

CONFIGS = Path(__file__).parent.parent / "configs"


def test_local_figure_has_one_frame_per_time_and_fixed_axis(paths):  # noqa: F811
    entities = load_entities(paths)
    _, local = build_fields(entities, CONFIGS)
    grid = make_grid("custom", center=(-8.2, 0.0, 0.02), spec=GridSpec(0.25, 12))
    hazards = entities[entities["kind"] == "star_massive_progenitor"]
    systems = entities[entities["kind"] == "planetary_system"]
    times = np.array([0.0, 1.0, 2.0])

    fig = interactive.local_figure(local, grid, {"hazard": hazards}, {"system": systems}, times)

    assert [f.name for f in fig.frames] == ["0.00", "1.00", "2.00"]
    assert len(fig.data) == 3  # surface + animated hazards + static systems
    assert all(len(f.data) == 2 for f in fig.frames)  # static layer is not re-sent
    assert tuple(fig.layout.scene.zaxis.range) == (0.0, 1.0)
    assert len(fig.layout.sliders[0].steps) == 3


def test_hover_reports_clock_and_provenance(paths):  # noqa: F811
    entities = load_entities(paths)
    betelgeuse = entities[entities["name"] == "Betelgeuse"].iloc[0]
    here = pd.Series({"habitability_here": 0.5, "confidence_here": 0.1})
    text = interactive.hover_text(betelgeuse, here, t=0.0)
    assert "[Speculative 0.30]" in text  # hand-entered mass
    assert "least certain: t_birth_myr (0.10)" in text or "least certain: t_collapse_myr (0.10)" in text
    assert "collapse in 0.10 Myr" in text
    assert "collapsed" in interactive.hover_text(betelgeuse, here, t=1.0)


def test_write_html_inlines_plotly_once(paths, tmp_path):  # noqa: F811
    entities = load_entities(paths)
    galactic, _ = build_fields(entities, CONFIGS)
    grid = make_grid("custom", spec=GridSpec(20.0, 8))
    fig = interactive.galactic_figure(galactic, grid, {"sun": entities[entities["id"] == "hyg:0"]})
    out = tmp_path / "veil.html"

    interactive.write_html([fig, fig], out)

    html = out.read_text(encoding="utf-8")
    assert html.count("plotly.js v") <= 2  # the one inlined bundle (banner may repeat once)
    assert html.count("<div id=") >= 2
    assert "Honesty notes" in html


def test_check_sun_rejects_a_wrong_frame(paths):  # noqa: F811
    entities = load_entities(paths)
    np.testing.assert_allclose(check_sun(entities), [-8.2, 0.0, 0.02], atol=1e-4)
    entities.loc[entities["id"] == "hyg:0", "r_gal_kpc"] = 8.5
    with pytest.raises(RuntimeError, match="frame"):
        check_sun(entities)


def test_intro_states_the_hazard_geometry():
    assert "slice through the Sun's plane" in interactive.intro_html(projected=False)
    projected = interactive.intro_html(projected=True)
    assert "projected onto the Sun's plane" in projected
    assert "overstated" in projected


def test_animated_page_does_not_autoplay(paths, tmp_path):  # noqa: F811
    entities = load_entities(paths)
    _, local = build_fields(entities, CONFIGS)
    grid = make_grid("custom", center=(-8.2, 0.0, 0.02), spec=GridSpec(0.25, 6))
    fig = interactive.local_figure(local, grid, {"sun": entities[entities["id"] == "hyg:0"]}, {},
                                   np.array([0.0, 1.0]))
    out = tmp_path / "veil.html"

    interactive.write_html([fig], out)

    assert fig.layout.sliders[0].active == 0
    # plotly's default auto_play emits a Plotly.animate call that starts the
    # slider moving on load, so the page opened part-way through time
    assert "Plotly.animate" not in out.read_text(encoding="utf-8")


def test_point_cloud_sits_on_the_veil_without_per_point_tooltips(paths):  # noqa: F811
    entities = load_entities(paths)
    galactic, _ = build_fields(entities, CONFIGS)
    xyz = np.array([[-8.2, 0.0, 0.0], [0.0, 0.0, 0.0], [5.0, 5.0, 0.0]])

    trace = interactive.point_cloud("Test points", xyz, galactic, t=0.0, color="red")

    np.testing.assert_allclose(trace.z, galactic(xyz, 0.0).height + interactive.MARKER_LIFT, rtol=1e-6)
    assert trace.hovertext is None
    assert trace.name == "Test points (3)"


def test_star_clouds_make_one_layer_per_star_kind(paths):  # noqa: F811
    entities = load_entities(paths)
    galactic, _ = build_fields(entities, CONFIGS)
    stars = entities[entities["kind"].isin(interactive.STAR_CLOUD_STYLES)]

    clouds = interactive.star_clouds(stars, galactic, t=0.0)

    kinds_present = [k for k in interactive.STAR_CLOUD_STYLES if (stars["kind"] == k).any()]
    assert len(clouds) == len(kinds_present)
    assert sum(len(c.x) for c in clouds) == len(stars)
