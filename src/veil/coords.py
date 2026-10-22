"""
coords.py

EQ-GEO-2: ICRS (ra, dec, heliocentric distance) -> galactocentric
Cartesian (x, y, z) in kpc, via astropy. Never use a catalog's own
x/y/z columns -- HYG's are heliocentric equatorial (ADR-003).

The Sun's position is pinned to factors.md Appendix A (R0 = 8.2 kpc,
z0 = 20 pc) rather than astropy's defaults, so the coordinate frame
and the model's radial profiles agree on where the Sun is. In this
frame the galactic center is the origin and the Sun sits near
(-8.2, 0, +0.02).
"""

import numpy as np
import astropy.units as u
from astropy.coordinates import Galactocentric, SkyCoord

R0_KPC = 8.2     # Sun's galactocentric distance
Z0_PC = 20.0     # Sun's height above the plane

GALACTOCENTRIC_FRAME = Galactocentric(galcen_distance=R0_KPC * u.kpc, z_sun=Z0_PC * u.pc)


def to_galactocentric(ra_deg, dec_deg, dist_pc) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized: array-like inputs of equal length -> (x, y, z) kpc arrays."""
    coord = SkyCoord(ra=np.asarray(ra_deg, dtype=float) * u.deg,
                     dec=np.asarray(dec_deg, dtype=float) * u.deg,
                     distance=np.asarray(dist_pc, dtype=float) * u.pc,
                     frame="icrs")
    g = coord.transform_to(GALACTOCENTRIC_FRAME)
    return (g.x.to_value(u.kpc), g.y.to_value(u.kpc), g.z.to_value(u.kpc))
