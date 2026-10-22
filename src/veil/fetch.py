"""
fetch.py

Downloads the Phase 0 raw catalogs (plan-phase0-veil-prototype.md 6.2)
into data/raw/ and records when each was retrieved, since the NASA
Exoplanet Archive is continuously updated and results must be
reproducible against a pinned retrieval date.
"""

import http.client
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HYG_FILE = "hygdata_v41.csv"
EXOPLANET_FILE = "exoplanets_ps.csv"
RETRIEVAL_LOG = "retrieved.json"

HYG_URL = f"https://raw.githubusercontent.com/astronexus/HYG-Database/main/hyg/CURRENT/{HYG_FILE}"

# Columns per source-nasa-exoplanet-archive.md; default_flag=1 gives one row per planet
EXOPLANET_COLUMNS = [
    "pl_name", "hostname", "ra", "dec", "sy_dist", "sy_pnum",
    "st_teff", "st_rad", "st_mass", "st_met", "st_lum",
    "pl_rade", "pl_bmasse", "pl_orbsmax", "pl_orbper", "pl_eqt", "pl_insol",
]
EXOPLANET_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?" + urllib.parse.urlencode({
    "query": f"select {','.join(EXOPLANET_COLUMNS)} from ps where default_flag=1",
    "format": "csv",
})

VIZIER_TAP = "https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync"


def vizier_url(query: str) -> str:
    """A VizieR TAP synchronous query returning CSV."""
    return VIZIER_TAP + "?" + urllib.parse.urlencode({
        "REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "MAXREC": 1_000_000, "QUERY": query,
    })


# Massive-star catalogs (source-galactic-wr-catalogue.md, source-als-iii.md)
WR_FILE = "wolf_rayet_rate_crowther_2020.csv"
WR_URL = vizier_url(
    # E_Dist / e_Dist differ only by case, and ADQL names are case-insensitive unless quoted
    'SELECT WR, SpType, Name, RA_ICRS, DE_ICRS, Dist, "E_Dist", "e_Dist", logL '
    'FROM "J/MNRAS/493/1512/table1"'
)
OB_FILE = "als_iii_ob_stars.csv"
OB_URL = vizier_url(
    'SELECT ALS, GaiaDR2, GOSC, RAJ2000, DEJ2000, DistP50, DistP16, DistP84, SpType '
    'FROM "J/MNRAS/504/2968/tablea1"'
)

# Open clusters (source-hunt-reffert-clusters.md). Fetched through VizieR's
# ASU interface, which returns tab-separated text with a units row and a
# divider row under the header (see ingest.read_vizier_tsv).
CLUSTER_FILE = "hunt_reffert_2023_clusters.tsv"
CLUSTER_URL = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?" + urllib.parse.urlencode({
    "-source": "J/A+A/673/A114/clusters",
    "-out": "Name,Type,CST,N,RA_ICRS,DE_ICRS,dist16,dist50,dist84,logAge16,logAge50,logAge84,CMDCl50,r50pc",
    "-out.max": "unlimited",
})

SOURCES = {
    HYG_FILE: HYG_URL,
    EXOPLANET_FILE: EXOPLANET_URL,
    WR_FILE: WR_URL,
    OB_FILE: OB_URL,
    CLUSTER_FILE: CLUSTER_URL,
}

# Gaia DR3 survey sample (source-gaia-dr3.md): bright stars with precise
# parallaxes within ~5 kpc -- about 2.9 million rows, so it runs as an
# asynchronous TAP job rather than a synchronous query.
GAIA_TAP = "https://gea.esac.esa.int/tap-server/tap"
GAIA_FILE = "gaia_dr3_g12_poe10.csv"
GAIA_QUERY = (
    "SELECT ra, dec, parallax, phot_g_mean_mag, bp_rp FROM gaiadr3.gaia_source "
    "WHERE phot_g_mean_mag < 12 AND parallax_over_error > 10 AND parallax > 0.2"
)
GAIA_MAXREC = 3_500_000  # the archive caps results at a small default unless MAXREC is set
ASYNC_SOURCES = {
    GAIA_FILE: (GAIA_TAP, GAIA_QUERY, GAIA_MAXREC),
}
ASYNC_POLL_SECONDS = 10
DOWNLOAD_ATTEMPTS = 6
ASYNC_TIMEOUT_SECONDS = 3600


def run_async_tap(tap_base: str, query: str, maxrec: int) -> str:
    """Submit an asynchronous ADQL job, wait for it, and return the result URL."""
    data = urllib.parse.urlencode({
        "REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "PHASE": "RUN",
        "MAXREC": maxrec, "QUERY": query,
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(f"{tap_base}/async", data=data), timeout=120) as r:
        job_url = r.geturl()  # urllib follows the 303 redirect to the job resource
    deadline = time.monotonic() + ASYNC_TIMEOUT_SECONDS
    while True:
        with urllib.request.urlopen(f"{job_url}/phase", timeout=60) as r:
            phase = r.read().decode().strip()
        if phase == "COMPLETED":
            return f"{job_url}/results/result"
        if phase in ("ERROR", "ABORTED"):
            raise RuntimeError(f"TAP job {job_url} ended in phase {phase}")
        if time.monotonic() > deadline:
            raise TimeoutError(f"TAP job {job_url} still {phase} after {ASYNC_TIMEOUT_SECONDS} s")
        time.sleep(ASYNC_POLL_SECONDS)


def download(url: str, partial: Path) -> None:
    """Stream url into partial, retrying dropped connections. Each retry asks
    the server to resume from the bytes already written (an HTTP Range
    request); if it won't, the download starts again from the beginning."""
    for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
        have = partial.stat().st_size if partial.exists() else 0
        request = urllib.request.Request(url, headers={"Range": f"bytes={have}-"} if have else {})
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                resumed = have and response.status == 206
                with open(partial, "ab" if resumed else "wb") as out:
                    while chunk := response.read(1 << 20):
                        out.write(chunk)
            return
        except (http.client.IncompleteRead, ConnectionError, TimeoutError, urllib.error.URLError) as error:
            if attempt == DOWNLOAD_ATTEMPTS:
                raise
            print(f"  connection dropped ({type(error).__name__}); retrying ({attempt}/{DOWNLOAD_ATTEMPTS - 1}) ...")
            time.sleep(5 * attempt)


def fetch_missing(raw_dir: Path) -> list[str]:
    """Download any raw catalog not already present. Returns the
    names of files fetched. Existing files are never re-downloaded --
    delete one to refresh it."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    log_path = raw_dir / RETRIEVAL_LOG
    log = json.loads(log_path.read_text()) if log_path.exists() else {}

    fetched = []
    for name in [*SOURCES, *ASYNC_SOURCES]:
        target = raw_dir / name
        if target.exists():
            continue
        if name in ASYNC_SOURCES:
            tap_base, query, maxrec = ASYNC_SOURCES[name]
            print(f"running TAP job for {name} (this can take several minutes) ...")
            url = run_async_tap(tap_base, query, maxrec)
            entry = {"tap": tap_base, "query": query}
        else:
            url = SOURCES[name]
            entry = {"url": url}
        print(f"downloading {name} ...")
        partial = target.with_suffix(target.suffix + ".part")
        partial.unlink(missing_ok=True)
        download(url, partial)
        if name in ASYNC_SOURCES:
            rows = sum(1 for _ in open(partial, "rb")) - 1  # minus the header
            if rows >= ASYNC_SOURCES[name][2]:
                raise RuntimeError(f"{name}: {rows} rows hit the MAXREC cap, so the result is truncated")
            entry["rows"] = rows
        partial.rename(target)  # only a complete download gets the real name
        entry["retrieved_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        log[name] = entry
        fetched.append(name)

    if fetched:
        log_path.write_text(json.dumps(log, indent=2) + "\n")
    return fetched
