"""Phase 0 pipeline tests on small inline fixtures -- no network, no downloaded catalogs."""

import numpy as np
import pytest

pd = pytest.importorskip("pandas")
pytest.importorskip("astropy")

from veil.coords import R0_KPC, to_galactocentric  # noqa: E402
from veil.ingest import (  # noqa: E402
    CONF,
    classify_star,
    load_entities,
    load_exoplanets,
    load_hazards,
    load_hyg,
    luminosity_class,
    modeled_feh,
)
from veil.registry import build_fields, build_hazard_field, evaluate_at_entities, near  # noqa: E402

HYG_HEADER = "id,hip,proper,ra,dec,dist,mag,absmag,spect,ci\n"
HYG_ROWS = """0,,Sol,0.0,0.0,0.0,-26.7,4.85,G2V,0.656
1,27989,Betelgeuse,5.919529,7.407063,152.6718,0.45,-5.469,M2Ib,1.5
2,65474,Spica,13.419883,-11.161322,76.5697,0.98,-3.44,B1V,-0.235
3,,,1.0,10.0,100000,9.0,-10.0,K0,1.0
4,,,2.0,20.0,,9.0,2.0,K0,1.0
5,,,3.0,-5.0,50.0,6.0,2.5,K0III,1.1
6,,,4.0,-6.0,20.0,8.0,6.0,K1V,0.9
"""
HAZARDS = """# comment lines are allowed
hip,name,mass_msun,t_collapse_myr,evolutionary_note
27989,Betelgeuse,18,0.1,red supergiant
65474,Spica,11.4,10.0,B main sequence
"""
EXOPLANETS = """pl_name,hostname,ra,dec,sy_dist,sy_pnum,st_teff,st_rad,st_mass,st_met,st_lum,pl_rade,pl_bmasse,pl_orbsmax,pl_orbper,pl_eqt,pl_insol
"Host b",Host,100.0,10.0,20.0,2,5700,1.0,1.0,0.10,0.0,1.0,1.0,1.0,365.0,,
"Host c",Host,100.0,10.0,20.0,2,5700,1.0,1.0,0.10,0.0,11.0,300.0,5.0,4000.0,,0.04
"Far b",Far,200.0,-20.0,500.0,1,4000,0.6,0.6,,-1.0,,5.0,0.1,10.0,,
"NoDist b",NoDist,10.0,0.0,,1,,,,,,1.0,,,,,
"""


@pytest.fixture
def paths(tmp_path):
    files = {"hyg": HYG_HEADER + HYG_ROWS, "hazards": HAZARDS, "exoplanets": EXOPLANETS}
    out = {}
    for key, text in files.items():
        out[key] = tmp_path / f"{key}.csv"
        out[key].write_text(text)
    return out


# ---- coords ----

def test_sun_lands_at_r0_and_z0():
    x, y, z = to_galactocentric([0.0], [0.0], [0.0])
    # galcen_distance is the 3D Sun-center distance, so in-plane R = sqrt(8.2^2 - 0.02^2)
    np.testing.assert_allclose([x[0], y[0], z[0]], [-R0_KPC, 0.0, 0.020], atol=1e-4)


def test_galactic_center_direction_points_at_origin():
    # Sgr A*, at the Sun-center distance
    x, y, z = to_galactocentric([266.41683], [-29.00781], [R0_KPC * 1000])
    assert np.hypot(x[0], y[0]) < 0.05
    assert abs(z[0]) < 0.05


# ---- classification ----

@pytest.mark.parametrize("spect,lum_class,kind", [
    ("M2Ib", "Ib", "star_supergiant"),
    ("B0.5Iavar", "Ia", "star_supergiant"),
    ("WC8 + O9I", "I", "star_supergiant"),
    ("K0III", "III", "star_giant"),
    ("G8III-IV", "III", "star_giant"),
    ("F3/F5IV", "IV", "star_main_sequence"),
    ("G2V", "V", "star_main_sequence"),
    ("K0", None, "star_main_sequence"),
    ("DA2", None, "white_dwarf"),
    (np.nan, None, "star_main_sequence"),
])
def test_spectral_classification(spect, lum_class, kind):
    assert luminosity_class(spect) == lum_class
    assert classify_star(spect) == kind


# ---- HYG ----

def test_hyg_filters_unknown_distances_but_keeps_sun(paths):
    stars = load_hyg(paths["hyg"])
    assert sorted(stars["id"]) == ["hyg:0", "hyg:1", "hyg:2", "hyg:5", "hyg:6"]


def test_hyg_converts_ra_hours_and_ignores_native_xyz(paths):
    stars = load_hyg(paths["hyg"]).set_index("id")
    assert stars.loc["hyg:1", "ra_icrs_deg"] == pytest.approx(5.919529 * 15)
    assert stars.loc["hyg:0", "r_gal_kpc"] == pytest.approx(R0_KPC, abs=1e-4)


def test_hyg_estimates_mass_for_main_sequence_only(paths):
    stars = load_hyg(paths["hyg"]).set_index("id")
    assert np.isnan(stars.loc["hyg:1", "mass_msun"])  # supergiant
    assert np.isnan(stars.loc["hyg:5", "mass_msun"])  # giant
    assert stars.loc["hyg:6", "mass_msun"] > 0
    assert stars.loc["hyg:6", "conf_mass_msun"] == CONF["hyg_mass"]
    assert np.isnan(stars.loc["hyg:5", "conf_mass_msun"])


def test_hyg_feh_is_modeled_from_radius(paths):
    stars = load_hyg(paths["hyg"])
    np.testing.assert_allclose(stars["feh"], modeled_feh(stars["r_gal_kpc"]))
    assert (stars["conf_feh"] == CONF["modeled_feh"]).all()


# ---- hazards ----

def test_hazards_take_position_from_hyg_and_derive_clock(paths):
    stars = load_hyg(paths["hyg"])
    hazards = load_hazards(paths["hazards"], stars).set_index("name")
    betelgeuse = stars.set_index("id").loc["hyg:1"]
    assert hazards.loc["Betelgeuse", "x_gal_kpc"] == betelgeuse["x_gal_kpc"]
    assert hazards.loc["Betelgeuse", "kind"] == "star_massive_progenitor"
    assert hazards["is_speculative"].all()
    life = hazards.loc["Spica", "main_sequence_lifetime_myr"]
    assert hazards.loc["Spica", "t_birth_myr"] == pytest.approx(10.0 - life)


def test_unmatched_hazard_is_an_error(paths, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("hip,name,mass_msun,t_collapse_myr\n99999999,Nowhere,20,1.0\n")
    with pytest.raises(ValueError, match="Nowhere"):
        load_hazards(bad, load_hyg(paths["hyg"]))


def test_hazard_born_in_the_future_is_an_error(paths, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("hip,name,mass_msun,t_collapse_myr\n27989,Betelgeuse,40,5.0\n")  # t_MS(40) ~ 1 Myr
    with pytest.raises(ValueError, match="future"):
        load_hazards(bad, load_hyg(paths["hyg"]))


# ---- exoplanets ----

def test_exoplanets_split_into_systems_and_planets(paths):
    exo = load_exoplanets(paths["exoplanets"]).set_index("id")
    assert "exo-sys:NoDist" not in exo.index
    assert exo.loc["exo-sys:Host", "num_planets"] == 2
    assert exo.loc["exo:Host b", "parent_star_id"] == "exo-sys:Host"
    assert exo.loc["exo:Host b", "kind"] == "planet_terrestrial"
    assert exo.loc["exo:Host c", "kind"] == "planet_gas_giant"
    assert exo.loc["exo:Far b", "kind"] == "planet_super_earth"  # no radius -> mass bounds


def test_habitable_zone_uses_insolation_or_derives_it(paths):
    exo = load_exoplanets(paths["exoplanets"]).set_index("id")
    # Host b: no pl_insol, L = 1, a = 1 AU -> S = 1.0, inside [0.35, 1.1]
    assert exo.loc["exo:Host b", "insolation_earth_equiv"] == pytest.approx(1.0)
    assert exo.loc["exo:Host b", "in_habitable_zone"] == True  # noqa: E712
    assert exo.loc["exo:Host c", "in_habitable_zone"] == False  # noqa: E712
    assert exo.loc["exo-sys:Host", "num_planets_in_hz"] == 1


def test_measured_metallicity_beats_modeled(paths):
    exo = load_exoplanets(paths["exoplanets"]).set_index("id")
    assert exo.loc["exo-sys:Host", "feh"] == 0.10
    assert exo.loc["exo-sys:Host", "conf_feh"] == CONF["exo_feh"]
    far = exo.loc["exo-sys:Far"]
    assert far["feh"] == pytest.approx(modeled_feh(far["r_gal_kpc"]))
    assert far["conf_feh"] == CONF["modeled_feh"]


# ---- unified table + registry ----

def test_entities_are_unique_and_fully_positioned(paths):
    entities = load_entities(paths)
    assert entities["id"].is_unique
    assert not entities[["x_gal_kpc", "y_gal_kpc", "z_gal_kpc"]].isna().any().any()
    assert (entities["kind"] == "star_massive_progenitor").sum() == 2
    assert "hyg:1" in set(entities["id"])  # hazard keeps its HYG id, appears once


def test_hazard_field_has_one_dip_per_progenitor(paths):
    entities = load_entities(paths)
    field = build_hazard_field(entities)
    assert len(field.factors) == 2
    betelgeuse = entities[entities["name"] == "Betelgeuse"].iloc[0]
    center = betelgeuse[["x_gal_kpc", "y_gal_kpc", "z_gal_kpc"]].to_numpy(dtype=float)[None, :]
    assert field(center, t=0.09).logit[0] < field(center, t=-5.0).logit[0] < 0
    # weakest-link confidence: the scenario clock
    assert field.factors[0].confidence == pytest.approx(0.9 * CONF["scenario_clock"])


def test_local_field_is_galactic_plus_hazards(paths):
    from pathlib import Path
    entities = load_entities(paths)
    galactic, local = build_fields(entities, Path(__file__).parent.parent / "configs")
    assert len(local.factors) == len(galactic.factors) + 2
    here = evaluate_at_entities(local, entities, t=0.0)
    assert here.index.equals(entities.index)
    assert ((here["habitability_here"] > 0) & (here["habitability_here"] < 1)).all()


def test_near_selects_square_patch(paths):
    entities = load_entities(paths)
    sun = (-R0_KPC, 0.0)
    picked = near(entities, sun, 0.1)
    assert "hyg:0" in set(picked["id"])
    assert (np.abs(picked["x_gal_kpc"] + R0_KPC) <= 0.1).all()
