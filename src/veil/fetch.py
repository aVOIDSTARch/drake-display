"""
fetch.py

Downloads the Phase 0 raw catalogs (plan-phase0-veil-prototype.md 6.2)
into data/raw/ and records when each was retrieved, since the NASA
Exoplanet Archive is continuously updated and results must be
reproducible against a pinned retrieval date.
"""

import json
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

SOURCES = {
    HYG_FILE: HYG_URL,
    EXOPLANET_FILE: EXOPLANET_URL,
}


def fetch_missing(raw_dir: Path) -> list[str]:
    """Download any raw catalog not already present. Returns the
    names of files fetched. Existing files are never re-downloaded --
    delete one to refresh it."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    log_path = raw_dir / RETRIEVAL_LOG
    log = json.loads(log_path.read_text()) if log_path.exists() else {}

    fetched = []
    for name, url in SOURCES.items():
        target = raw_dir / name
        if target.exists():
            continue
        print(f"downloading {name} ...")
        partial = target.with_suffix(target.suffix + ".part")
        with urllib.request.urlopen(url, timeout=300) as response, open(partial, "wb") as out:
            while chunk := response.read(1 << 20):
                out.write(chunk)
        partial.rename(target)  # only a complete download gets the real name
        log[name] = {"url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        fetched.append(name)

    if fetched:
        log_path.write_text(json.dumps(log, indent=2) + "\n")
    return fetched
