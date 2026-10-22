"""
ingest.py

Raw catalogs -> one unified entity table (plan-phase0 6.3-6.5), following
the field maps in project-building-files/data/external-sources/:

    load_hyg          stars from HYG (positions measured; mass, teff,
                      luminosity estimated; feh modeled from the gradient)
    load_hazards      curated massive stars, joined to HYG by Hipparcos number
    load_exoplanets   planetary systems + planets from the NASA Exoplanet Archive
    load_entities     all of the above, one row per entity

Column names follow entity.md. Values that are unknown stay NaN -- never
zero. Each row also carries a confidence for the fields the field model
reads (conf_position, conf_mass_msun, conf_feh, conf_clock), taken from
the source field maps; that is the input side of EQ-CORE-4.

Entity resolution between sources is a no-op in Phase 0 (pipeline-idea-v2
3.2): exoplanet hosts are kept as their own planetary_system entities.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

from fields.kernels import MetallicityBandKernel
from fields.temporal import ms_lifetime_myr

from .coords import to_galactocentric

HYG_UNKNOWN_DISTANCE_PC = 100000  # HYG sentinel for "distance unknown"
SOLAR_ABSMAG_V = 4.83
MASS_LUMINOSITY_EXPONENT = 3.5    # L ~ M^3.5, main sequence only
HZ_FLUX_INNER = 1.1               # S_inner, factors.md Appendix A
HZ_FLUX_OUTER = 0.35              # S_outer

# Confidences from the source field maps (source-at-hyg.md, source-nasa-exoplanet-archive.md)
CONF = {
    "hyg_position": 0.85,
    "hyg_mass": 0.50,
    "hyg_teff": 0.65,
    "hyg_luminosity": 0.80,
    "modeled_feh": 0.40,
    "exo_position": 0.90,
    "exo_mass": 0.70,
    "exo_feh": 0.85,
    "curated_mass": 0.30,   # hand-entered, see data/curated/phase0_hazard_stars.csv
    "scenario_clock": 0.10,  # t_collapse is a scenario assignment, not a measurement
}

ENTITY_COLUMNS = [
    "id", "name", "kind", "is_speculative", "data_source",
    "ra_icrs_deg", "dec_icrs_deg", "distance_pc",
    "x_gal_kpc", "y_gal_kpc", "z_gal_kpc", "r_gal_kpc", "z_height_kpc",
    "mag_apparent_v", "mag_absolute_v", "color_bv", "spectral_type",
    "luminosity_lsun", "teff_k", "mass_msun", "feh",
    "main_sequence_lifetime_myr", "t_birth_myr", "t_collapse_myr",
    "num_planets", "num_planets_in_hz", "parent_star_id",
    "planet_radius_rearth", "insolation_earth_equiv", "in_habitable_zone",
    "conf_position", "conf_mass_msun", "conf_feh", "conf_clock",
]

_LUMINOSITY_CLASS = re.compile(r"\d(?:\.\d+)?\s*(Iab|Ia|Ib|III|II|IV|VI|V|I)(?![a-z]*[IV])")
_GRADIENT = MetallicityBandKernel()  # holds EQ-CHEM-1 with the Appendix A constants


def _add_positions(df: pd.DataFrame) -> pd.DataFrame:
    x, y, z = to_galactocentric(df["ra_icrs_deg"], df["dec_icrs_deg"], df["distance_pc"])
    df["x_gal_kpc"], df["y_gal_kpc"], df["z_gal_kpc"] = x, y, z
    df["r_gal_kpc"] = np.hypot(x, y)  # EQ-GEO-3
    df["z_height_kpc"] = np.abs(z)
    return df


def modeled_feh(r_gal_kpc) -> np.ndarray:
    """EQ-CHEM-1: [Fe/H] from galactocentric radius (Modeled, conf 0.40)."""
    return _GRADIENT.feh(np.asarray(r_gal_kpc, dtype=float))


def luminosity_class(spectral_type) -> str | None:
    """Roman-numeral luminosity class from a spectral type, e.g. 'M2Ib' -> 'Ib'."""
    if not isinstance(spectral_type, str):
        return None
    match = _LUMINOSITY_CLASS.search(spectral_type)
    return match.group(1) if match else None


def classify_star(spectral_type) -> str:
    """entity.md kind from spectral type. Stars with no luminosity class
    default to main sequence, the most common case."""
    if isinstance(spectral_type, str) and spectral_type.startswith("D"):
        return "white_dwarf"
    lum_class = luminosity_class(spectral_type)
    if lum_class in ("I", "Ia", "Iab", "Ib"):
        return "star_supergiant"
    if lum_class in ("II", "III"):
        return "star_giant"
    return "star_main_sequence"


def load_hyg(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, low_memory=False)

    # Filter: distance unknown or non-positive -> can't place in 3D. The Sun
    # (dist 0, id 0) is kept: it is the reference point, not a bad row.
    is_sun = raw["id"] == 0
    has_distance = raw["dist"].notna() & (raw["dist"] > 0) & (raw["dist"] < HYG_UNKNOWN_DISTANCE_PC)
    raw = raw[has_distance | is_sun].copy()

    df = pd.DataFrame({
        "id": "hyg:" + raw["id"].astype(str),
        "hip": raw["hip"],
        "name": raw["proper"],
        "ra_icrs_deg": raw["ra"] * 15.0,   # HYG ra is in HOURS
        "dec_icrs_deg": raw["dec"],
        "distance_pc": raw["dist"],
        "mag_apparent_v": raw["mag"],
        "mag_absolute_v": raw["absmag"],
        "color_bv": raw["ci"],
        "spectral_type": raw["spect"],
    })
    df["kind"] = df["spectral_type"].map(classify_star)
    df["is_speculative"] = False
    df["data_source"] = "HYG v4.1"

    df["luminosity_lsun"] = 10 ** (0.4 * (SOLAR_ABSMAG_V - df["mag_absolute_v"]))
    # Ballesteros (2012) B-V -> Teff
    bv = df["color_bv"]
    df["teff_k"] = 4600.0 * (1 / (0.92 * bv + 1.7) + 1 / (0.92 * bv + 0.62))
    # Mass-luminosity is main-sequence only; leave giants etc. unknown
    is_ms = df["kind"] == "star_main_sequence"
    df["mass_msun"] = np.where(is_ms, df["luminosity_lsun"] ** (1 / MASS_LUMINOSITY_EXPONENT), np.nan)

    df = _add_positions(df)
    df["feh"] = modeled_feh(df["r_gal_kpc"])

    df["conf_position"] = CONF["hyg_position"]
    df["conf_mass_msun"] = np.where(df["mass_msun"].notna(), CONF["hyg_mass"], np.nan)
    df["conf_feh"] = CONF["modeled_feh"]
    return df


def load_hazards(path: Path, stars: pd.DataFrame) -> pd.DataFrame:
    """Curated massive stars, positioned from their HYG rows. Returns new
    entity rows (kind star_massive_progenitor); the matching HYG rows
    should be dropped so each star appears once."""
    curated = pd.read_csv(path, comment="#")
    candidates = stars[stars["hip"].isin(curated["hip"])]
    joined = curated.merge(candidates.drop(columns=["name", "mass_msun", "conf_mass_msun"]),
                           on="hip", how="left", validate="one_to_one")
    unmatched = joined.loc[joined["id"].isna(), "name"].tolist()
    if unmatched:
        raise ValueError(f"hazard stars with no usable HYG row: {unmatched}")

    df = joined.copy()
    df["kind"] = "star_massive_progenitor"
    df["is_speculative"] = True  # mass and clock are hand-assigned
    df["data_source"] = "HYG v4.1 + curated Phase 0 hazard list"
    df["main_sequence_lifetime_myr"] = df["mass_msun"].map(ms_lifetime_myr)
    df["t_birth_myr"] = df["t_collapse_myr"] - df["main_sequence_lifetime_myr"]
    unborn = df.loc[df["t_birth_myr"] > 0, "name"].tolist()
    if unborn:
        raise ValueError(f"t_collapse_myr is later than the EQ-STAR-1 lifetime allows, so these "
                         f"stars would be born in the future: {unborn}")
    df["conf_mass_msun"] = CONF["curated_mass"]
    df["conf_clock"] = CONF["scenario_clock"]
    return df


def _planet_kind(radius_rearth: float, mass_mearth: float) -> str:
    """entity.md planet kind from radius (R_earth), falling back to mass (M_earth)."""
    if not np.isnan(radius_rearth):
        bounds, value = (1.25, 2.0, 6.0), radius_rearth
    elif not np.isnan(mass_mearth):
        bounds, value = (2.0, 10.0, 50.0), mass_mearth
    else:
        return "exoplanet_unclassified"
    kinds = ("planet_terrestrial", "planet_super_earth", "planet_mini_neptune")
    for bound, kind in zip(bounds, kinds):
        if value < bound:
            return kind
    return "planet_gas_giant"


def load_exoplanets(path: Path) -> pd.DataFrame:
    """Planets and their planetary_system hosts."""
    raw = pd.read_csv(path)
    raw = raw.dropna(subset=["ra", "dec", "sy_dist"])
    raw = raw[raw["sy_dist"] > 0]

    # EQ-HZ-1 where the archive has no insolation: S = L / a^2, st_lum is log10(L/Lsun)
    insolation = raw["pl_insol"].fillna(10 ** raw["st_lum"] / raw["pl_orbsmax"] ** 2)
    in_hz = insolation.between(HZ_FLUX_OUTER, HZ_FLUX_INNER).where(insolation.notna())

    planets = pd.DataFrame({
        "id": "exo:" + raw["pl_name"],
        "name": raw["pl_name"],
        "kind": [_planet_kind(r, m) for r, m in zip(raw["pl_rade"], raw["pl_bmasse"])],
        "parent_star_id": "exo-sys:" + raw["hostname"],
        "ra_icrs_deg": raw["ra"],
        "dec_icrs_deg": raw["dec"],
        "distance_pc": raw["sy_dist"],
        "planet_radius_rearth": raw["pl_rade"],
        "insolation_earth_equiv": insolation,
        "in_habitable_zone": in_hz,
    })

    hosts = raw.groupby("hostname", sort=False).first()
    hz_counts = in_hz.fillna(False).astype(bool).groupby(raw["hostname"]).sum()
    systems = pd.DataFrame({
        "id": "exo-sys:" + hosts.index,
        "name": hosts.index,
        "kind": "planetary_system",
        "ra_icrs_deg": hosts["ra"].to_numpy(),
        "dec_icrs_deg": hosts["dec"].to_numpy(),
        "distance_pc": hosts["sy_dist"].to_numpy(),
        "teff_k": hosts["st_teff"].to_numpy(),
        "mass_msun": hosts["st_mass"].to_numpy(),
        "feh": hosts["st_met"].to_numpy(),
        "luminosity_lsun": (10 ** hosts["st_lum"]).to_numpy(),
        "num_planets": hosts["sy_pnum"].to_numpy(),
        "num_planets_in_hz": hz_counts.reindex(hosts.index).to_numpy(),
    })

    df = pd.concat([systems, planets], ignore_index=True)
    df["is_speculative"] = False
    df["data_source"] = "NASA Exoplanet Archive (PS, default_flag=1)"
    df = _add_positions(df)

    # Spectroscopic st_met surfaces over the modeled gradient where present
    measured_feh = df["feh"].notna()
    df.loc[~measured_feh & (df["kind"] == "planetary_system"), "feh"] = modeled_feh(
        df.loc[~measured_feh & (df["kind"] == "planetary_system"), "r_gal_kpc"])
    df["conf_feh"] = np.where(measured_feh, CONF["exo_feh"],
                              np.where(df["feh"].notna(), CONF["modeled_feh"], np.nan))
    df["conf_position"] = CONF["exo_position"]
    df["conf_mass_msun"] = np.where(df["mass_msun"].notna(), CONF["exo_mass"], np.nan)
    return df


def load_entities(paths: dict[str, Path]) -> pd.DataFrame:
    """paths: {"hyg": ..., "exoplanets": ..., "hazards": ...} -> unified entity table."""
    stars = load_hyg(paths["hyg"])
    hazards = load_hazards(paths["hazards"], stars)
    stars = stars[~stars["id"].isin(hazards["id"])]
    exoplanets = load_exoplanets(paths["exoplanets"])

    entities = pd.concat([stars, hazards, exoplanets], ignore_index=True)
    for column in ENTITY_COLUMNS:
        if column not in entities:
            entities[column] = np.nan
    return entities[ENTITY_COLUMNS]
