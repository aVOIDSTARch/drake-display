"""
Phase 0 calibration (DECISIONS.md ADR-013).

Solves for the galactic baseline and magnitudes that hit the calibration
targets, then the supernova magnitude that drives H down to the kill
target at collapse. Prints the values; it does not edit the configs --
copy them into configs/phase0-galactic.toml and src/veil/registry.py.

Run from the repo root:  .venv/bin/python scripts/calibrate_phase0.py
"""

import numpy as np

from fields.kernels import LogisticStepKernel, MetallicityBandKernel

# ---- targets (ADR-013) ----
TARGETS = {0.0: 0.20, 8.2: 0.75, 20.0: 0.40}   # galactocentric R (kpc) -> H, at z = 0
SN_TARGET_H = 0.10                              # inside the kill radius, at collapse, near the Sun

# ---- fixed by factors.md: profiles, backings, and the density : core magnitude ratio ----
BACKING = {"metal": 0.9, "density": 0.6, "agn": 0.5, "sn": 0.9}
DENSITY_TO_AGN = (0.7, 0.8)
H_R_KPC = 2.5
BAND = MetallicityBandKernel()
INNER = LogisticStepKernel(radius=2.5, width=0.3)


def logit(p):
    return np.log(p / (1 - p))


def density(R):
    return np.exp(-np.asarray(R) / H_R_KPC)


def main() -> None:
    R = np.array(list(TARGETS))
    # unknowns: baseline B0, metallicity magnitude, and a shared scale k
    # for the hazards, with M_density = 0.7 k and M_agn = 0.8 k
    hazard_profile = (BACKING["density"] * DENSITY_TO_AGN[0] * density(R)
                      + BACKING["agn"] * DENSITY_TO_AGN[1] * INNER(R))
    A = np.column_stack([np.ones_like(R), BACKING["metal"] * BAND(R), -hazard_profile])
    b0, m_metal, k = np.linalg.solve(A, logit(np.array(list(TARGETS.values()))))
    m_density, m_agn = DENSITY_TO_AGN[0] * k, DENSITY_TO_AGN[1] * k

    def galactic_logit(R):
        return (b0 + BACKING["metal"] * m_metal * BAND(R)
                - BACKING["density"] * m_density * density(R)
                - BACKING["agn"] * m_agn * INNER(R))

    m_sn = (galactic_logit(8.2) - logit(SN_TARGET_H)) / BACKING["sn"]

    print(f"baseline        = {b0:.3f}")
    print(f"FAC-METAL   M   = {m_metal:.3f}")
    print(f"FAC-DENSITY M   = {m_density:.3f}")
    print(f"FAC-AGN     M   = {m_agn:.3f}")
    print(f"FAC-SN      M   = {m_sn:.3f}")
    Rs = np.array([0, 1, 2, 3, 4, 5, 6, 8.2, 10, 12, 15, 20.0])
    H = 1 / (1 + np.exp(-galactic_logit(Rs)))
    print("H(R):", "  ".join(f"{r:g}:{h:.2f}" for r, h in zip(Rs, H)))


if __name__ == "__main__":
    main()
