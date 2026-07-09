# Entity Schema — Complete Field Definition for the Galactic Habitability Veil

> This document defines the data model for **every entity** — star, planet, hazard source, remnant, cluster — that appears on the veil map and can be clicked or hovered for information. It is the **contract** between the data pipeline (ingestion → coordinate transform → enrichment → model evaluation) and the renderer. All downstream code consumes this schema. When a new data source or computed field is introduced, it is added here first, then propagated backward through the pipeline. Referenced by `plan-phase0-veil-prototype.md` (§6.5, the unified entity table) and `spec-galactic-habitability-veil.md`.

---

## Design conventions

- **Naming:** `snake_case`, with unit suffixes where meaningful (`_kpc`, `_pc`, `_msun`, `_myr`, `_k`, `_au`). Predictable names let the renderer bind fields generically.
- **Units:** stated explicitly per field. Positions in kiloparsecs (galactocentric) and parsecs (heliocentric distance); masses in solar masses; temperatures in kelvin; times in megayears; planetary distances in astronomical units.
- **Nullability:** only the **core** group is required for *every* entity. All other groups are conditionally populated by `kind` (a planet has no `spectral_type`; a black hole has no `habitable_zone`). Missing values are explicit NULL, never silently zero — zero and unknown must be distinguishable in the field math.
- **Provenance philosophy:** every physically meaningful value should be traceable to a source and flagged as measured vs. modeled (`is_speculative`, `data_source`). This powers the observed-vs-speculative shading that keeps the veil honest.
- **Growth rule:** the schema only ever *grows*. Fields are never removed, so older cached entities stay valid.

---

## 1. Core identity & classification — *required for all entities*

| Field | Type | Units | Required | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | string | — | ✓ | catalog-native or synthetic UUID | Unique across the entity table; stable across updates; used for cross-reference, hover persistence, bookmarking |
| `name` | string | — | — | catalog | User-facing display name; may be empty for faint stars |
| `catalog_name` | string | — | — | catalog | Formal designation, e.g. `Gaia DR3 4657...`, `HIP 27989`, `SNR Cas A` |
| `aliases` | string[] | — | — | enrichment (SIMBAD) | Alternative designations for search/cross-ID |
| `kind` | enum | — | ✓ | ingestion logic | See enum list below; drives rendering style, click behavior, and which field groups apply |
| `is_speculative` | bool | — | ✓ | pipeline | `true` if position/properties are modeled (population synthesis, estimation); `false` if from real survey. Drives provenance shading |

**`kind` enumeration:** `star_main_sequence`, `star_giant`, `star_supergiant`, `star_wolf_rayet`, `star_massive_progenitor`, `brown_dwarf`, `white_dwarf`, `neutron_star`, `pulsar`, `magnetar`, `black_hole`, `planet_terrestrial`, `planet_super_earth`, `planet_mini_neptune`, `planet_gas_giant`, `exoplanet_candidate`, `planetary_system`, `open_cluster`, `globular_cluster`, `supernova_remnant`, `hazard_collapsar`, `hazard_grb_candidate`, `dark_star_candidate`, `region_marker`.

---

## 2. Positioning & coordinates — *required for all entities*

| Field | Type | Units | Required | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| `ra_icrs_deg` | float | degrees | ✓ | catalog | Right ascension, ICRS (0–360) |
| `dec_icrs_deg` | float | degrees | ✓ | catalog | Declination, ICRS (−90 to +90) |
| `distance_pc` | float | parsecs | ✓ | catalog (parallax → 1000/parallax_mas) or photometric | Heliocentric distance; guard against non-positive parallax; NULL if unmeasurable |
| `distance_err_pc` | float | parsecs | — | catalog | 1σ uncertainty; flags low-confidence placement |
| `x_gal_kpc` | float | kiloparsecs | ✓ | computed (astropy `Galactocentric`) | Galactocentric Cartesian x |
| `y_gal_kpc` | float | kiloparsecs | ✓ | computed | Galactocentric Cartesian y |
| `z_gal_kpc` | float | kiloparsecs | ✓ | computed | Galactocentric Cartesian z (perpendicular to disk) |
| `r_gal_kpc` | float | kiloparsecs | ✓ | derived √(x²+y²) | Galactocentric cylindrical radius; cached — the primary input to radius-dependent factors (metallicity, density) |
| `z_height_kpc` | float | kiloparsecs | ✓ | derived \|z\| | Absolute height off the plane; distinguishes thin-disk / thick-disk / halo |

---

## 3. Astrometry & motion — *optional (stars/remnants)*

| Field | Type | Units | Source | Notes |
| --- | --- | --- | --- | --- |
| `parallax_mas` | float | milliarcsec | Gaia/Hipparcos | Inverse gives distance |
| `pm_ra_mas_yr` | float | mas/yr | Gaia | Proper motion in RA; enables position extrapolation in time |
| `pm_dec_mas_yr` | float | mas/yr | Gaia | Proper motion in Dec |
| `radial_velocity_km_s` | float | km/s | APOGEE/GALAH/Gaia | Heliocentric line-of-sight velocity |
| `space_velocity_uvw_km_s` | float[3] | km/s | derived | Full galactocentric velocity vector; for kinematic-population tagging |

---

## 4. Stellar physical properties — *conditional on stellar `kind`*

| Field | Type | Units | Source | Notes |
| --- | --- | --- | --- | --- |
| `mass_msun` | float | M☉ | spectroscopy or mass–luminosity relation | May be estimated; **drives the main-sequence-lifetime clock** |
| `mass_err_msun` | float | M☉ | catalog | 1σ; flags calibration confidence |
| `radius_rsun` | float | R☉ | measured or Stefan–Boltzmann | From luminosity + temperature |
| `teff_k` | float | kelvin | spectroscopy or color calibration | Sets the emitted spectrum (Wien) → energy-availability factor |
| `logg_cgs` | float | dex (cgs) | spectroscopy | Surface gravity; separates dwarfs from giants |
| `luminosity_lsun` | float | L☉ | derived | From radius+temp or parallax+magnitude; sets habitable-zone boundaries |
| `mag_apparent_v` | float | mag | catalog | Apparent visual magnitude |
| `mag_absolute_v` | float | mag | derived | From distance + apparent magnitude |
| `color_bv` | float | mag | photometry | B−V index; proxy for temperature |
| `spectral_type` | string | — | catalog or derived | e.g. `G2V`, `M3`, `O9`, `WC8`; drives filter UI |
| `extinction_av` | float | mag | 3D dust maps | V-band dust dimming; needed to de-redden luminosity |
| `rotational_velocity_km_s` | float | km/s | spectroscopy | High v·sin i → activity, flares, shorter stable window |
| `activity_level` | enum | — | derived | `quiet` / `moderate` / `active` / `superflare_prone`; feeds flare-hazard factor |
| `log_lx_lbol` | float | dex | catalog/derived | X-ray-to-bolometric ratio; high-energy output diagnostic |

---

## 5. Chemical composition & enrichment — *conditional on stellar `kind`*

| Field | Type | Units | Source | Notes |
| --- | --- | --- | --- | --- |
| `feh` | float | dex | spectroscopy (APOGEE/GALAH) or **modeled `feh(R)`** | [Fe/H] vs. solar; **primary input to the metallicity-ridge factor**; if measured absent, filled from the radial gradient (flag via `is_speculative`) |
| `feh_err` | float | dex | catalog | 1σ; distinguishes spectroscopic from grid-interpolated |
| `alpha_fe` | float | dex | spectroscopy | [α/Fe]; high → rapid early star formation (thick-disk marker) |
| `abundance_c` | float | dex | spectroscopy | [C/H] |
| `abundance_n` | float | dex | spectroscopy | [N/H] |
| `abundance_o` | float | dex | spectroscopy | [O/H]; water & rocky-body composition |
| `abundance_mg` | float | dex | spectroscopy | [Mg/H]; terrestrial cores, chlorophyll |
| `abundance_si` | float | dex | spectroscopy | [Si/H]; mantle/rock composition |
| `abundance_th_u_proxy` | float | dex | spectroscopy/derived | Radiogenic-heat proxy (Th/U); tectonic & dynamo longevity |

---

## 6. Temporal & evolutionary properties — *drives the time slider*

| Field | Type | Units | Source | Notes |
| --- | --- | --- | --- | --- |
| `main_sequence_lifetime_myr` | float | Myr | derived | ~10⁴·(M/M☉)^−2.5 Myr; the hazard clock |
| `t_birth_myr` | float | Myr | catalog (clusters) or assigned | Formation time on the scenario timeline |
| `t_collapse_myr` | float | Myr | derived | `t_birth + main_sequence_lifetime`; when a massive star's dip spikes |
| `age_myr` | float | Myr | catalog or model | Current age (for clusters, isochrone-derived) |
| `evolutionary_state` | enum | — | derived at scenario time | `pre_ms`/`main_sequence`/`subgiant`/`giant`/`agb`/`death_imminent`/`remnant_wd`/`remnant_ns`/`remnant_bh` |
| `remaining_stable_myr` | float | Myr | derived at scenario time | Stable lifetime left at current slider position |

---

## 7. Planetary-system properties — *conditional on host `kind`*

| Field | Type | Units | Source | Notes |
| --- | --- | --- | --- | --- |
| `num_planets` | int | — | Exoplanet Archive | Confirmed planet count |
| `num_planets_in_hz` | int | — | derived | Count within the habitable zone |
| `hz_inner_au` | float | AU | derived | Inner habitable-zone edge from luminosity |
| `hz_outer_au` | float | AU | derived | Outer habitable-zone edge |

---

## 8. Planet-specific properties — *conditional on planet `kind`*

| Field | Type | Units | Source | Notes |
| --- | --- | --- | --- | --- |
| `parent_star_id` | string | — | Exoplanet Archive | Foreign key to host entity; enables hierarchical/tree UI |
| `planet_mass_mearth` | float | M⊕ | transit/RV | Often a lower bound |
| `planet_radius_rearth` | float | R⊕ | transit/imaging | |
| `semi_major_axis_au` | float | AU | catalog | Orbital distance; sets irradiance & HZ status |
| `orbital_period_days` | float | days | derived (Kepler III) | |
| `eq_temp_k` | float | kelvin | derived | Equilibrium temperature (albedo ~0.3); climate regime |
| `insolation_earth_equiv` | float | S⊕ | derived | Stellar flux vs. Earth (1.0 = Earth); habitability proxy |
| `in_habitable_zone` | bool | — | derived | Orbit vs. computed HZ |
| `planet_type` | enum | — | derived | `terrestrial`/`super_earth`/`mini_neptune`/`gas_giant`/`sub_stellar` |

---

## 9. Hazard-specific properties — *conditional on hazard `kind`*

| Field | Type | Units | Source | Notes |
| --- | --- | --- | --- | --- |
| `hazard_type` | enum | — | ingestion | `core_collapse_sn`/`type_ia_sn`/`long_grb`/`short_grb`/`magnetar_flare`/`stellar_flare`/`crowding` |
| `kill_radius_kpc` | float | kpc | factors / literature | Lethal reach (ozone-destruction distance); ~0.01 kpc for SN, ~1–2 kpc for beamed long GRB |
| `is_beamed` | bool | — | model | GRBs are beamed → only targets in the jet are affected (probabilistic contribution) |
| `beam_direction_deg` | float[2] | degrees | model | Jet orientation, if beamed |
| `hazard_luminosity_erg_s` | float | erg/s | catalog/model | Energy output; scales lethality |
| `temporal_profile` | enum | — | factors | Which `g(t)`: `ramp_to_collapse`/`spike_and_decay`/`persistent` |
| `hazard_onset_myr` | float | Myr | derived | When the hazard becomes active on the timeline |

---

## 10. Habitability-model outputs — *computed per entity at the current scenario time*

| Field | Type | Units | Source | Notes |
| --- | --- | --- | --- | --- |
| `factor_contributions` | dict{string→float} | — | `field.py` at render | Per-factor influence at this location/time; lets the UI explain *why* habitability is high/low here |
| `logit_here` | float | log-odds | `field.py` | Sum of all factor logits at this entity's position (pre-`expit`) |
| `habitability_here` | float | probability [0,1] | `field.py` | `expit(logit_here)`; the veil's height at this entity's (x,y) |
| `confidence_here` | float | [0,1] | derived | Aggregate backing-weight / data-quality at this location; drives provenance shading |

---

## 11. Provenance & metadata — *system/UI plumbing*

| Field | Type | Units | Source | Notes |
| --- | --- | --- | --- | --- |
| `data_source` | string | — | ingestion | Primary catalog of origin (e.g. `Gaia DR3`, `NASA Exoplanet Archive`, `TRILEGAL synthetic`) |
| `data_source_ids` | dict | — | enrichment | Per-catalog IDs for cross-reference |
| `last_updated` | datetime | ISO 8601 | pipeline | For cache invalidation and freshness UX |
| `render_hint` | dict | — | renderer | Optional style overrides (icon, color, size scaling) |

---

## Field-group applicability by `kind` (quick reference)

- **Main-sequence / giant star:** groups 1, 2, 3, 4, 5, 6, 10, 11 (+ 7 if it hosts planets).
- **Massive progenitor / collapsar / GRB candidate:** groups 1, 2, 4, 6, 9, 10, 11 — the time-evolving hazard drivers.
- **Remnant (WD / NS / pulsar / magnetar / BH):** groups 1, 2, 6, 9 (for NS/magnetar flares), 10, 11.
- **Planet:** groups 1, 2, 8, 10, 11 (+ links to parent via `parent_star_id`).
- **Cluster / region marker:** groups 1, 2, 10, 11 (aggregate/statistical).

---

## Minimum viable subset for Phase 0

To stand up the Phase 0 prototype, only these are strictly required per entity: `id`, `kind`, `is_speculative`, `x_gal_kpc`, `y_gal_kpc`, `z_gal_kpc`, `r_gal_kpc`, `distance_pc`, and — for stars — `mass_msun` and `feh` (the latter may be modeled from the radial gradient), plus `t_birth_myr` and `main_sequence_lifetime_myr` for any entity that acts as a time-evolving hazard. Everything else is enrichment layered on in later phases.
