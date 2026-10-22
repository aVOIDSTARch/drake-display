"""Phase 0 pipeline tests on small inline fixtures -- no network, no downloaded catalogs."""

import numpy as np
import pytest

pd = pytest.importorskip("pandas")
pytest.importorskip("astropy")

from veil.coords import R0_KPC, to_galactocentric  # noqa: E402
from veil.ingest import (  # noqa: E402
    MEASURED,
    STATISTICAL,
    MODELED,
    PHYSICAL_FIELDS,
    SPECULATIVE,
    classify_star,
    enforce_provenance_default,
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
    assert stars.loc["hyg:6", "mass_msun__conf"] == 0.50
    assert stars.loc["hyg:6", "mass_msun__tier"] == "Inferred"
    assert np.isnan(stars.loc["hyg:5", "mass_msun__conf"])  # no value -> no provenance


def test_hyg_feh_is_modeled_from_radius(paths):
    stars = load_hyg(paths["hyg"])
    np.testing.assert_allclose(stars["feh"], modeled_feh(stars["r_gal_kpc"]))
    assert (stars["feh__conf"] == 0.40).all()
    assert (stars["feh__tier"] == MODELED).all()


# ---- hazards ----

def test_hazards_take_position_from_hyg_and_derive_clock(paths):
    stars = load_hyg(paths["hyg"])
    hazards = load_hazards(paths["hazards"], stars).set_index("name")
    betelgeuse = stars.set_index("id").loc["hyg:1"]
    assert hazards.loc["Betelgeuse", "x_gal_kpc"] == betelgeuse["x_gal_kpc"]
    assert hazards.loc["Betelgeuse", "kind"] == "star_massive_progenitor"
    assert (hazards["mass_msun__tier"] == SPECULATIVE).all()
    assert (hazards["t_collapse_myr__conf"] == 0.10).all()
    assert (hazards["x_gal_kpc__tier"] == MEASURED).all()  # position is still measured
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
    assert exo.loc["exo-sys:Host", "feh__conf"] == 0.85
    assert exo.loc["exo-sys:Host", "feh__tier"] == MEASURED
    far = exo.loc["exo-sys:Far"]
    assert far["feh"] == pytest.approx(modeled_feh(far["r_gal_kpc"]))
    assert far["feh__conf"] == 0.40
    assert far["feh__tier"] == MODELED


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
    assert field.factors[0].confidence == pytest.approx(0.9 * 0.10)


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


# ---- graded provenance (ADR-011) ----

def test_every_present_physical_value_has_provenance(paths):
    entities = load_entities(paths)
    for field in PHYSICAL_FIELDS:
        present = entities[field].notna()
        assert entities.loc[present, f"{field}__conf"].notna().all(), field
        assert entities.loc[present, f"{field}__tier"].notna().all(), field
        assert entities.loc[~present, f"{field}__conf"].isna().all(), field
        assert entities[f"{field}__conf"].dropna().between(0, 1).all(), field


def test_unstated_provenance_defaults_to_speculative():
    entities = pd.DataFrame({field: [np.nan] for field in PHYSICAL_FIELDS})
    for field in PHYSICAL_FIELDS:
        entities[f"{field}__tier"] = None
        entities[f"{field}__conf"] = np.nan
    entities.loc[0, "teff_k"] = 5000.0  # a value nobody vouched for

    out = enforce_provenance_default(entities)

    assert out.loc[0, "teff_k__tier"] == SPECULATIVE
    assert out.loc[0, "teff_k__conf"] == 0.10
    assert np.isnan(out.loc[0, "mass_msun__conf"])


# ---- hazard geometry: slice vs projection (ADR-014) ----

def _off_plane_star(dz_kpc):
    return pd.Series({
        "name": "off-plane", "x_gal_kpc": -8.2, "y_gal_kpc": 0.0, "z_gal_kpc": 0.02 + dz_kpc,
        "t_birth_myr": -5.0, "t_collapse_myr": 0.0,
        "x_gal_kpc__conf": 0.85, "mass_msun__conf": 0.3, "t_collapse_myr__conf": 0.1,
    })


def test_off_plane_star_leaves_no_dip_in_the_slice():
    from veil.registry import supernova_factor
    on_plane_point = np.array([[-8.2, 0.0, 0.02]])
    factor = supernova_factor(_off_plane_star(0.100))
    assert factor.contribution(on_plane_point, t=0.0)[0] == 0.0


def test_projection_shows_the_off_plane_dip():
    from veil.registry import supernova_factor
    on_plane_point = np.array([[-8.2, 0.0, 0.02]])
    projected = supernova_factor(_off_plane_star(0.100), project_onto_plane=True)
    in_plane = supernova_factor(_off_plane_star(0.0))
    np.testing.assert_allclose(projected.contribution(on_plane_point, t=0.0),
                               in_plane.contribution(on_plane_point, t=0.0))
    assert projected.contribution(on_plane_point, t=0.0)[0] < 0


def test_build_fields_passes_projection_through(paths):
    from pathlib import Path
    from fields.distance import CylindricalDistance, EuclideanDistance
    entities = load_entities(paths)
    configs = Path(__file__).parent.parent / "configs"
    _, sliced = build_fields(entities, configs)
    _, projected = build_fields(entities, configs, project_hazards=True)
    assert isinstance(sliced.factors[-1].spatial.distance_metric, EuclideanDistance)
    assert isinstance(projected.factors[-1].spatial.distance_metric, CylindricalDistance)


# ---- catalog hazards: Wolf-Rayet and ALS III ----

WR_CSV = """WR,SpType,Name,RA_ICRS,DE_ICRS,Dist,E_Dist,e_Dist,logL
"WR1","WN4b","HD 4004",10.868291666666666,64.75983333333332,3.15,0.47,0.36,
"WR11","WC8 + O7.5III","gam2 Vel",122.383,-47.337,0.34,0.05,0.04,5.31
"WR999","WN6","",200.0,-10.0,,,,
"""
OB_CSV = """ALS,GaiaDR2,GOSC,RAJ2000,DEJ2000,DistP50,DistP16,DistP84,SpType
1,1,"HD 46223",97.97,4.83,1500.0,1400.0,1600.0,"O4V((f))"
2,2," ",100.0,5.0,800.0,750.0,850.0,"B7III, B8V"
3,3," ",101.0,6.0,900.0,850.0,950.0," "
4,4," ",201.298,-11.161,77.0,75.0,79.0,"B1V"
5,5," ",102.0,7.0,2000.0,1900.0,2100.0,"B0Ia"
"""


@pytest.fixture
def catalog_paths(paths, tmp_path):
    (tmp_path / "wr.csv").write_text(WR_CSV)
    (tmp_path / "ob.csv").write_text(OB_CSV)
    return {**paths, "wolf_rayet": tmp_path / "wr.csv", "ob_stars": tmp_path / "ob.csv"}


@pytest.mark.parametrize("spect,low,high", [
    ("O3V", 55, 65), ("B0V", 13, 17), ("B2.5V", 7.5, 8.5), ("B0Ia", 22, 30), ("O5/6III", 40, 50),
])
def test_ob_mass_calibration(spect, low, high):
    from veil.ingest import estimate_ob_mass
    assert low <= estimate_ob_mass(spect) <= high


@pytest.mark.parametrize("spect", ["OB", "A0V", "", None, "WN6"])
def test_unreadable_spectral_types_give_no_mass(spect):
    from veil.ingest import estimate_ob_mass
    assert np.isnan(estimate_ob_mass(spect))


def test_clock_draws_are_reproducible_and_independent():
    from veil.ingest import draw_clocks
    ids = pd.Series(["als:1", "als:2", "als:3"])
    a = draw_clocks(ids, remaining_myr_max=0.5)
    b = draw_clocks(ids, remaining_myr_max=0.5)
    pd.testing.assert_series_equal(a, b)
    assert ((a >= 0) & (a <= 0.5)).all()
    # one star's draw doesn't depend on which others are present
    assert draw_clocks(pd.Series(["als:2"]), remaining_myr_max=0.5).iloc[0] == a.iloc[1]


def test_wolf_rayet_loader(catalog_paths):
    from veil.ingest import load_wolf_rayet
    wr = load_wolf_rayet(catalog_paths["wolf_rayet"]).set_index("id")
    assert list(wr.index) == ["wr:WR1", "wr:WR11"]           # WR999 has no distance
    assert wr.loc["wr:WR1", "distance_pc"] == 3150.0          # kpc -> pc
    assert wr.loc["wr:WR11", "name"] == "WR11 (gam2 Vel)"
    assert (wr["kind"] == "star_wolf_rayet").all()
    assert (wr["t_collapse_myr"].between(0, 0.5)).all()
    assert (wr["t_birth_myr"] < 0).all()
    assert (wr["t_collapse_myr__tier"] == STATISTICAL).all()
    assert (wr["mass_msun__tier"] == SPECULATIVE).all()


def test_ob_loader_keeps_only_core_collapse_progenitors(catalog_paths):
    from veil.ingest import load_ob_stars
    ob = load_ob_stars(catalog_paths["ob_stars"]).set_index("id")
    # ALS 2 (~5 Msun) is too light; ALS 3 has no spectral type
    assert sorted(ob.index) == ["als:1", "als:4", "als:5"]
    assert ob.loc["als:1", "name"] == "HD 46223 (ALS 1)"
    assert (ob["mass_msun"] >= 8).all()
    assert (ob["mass_msun__tier"] == MODELED).all()
    remaining = ob["t_collapse_myr"] / ob["main_sequence_lifetime_myr"]
    assert remaining.between(0, 1).all()


def test_catalog_duplicates_are_dropped_by_sky_position(catalog_paths):
    entities = load_entities(catalog_paths)
    # ALS 4 sits on Spica, already a curated hazard: kept once, as the curated row
    assert "als:4" not in set(entities["id"])
    assert (entities["name"] == "Spica").sum() == 1
    hazards = entities[entities["kind"].isin(["star_massive_progenitor", "star_wolf_rayet"])]
    assert set(hazards["id"]) >= {"hyg:2", "wr:WR1", "als:1", "als:5"}
    assert entities["id"].is_unique


def test_hazards_reaching_culls_to_the_patch(catalog_paths):
    from veil.registry import SN_REACH_KPC, hazards_reaching
    entities = load_entities(catalog_paths)
    sun = np.array([-8.2, 0.0, 0.02])
    reaching = hazards_reaching(entities, sun, 0.25)
    assert (np.abs(reaching["x_gal_kpc"] - sun[0]) <= 0.25 + SN_REACH_KPC).all()
    assert (np.abs(reaching["z_gal_kpc"] - sun[2]) <= SN_REACH_KPC).all()
    far = entities[entities["id"] == "wr:WR1"]  # ~3 kpc away
    assert far["id"].iloc[0] not in set(reaching["id"])
    assert len(hazards_reaching(entities, sun, 0.25, project_onto_plane=True)) >= len(reaching)
