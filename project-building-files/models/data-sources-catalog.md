# Data Sources Catalog — Public Astronomical Data for the Habitability Veil Project

> Living reference. Every entry lists: **URL**, **access requirements**, **size/scale**, and **contents / relevance**. Grouped by function. Append new sources as we discover them; update figures as new data releases land. All listed sources are free/public unless noted. Figures marked "~" are approximate and worth reverifying at time of use.

---

## How to read this catalog: data levels and the "raw data" question

Astronomical data exists at **levels**, and knowing which level you're pulling matters:

- **Level 0/1 (raw / calibrated pixels):** detector output — images, spectra as recorded. Enormous, requires specialist pipelines to be useful.
- **Level 2 (epoch / per-observation):** calibrated individual measurements over time. (Gaia DR4 releases this for the first time — most of its ~400 TB.)
- **Level 3 (science-ready catalogs):** the distilled tables of positions, distances, temperatures, abundances, etc. **This is what the veil project should consume by default.**

**The honest rule of thumb:** the giant collaborations have already turned their raw data into reliable stellar-parameter catalogs better than an individual could. So *filling in entities* is best done by **joining existing Level-3 catalogs**, not by re-reducing raw spectra yourself. Re-processing raw data is a legitimate discipline ("archival astronomy") but a specialist one — reserve DIY effort for **cross-matching**, applying **published photometric relations**, and **population synthesis** (see §10), not for re-deriving parallaxes or abundances from pixels.

**The Milky-Way-vs-external-galaxy tradeoff (see §9):** per-entity 3D data (distance, motion, spectrum, planets) exists *only* for our own galaxy, because we're inside it. External galaxies give a clean external *view* and structural context but not per-star 3D or planets. Since you're rendering in software anyway, you can view the Milky Way from any angle — so the Milky Way wins for this project.

---

## 1. Astrometry & core stellar catalogs (your 3D backbone)

**Gaia (ESA)**

- URL: <https://gea.esac.esa.int/archive/> (portal: <https://www.cosmos.esa.int/web/gaia>)
- Access: free; web ADQL query interface, or Python `astroquery.gaia`; bulk download.
- Size: <cite index="50-1">DR3 (June 2022): over 1.8 billion sources (~10 TB).</cite> <cite index="48-1">DR4 (2 Dec 2026): ~2.8 billion processed sources (~2 billion high-quality), ~400 TB including epoch-level data.</cite>
- Contents: positions, parallax distances, proper motions, magnitudes, colors; radial velocities (~33M in DR3); astrophysical parameters (temperature, gravity, metallicity); variability. <cite index="48-1">DR4 adds an exoplanet list, non-single-star/binary solutions, and per-source epoch data.</cite> **The single most important source for this project** — precise 3D for the solar neighborhood, degrading with distance.

**AT-HYG / HYG Database (Astronexus)**

- URL: <https://github.com/astronexus/HYG-Database>
- Access: free; plain CSV on GitHub, no registration.
- Size: classic HYG ~120,000 stars; the newer AT-HYG (Augmented Tycho + Gaia) extends toward ~2.5 million stars. Tens of MB.
- Contents: merged Hipparcos/Yale/Gliese (+Gaia) with **pre-computed Cartesian x/y/z coordinates**, magnitudes, spectral types. **Your fastest Phase-0 on-ramp** — purpose-built for 3D star-map projects.

**Gaia Catalogue of Nearby Stars (GCNS)**

- URL: via Gaia archive (part of EDR3/DR3).
- Access: free.
- Size: 331,312 stars within ~100 pc.
- Contents: clean, near-complete census of the immediate solar neighborhood — ideal for a high-fidelity local core.

**Hipparcos / Tycho-2 (ESA, legacy)**

- URL: via VizieR/CDS (§4).
- Access: free.
- Size: Hipparcos ~118,000; Tycho-2 ~2.5 million.
- Contents: pre-Gaia astrometry; largely superseded by Gaia but useful for cross-ID and historical continuity.

---

## 2. Spectroscopic & chemical-abundance surveys (your metallicity field)

**APOGEE (SDSS)**

- URL: <https://www.sdss.org> (data: <https://www.sdss.org/dr18/>)
- Access: free; web query, CSV/FITS download.
- Size: ~657,000+ stars (SDSS DR17); SDSS-V ongoing.
- Contents: near-infrared spectra yielding [Fe/H], [α/Fe], and ~20 individual elemental abundances, radial velocities, temperatures. Near-IR penetrates dust — good for disk-plane coverage. **Primary basis for the metallicity ridge (veil factors 1/2/13).**

**GALAH (AAT)**

- URL: <https://www.galah-survey.org>
- Access: free; catalog download.
- Size: ~588,000 stars (DR3); ~917,000 (DR4).
- Contents: optical high-resolution spectra, up to ~30 elemental abundances — the finest chemical-tagging dataset in the southern sky.

**LAMOST (China)**

- URL: <http://www.lamost.org>
- Access: free.
- Size: ~10–20+ million spectra (DR8 and later) — the largest spectroscopic survey by count.
- Contents: stellar parameters, radial velocities, metallicities; enormous statistical coverage.

**RAVE (final, DR6)**

- URL: <https://www.rave-survey.org>
- Access: free.
- Size: ~500,000 stars.
- Contents: radial velocities and stellar parameters; a completed legacy southern survey.

---

## 3. Exoplanets (your "planet present" factor)

**NASA Exoplanet Archive**

- URL: <https://exoplanetarchive.ipac.caltech.edu>
- Access: free; web tables, TAP service, API, bulk CSV.
- Size: ~5,900+ confirmed planets (+ thousands of candidates); grows continually.
- Contents: host-star coordinates/distances, planet radii/masses/orbits, habitable-zone-relevant parameters. **Directly populates veil factor 5.** (Gaia DR4 will add an astrometric planet list.)

**ExoFOP**

- URL: <https://exofop.ipac.caltech.edu>
- Access: free (some follow-up data community-contributed).
- Size: follow-up data for TESS/Kepler targets.
- Contents: supplementary characterization of planet candidates.

---

## 4. Object registries & cross-identification (the "click an entity → info" backbone)

**SIMBAD (CDS Strasbourg)**

- URL: <http://simbad.cds.unistra.fr>
- Access: free; web, API, `astroquery.simbad`.
- Size: ~19 million objects.
- Contents: cross-identifications, object types, basic measurements, bibliography per object. **Your lookup layer for entity info panels.**

**VizieR (CDS Strasbourg)**

- URL: <https://vizier.cds.unistra.fr>
- Access: free; web, API, `astroquery.vizier`.
- Size: ~20,000+ published catalogs behind one interface.
- Contents: essentially every published astronomical table — the meta-source for hazard catalogs, abundance tables, etc.

**NED (NASA/IPAC Extragalactic Database)**

- URL: <https://ned.ipac.caltech.edu>
- Access: free.
- Size: hundreds of millions of extragalactic objects.
- Contents: galaxies and their properties — relevant if you extend beyond the Milky Way (§9).

**Aladin (CDS)**

- URL: <https://aladin.cds.unistra.fr>
- Access: free desktop/web sky atlas.
- Contents: interactive sky viewer overlaying images + catalogs; useful for exploration and prototyping.

---

## 5. Hazard-source catalogs (where you place the dips)

**ATNF Pulsar Catalogue (CSIRO)**

- URL: <https://www.atnf.csiro.au/research/pulsar/psrcat>
- Access: free; web query + downloadable.
- Size: ~3,700 pulsars/neutron stars.
- Contents: positions, distances, spin/magnetic parameters — for veil factor 14 (nearby neutron star/magnetar).

**Green's Catalogue of Galactic SNRs (Cambridge)**

- URL: <https://www.mrao.cam.ac.uk/surveys/snrs/>
- Access: free.
- Size: ~310 supernova remnants.
- Contents: positions, sizes, types — records of past supernovae (context for factor 8).

**Galactic Wolf-Rayet Catalogue**

- URL: via VizieR (also community-maintained lists).
- Access: free.
- Size: ~650+ WR stars.
- Contents: the collapsar / long-GRB and core-collapse progenitor candidates — **the sources of your most dramatic time-evolving dips (factors 8/9).**

---

## 6. Photometric & imaging all-sky surveys (breadth, and dust-penetrating IR)

**2MASS (Two Micron All-Sky Survey)**

- URL: <https://irsa.ipac.caltech.edu> (§11)
- Access: free.
- Size: ~470 million point sources.
- Contents: near-infrared photometry, all-sky; sees through dust better than optical.

**WISE / AllWISE / CatWISE (NASA)**

- URL: <https://irsa.ipac.caltech.edu>
- Access: free.
- Size: AllWISE ~750 million; CatWISE ~1.9 billion.
- Contents: mid-infrared all-sky photometry; excellent for cool stars, dusty regions, brown dwarfs.

**Pan-STARRS (MAST)**

- URL: <https://catalogs.mast.stsci.edu>
- Access: free.
- Size: ~3 billion sources.
- Contents: deep optical imaging/photometry of ~3/4 of the sky.

**SDSS imaging & spectra**

- URL: <https://www.sdss.org>
- Access: free.
- Size: ~1 billion+ photometric objects; millions of spectra (DR18/DR19).
- Contents: multiband imaging + spectroscopy; foundational multi-purpose survey.

---

## 7. Time-domain surveys & the coming firehose

**TESS (MAST)**

- URL: <https://archive.stsci.edu/tess/>
- Access: free.
- Size: TESS Input Catalog ~1.7 billion stars; full-frame images all-sky.
- Contents: light curves, transiting-planet detections, stellar variability.

**Kepler / K2 (MAST)**

- URL: <https://archive.stsci.edu/kepler/>
- Access: free.
- Size: ~200,000 primary targets; ~half-million+ light curves.
- Contents: the highest-precision transit photometry; foundational for planet-occurrence statistics.

**ZTF (Zwicky Transient Facility)**

- URL: <https://www.ztf.caltech.edu>
- Access: free public data releases + alert streams.
- Contents: time-domain optical survey — supernovae, variables, transients.

**Vera C. Rubin Observatory / LSST**

- URL: <https://rubinobservatory.org>
- Access: alert streams public; full data via Rubin Science Platform (data rights phased; public releases planned).
- Size: <cite index="59-1">~20 TB raw/night; ~60 PB raw over 10 years; ~500 PB fully processed</cite>; <cite index="58-1">a catalog of ~40 billion sources and 30 trillion brightness measurements, ~10 million alerts every 60 seconds.</cite> <cite index="61-1">The survey officially began 30 June 2026.</cite>
- Contents: the deepest, widest optical time-domain survey ever — will transform stellar, transient, and Milky Way structure data over the coming decade. **The future firehose validating your intuition about vast, freshly-collected data.**

---

## 8. Interstellar medium, dust & galactic structure (realism + the model substrate)

**3D Dust Maps (Bayestar / "argonaut"; Edenhofer et al. 2024)**

- URL: <https://argonaut.skymaps.info> (Bayestar); Edenhofer map via published data.
- Access: free; query API and downloadable cubes.
- Size: 3D reddening cubes; Edenhofer (2024) high-resolution out to ~1.25 kpc.
- Contents: dust/extinction as a function of 3D position — for obscuration realism and correcting stellar data.

**BeSSeL Survey (maser parallaxes / spiral-arm model)**

- URL: <http://bessel.vlbi-astrometry.org>
- Access: free; published model parameters.
- Size: hundreds of high-mass star-forming region parallaxes.
- Contents: the empirical geometry of the Milky Way's **spiral arms and bar** — **your "structural model substrate" for the regions Gaia can't resolve** (factor 12, and the disk skeleton itself).

---

## 9. External galaxies (the face-on question — context, not per-entity 3D)

**PHAT / PHAST — Panchromatic Hubble Andromeda Treasury (M31)**

- URL: via MAST (<https://archive.stsci.edu>).
- Access: free.
- Size: <cite index="68-1">PHAT: ~117 million resolved stars over ~1/3 of M31's disk</cite>; <cite index="74-1">PHAST extends coverage to ~two-thirds of the disk with 90+ million more stars.</cite>
- Contents: six-band UV-to-IR photometry giving per-star temperature, luminosity, and extinction. **Crucial caveat for the veil project:** these are <cite index="68-1">"equidistant" stars — all placed at M31's single distance, i.e. 2D-projected photometry with no individual depth/3D and no planets</cite>, and M31 is inclined ~77° (not face-on). Superb for *structural/statistical* context; not a substitute for the Milky Way's per-entity 3D data.
- Other resolved-star targets: the **Magellanic Clouds**, **M33 (Triangulum)**, and Local Group dwarfs (nearer, individually resolved, still 2D-projected, no planets). Truly face-on spirals (M101, M74/NGC 628, M51) are far more distant and resolve into far fewer, poorer-characterized stars.

---

## 10. Population synthesis & models (honestly filling the unobserved galaxy)

**Galaxia**

- URL: <http://galaxia.sourceforge.net>
- Access: free software.
- Contents: generates statistically realistic synthetic stellar populations from a Milky Way model — for populating regions no telescope has resolved.

**TRILEGAL**

- URL: <http://stev.oapd.inaf.it/cgi-bin/trilegal>
- Access: free web interface + downloadable.
- Contents: population-synthesis star counts for any line of sight/volume. **The principled way to fill the far side of the disk** (your "speculative data first" approach, done rigorously).

---

## 11. Major archives (raw & intermediate data — for DIY reprocessing, per §"data levels")

**MAST — Mikulski Archive for Space Telescopes (STScI)**

- URL: <https://archive.stsci.edu>
- Access: free.
- Contents: raw + processed data for HST, JWST, TESS, Kepler/K2, Pan-STARRS, and more. **The main archive if you ever do reprocess space-telescope data.**

**IRSA — NASA/IPAC Infrared Science Archive**

- URL: <https://irsa.ipac.caltech.edu>
- Access: free.
- Contents: 2MASS, WISE, Spitzer, and infrared survey holdings — raw to catalog level.

**ESO Science Archive**

- URL: <https://archive.eso.org>
- Access: free (after proprietary period).
- Contents: raw + processed ground-based data from ESO's telescopes (VLT, etc.).

**CDS (Strasbourg Astronomical Data Center)**

- URL: <https://cds.unistra.fr>
- Access: free.
- Contents: hosts SIMBAD, VizieR, and Aladin — the connective tissue of public astronomy; your first stop for finding *any* catalog.

---

## 12. Visualization tools & prior art (learn from, don't reinvent)

**Gaia Sky (ESA, open source)**

- URL: <https://zah.uni-heidelberg.de/gaia/outreach/gaiasky> (source on GitLab/GitHub)
- Access: free, open source.
- Contents: <cite index="52-1">a real-time 3D galaxy explorer built specifically to navigate Gaia data</cite>. **The closest existing thing to your dream — study its architecture directly.**

**OpenSpace (NASA-affiliated, open source)**

- URL: <https://www.openspaceproject.com>
- Access: free, open source.
- Contents: mature interactive astrovisualization engine with time controls and large-dataset handling.

**Celestia**

- URL: <https://celestiaproject.space>
- Access: free, open source.
- Contents: real-time 3D space simulation; lighter-weight, good reference for interaction patterns.
