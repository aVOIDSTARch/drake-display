"""
veil -- the Phase 0 pipeline for The Drake Display.

Wires real catalog data into the fields library and renders the veil:

    fetch     download raw catalogs to data/raw/
    coords    ICRS (ra, dec, distance) -> galactocentric x, y, z in kpc
    ingest    raw catalogs -> one unified entity table
    registry  entities + configs -> LogOddsFields (galactic, local)
    interactive  Plotly HTML: veil surface, entity hover, time slider
    main      single entry point (python -m veil, or python src/main.py)
"""
