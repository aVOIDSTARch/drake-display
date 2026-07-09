# Research: A Stellar Compendium — Types of Stars, Their Remnants, Temporal Populations, and Their Radiography

> Scope note: This is a reference atlas. It classifies stars and remnants (observed and theoretical), maps the *temporally distinct* types that can only exist at particular epochs of cosmic history (past and future), and — the part most compendia neglect — details the **radiography**: the spectral energy distribution (what fraction of the output is radio / infrared / visible / ultraviolet / X-ray / gamma) of each object and, crucially, how that mix *shifts as the object ages*, with the physics that produces it. Cross-references: the early-universe and dark-sector material connects to `research-cosmology-mysteries.md`; the megastructure/black-hole engineering notes connect to `research-kardashev-scale.md` and `research-centripetal-centrifugal-forces.md`.

## 1. Question or Topic of Research

What is the full taxonomy of stellar objects — main-sequence stars, evolved stars, compact remnants, exotic theoretical bodies, and the epoch-bound types that could only form at particular moments in cosmic history — and what is the detailed radiation output (the fractional spectral energy distribution) of each, both at a given moment and across its aging, together with the physical mechanisms responsible for that mix?

## 2. Current Established Science

### 2.1 — How stars are classified (the taxonomy you must speak fluently)

Two orthogonal axes, combined, locate almost any star. **Spectral class** (the Harvard system, ordered by decreasing surface temperature) runs **O B A F G K M**, subdivided 0–9 — the mnemonic-worthy sequence from blue-white ~40,000 K down to red ~2,500 K. Three extensions matter: **L, T, Y** for the sub-stellar brown dwarfs (cooler still, down to near room temperature for Y); **W** for Wolf–Rayet stars (hot, stripped, emission-line); and **C** and **S** for carbon and zirconium-oxide giants. **Luminosity class** (the Morgan–Keenan system) captures size/evolutionary state: **Ia⁺/0** hypergiants, **Ia/Ib** supergiants, **II** bright giants, **III** giants, **IV** subgiants, **V** main-sequence dwarfs (the Sun is G2V), **VI/sd** subdwarfs, **VII/D** white dwarfs. Plotted, temperature against luminosity yields the **Hertzsprung–Russell diagram**, whose diagonal main sequence, giant branch, and white-dwarf clump are the map on which all of stellar evolution is drawn. A star's *position* on the HR diagram is not its identity but its current *life stage*.

### 2.2 — The radiation physics primer (read this before the SED tables)

Four ideas govern every spectrum below.

- **Thermal (blackbody) continuum.** A star's photosphere radiates approximately as a blackbody. **Wien's displacement law** fixes the peak: λ_peak ≈ (2.9 × 10⁶ nm·K) / T. So a 5,772 K Sun peaks near 500 nm (green-yellow, in the visible); a 40,000 K O star peaks near 72 nm (far ultraviolet); a 3,000 K M dwarf peaks near 1,000 nm (near-infrared); a million-kelvin neutron-star surface peaks near 3 nm (soft X-ray). **Stefan–Boltzmann** (L = 4πR²σT⁴) sets the total power. Temperature alone therefore dictates *color*; temperature and radius together dictate *luminosity*.
- **The emergent spectrum is NOT the core spectrum.** Fusion in the core produces gamma rays and neutrinos. The photons thermalize over ~10⁴–10⁵ years of random-walk diffusion and escape at the far cooler photospheric temperature; only the **neutrinos** stream out directly (the Sun sheds ~2% of its luminosity as neutrinos — a genuine, if invisible, part of its "radiography"). Never conflate the reactor with the radiator.
- **Spectral lines ride atop the continuum.** Atomic transitions in the cooler outer layers carve **absorption lines** (the basis of spectral classification); hot, thin gas (chromospheres, nebulae, accretion regions) produces **emission lines**. Line strength encodes temperature, composition (metallicity), density, and velocity.
- **Non-thermal emission — the exotic add-ons.** Beyond blackbody, several mechanisms produce power-law (not temperature-set) spectra: **synchrotron** (relativistic electrons spiraling in magnetic fields → radio through X-ray; the signature of pulsars, jets, supernova remnants); **inverse-Compton / Comptonization** (low-energy photons upscattered by hot electrons → the hard X-ray power law of accretion coronae); **bremsstrahlung** (free electrons decelerating in ionized gas → thermal X-rays from shocked plasma); and **curvature/coherent** radiation (the pulsar radio beam). When you see radio or hard X-rays from a star, you are almost always seeing magnetism or accretion, not heat.

### 2.3 — The main-sequence zoo, with radiography

Main-sequence stars fuse hydrogen in their cores; their emergent spectrum is dominated by the photospheric blackbody, modulated by absorption lines and, for cool stars, a magnetically heated X-ray corona. Approximate fractional energy budgets (bolometric; band definitions vary, treat as order-of-magnitude):

| Class | ~T_surf (K) | SED peak | UV | Visible | IR | Non-thermal notes |
| --- | --- | --- | --- | --- | --- | --- |
| O | 30,000–50,000 | far-UV | ~90%+ (much ionizing) | few % | negligible | X-rays from wind shocks; drives HII regions |
| B | 10,000–30,000 | UV | majority | modest | small | wind X-rays |
| A | 7,500–10,000 | near-UV/violet | large | large | small | weak coronae |
| F | 6,000–7,500 | blue-visible | ~15% | ~50% | ~35% | onset of convective coronae |
| G (Sun) | 5,200–6,000 | visible (~500 nm) | ~8% | ~44% | ~48% | ~10⁻⁶ of L in coronal X-rays; +2% as neutrinos |
| K | 3,700–5,200 | red/near-IR | small | ~30–40% | majority | active coronae, flares |
| M | 2,400–3,700 | near-IR (~1 µm) | tiny | few % | ~majority | strong flares; X-ray/UV spikes dwarf the quiescent output |
| L/T/Y (brown dwarfs) | 200–2,400 | IR / mid-IR | ~none | ~none | overwhelming | methane/water bands; Y peaks in mid-IR |

Two points a careful reader should hold. First, the hottest stars pour most of their energy where the eye can't see (the UV), which is why an O star's *visible* brightness understates its true, ionizing ferocity. Second, for cool active stars (M dwarfs especially) the *quiescent* spectrum is nearly all infrared, but **flares** — magnetic-reconnection events — briefly dump enormous UV and X-ray output, a fact with real consequences for the habitability of planets around red dwarfs (a possible worldbuilding hinge).

### 2.4 — Evolved and peculiar stars

When core hydrogen is exhausted, the star migrates off the main sequence and its radiography changes accordingly.

- **Red giants / red supergiants (K–M III/I):** cool (~3,000–4,000 K) but vast; luminosity soars while the SED shifts strongly to the **red and infrared**. Betelgeuse-class supergiants radiate predominantly in the IR.
- **Asymptotic-giant-branch (AGB) stars:** shed dusty envelopes; the dust reprocesses starlight into a strong **infrared excess**, and these are the galaxy's chief factories of carbon and s-process elements. **Carbon (C) and S stars** are AGB chemistry variants.
- **Cepheids, RR Lyrae, Miras:** pulsating variables whose regular light curves make them cosmic distance indicators (Cepheids underpin the Hubble-tension distance ladder in the cosmology doc).
- **Wolf–Rayet (W) stars:** massive stars stripped of their hydrogen envelopes, exposing hot (25,000–200,000 K) helium/nitrogen or carbon cores; **UV-dominated**, with broad *emission* lines from dense, fast winds. Note for §2.5: Wolf–Rayet stars produce the hard **He II 1640 Å** signature that also mimics primordial stars — a genuine observational headache.
- **Protostars / young stellar objects (T Tauri, Herbig Ae/Be):** still embedded in natal dust; their light emerges reprocessed, so they are **infrared- and submillimeter-dominated**, often with disk signatures.

### 2.5 — Temporally distinct populations (types bound to specific cosmic epochs)

This is the axis you specifically flagged, and it cuts in *both* temporal directions.

**Stellar populations by metallicity (a chronological sequence):**

- **Population I** — metal-rich, young, found in galactic disks and spiral arms; the Sun is one. Only possible *after* generations of prior stars enriched the gas.
- **Population II** — metal-poor, old; inhabiting halos, globular clusters, and bulges. Low-mass Pop II survivors are still observable ("stellar archaeology") and let us read early-universe conditions.
- **Population III** — the hypothesized **first stars**: forged from pristine hydrogen and helium with essentially *zero* metals. Because metal-line cooling is what lets gas fragment into small clumps, its absence is thought to have produced extremely **massive** stars (tens to hundreds, perhaps >1,000 M☉), blisteringly hot (>10⁵ K), overwhelmingly **UV and ionizing** — the engines of cosmic reionization and the first nucleosynthesis. They are epoch-bound in the strict sense: *once the universe was polluted with metals, this type could never form again.* The most massive would die within a few million years, some as **pair-instability supernovae** that leave **no remnant at all** (the star is entirely unbound), others by **direct collapse** to black holes. **Observational status (2026):** despite being a flagship JWST goal, there is still **no robust confirmed detection** — only a growing set of tentative candidates identified by strong He II 1640 emission with weak or absent metal lines. <cite index="93-1">In late 2025 the gravitationally lensed system LAP1-B, seen ~800 million years after the Big Bang, was reported as a candidate</cite>, and <cite index="100-1">JWST has flagged several Pop III candidates via colors and emission lines (Maiolino 2024, Wang 2024, Fujimoto 2025)</cite>. **Bias flag:** the diagnostic is treacherous — <cite index="99-1">Wolf–Rayet stars, X-ray binaries, and black holes can all mimic the hard ionizing spectrum expected of metal-free stars</cite>, so treat any "first stars found" headline as provisional.

**Theoretical first-generation alternatives (also epoch-bound):**

- **Dark stars** — a genuinely different first-star hypothesis: objects made almost entirely of hydrogen and helium but powered not by fusion but by **dark-matter self-annihilation** in the dense dark-matter cusps of early halos. Their radiography is *diagnostically distinct* from Pop III: because heat is deposited throughout the volume rather than in a fusing core, they stay **cool** (~10,000 K surface) yet can grow enormous and luminous. <cite index="104-1">Models describe them as puffy (~10 AU), able to accrete up to ~10⁶ solar masses and exceed a billion solar luminosities, making them visible to JWST</cite>. <cite index="106-1">Freese, Ilie and collaborators have reported spectroscopic supermassive-dark-star candidates in JWST data, including objects at redshift ~14 (only ~300 million years after the Big Bang), citing a He II 1640 Å absorption feature as a "smoking gun."</cite> **Bias flag:** these remain contested candidates, not confirmations, and the same objects are alternatively interpreted as ordinary early galaxies. Their appeal is that <cite index="101-1">they could simultaneously explain JWST's over-abundance of bright compact early objects and seed the supermassive black holes powering the earliest quasars</cite>.
- **Supermassive / quasi-stars** — hypothesized 10⁴–10⁵ M☉ radiation-pressure-supported stars (or bloated envelopes around a nascent accreting black hole) that collapse to form **massive black-hole seeds** via **direct collapse**, a leading explanation for early supermassive black holes. Epoch-bound to the pristine, rapidly-accreting early universe.

### 2.6 — Compact remnants (the standard three), with radiography and aging

What a star leaves behind is set almost entirely by its initial mass.

- **White dwarfs** (progenitors up to ~8 M☉): Earth-sized balls of electron-**degenerate** matter (carbon-oxygen, or oxygen-neon for the heaviest), supported by degeneracy pressure up to the **Chandrasekhar limit (~1.4 M☉)**; exceed it (e.g., by accretion) and you get a **Type Ia supernova**. **Radiography and aging:** a newborn white dwarf is ferociously hot (100,000–200,000 K), so its blackbody peaks in the **extreme UV / soft X-ray**; over billions of years it simply *cools at fixed radius*, its peak marching down through the UV, to blue-white, to yellow, to red — a nearly pure cooling-blackbody track (spectral types DA, DB, etc., set by trace surface composition). Given enough time (~10¹⁵ years, far exceeding the current age of the universe) it would fade to a cold **black dwarf** (see §2.8) — which is why **none exist yet**.
- **Neutron stars** (progenitors ~8–20+ M☉): city-sized, ~1.4–2.2 M☉ of neutron-degenerate matter near nuclear density, capped by the **Tolman–Oppenheimer–Volkoff limit** (~2.2–2.3 M☉). Their radiography is a rich, dual-origin story:
  - **Thermal surface emission:** a young neutron-star surface at ~10⁶ K peaks (Wien) in the **soft X-ray**; it cools over ~10⁶ years.
  - **Non-thermal magnetospheric emission:** as **pulsars**, they beam **coherent radio** (curvature radiation) and, for energetic ones, pulsed **optical-to-gamma** synchrotron/curvature emission, all modulated at the spin period.
  - **Magnetars:** the extreme magnetic subclass (fields ~10¹⁴–10¹⁵ G), powered by **magnetic-field decay** rather than spin or heat, emitting persistent and bursting **soft gamma / hard X-ray** — and now linked to some fast radio bursts.
  - **Aging trajectory:** high-energy, radio-loud, and rapidly spinning when young; spin-down and cooling gradually silence the radio beam and dim the thermal X-rays over millions of years, ending as a cold, dark, effectively undetectable remnant.
- **Black holes** (progenitors above ~20–25 M☉, or via direct collapse): the remnant itself emits essentially nothing (Hawking radiation is negligible for any astrophysical mass). **All black-hole radiography is the radiography of accretion:**
  - **Accretion disk (thermal):** gravitational potential energy heats infalling gas. For a **stellar-mass** black hole the inner disk reaches ~10⁷ K and peaks in **X-rays** (X-ray binaries); for a **supermassive** black hole the larger, cooler disk peaks in the **UV/optical** (the "big blue bump" of quasars).
  - **Corona (non-thermal):** a hot electron cloud Comptonizes disk photons into a **hard X-ray power law**.
  - **Jets (non-thermal):** relativistic outflows radiate **synchrotron** from radio through X-ray, the defining signature of radio-loud AGN and microquasars.
  - **Reprocessing:** a surrounding dusty torus re-emits absorbed light in the **infrared**.
  So the same object reads as an "X-ray source," "UV quasar," "radio galaxy," or "infrared-bright AGN" depending on which component and viewing angle dominate — the accretion state, not the hole, sets the spectrum.
- **Supernova remnants** (the debris, not the core): expanding shocked gas radiating **synchrotron in the radio**, **thermal bremsstrahlung/line emission in X-rays**, and **optical line emission** — the multiwavelength shell (e.g., the Crab, Cassiopeia A) that fades over ~10⁴–10⁵ years.

### 2.7 — Exotic and hypothetical remnants

Beyond the standard three lie objects that are theoretically motivated but unconfirmed or contested:

- **Quark / strange stars:** if matter above nuclear density deconfines into free quarks, a neutron star's core (or the whole object) could become **quark matter**; **strange quark matter** (up-down-strange) might even be the true ground state of dense matter. Such a "strange star" would be slightly smaller and denser than a neutron star, and certain unusually compact or massive compact objects are occasionally proposed as candidates — but there is **no confirmed detection**, and the equation of state at these densities is a genuine open problem.
- **Thorne–Żytkow objects:** a neutron star swallowed into the envelope of a red supergiant, producing a bizarre hybrid with anomalous chemistry; one or two candidates exist, unconfirmed.
- **Boson stars, gravastars, preon stars:** purely theoretical compact objects invoked as black-hole mimickers or alternative dense states; none observed, all serving mainly as foils in strong-gravity and dark-matter theory.

### 2.8 — Future-epoch stars and remnants (the other end of the temporal axis)

Adams & Laughlin's framework of cosmic "ages" — **Stelliferous** (now), **Degenerate**, **Black Hole**, and **Dark** eras — organizes objects that *cannot exist yet* because the universe is too young:

- **Red dwarfs as the long twilight:** the lowest-mass M dwarfs fuse hydrogen so frugally they will shine for **trillions of years**, long outliving every larger star — the last ordinary starlight in the cosmos.
- **Blue dwarfs (theoretical):** a very-low-mass red dwarf, at the end of its life, is predicted to *contract and heat* — growing **bluer** — before finally becoming a white dwarf, rather than swelling into a red giant. Because red-dwarf lifetimes exceed the current age of the universe, **no blue dwarf has ever existed**; they are a strictly future phenomenon.
- **Black dwarfs (theoretical):** the cold end-state of a white dwarf after it radiates away its heat over ~10¹⁵ years. Radiography: a faint, cold blackbody peaking in the **far-infrared/microwave**, effectively invisible. **None exist** — the universe is ~10⁵ times too young.
- **Iron stars and the deep future (extreme speculation):** on timescales like 10¹⁵⁰⁰ years, quantum tunneling could drive cold fusion/fission converting stellar remnants toward **iron-56**, and (absent proton decay) black dwarfs might ultimately collapse. These are limiting-case thought experiments at the frontier of what physics can even address.
- **"Frozen stars"** — a term with two meanings worth disambiguating: historically, an early external-observer description of **black holes** (time appearing frozen at the horizon); and in far-future cosmology, hypothetical very-low-mass stars formed from highly enriched gas with surfaces cold enough to be nearly frozen — deeply speculative.

## 3. Ongoing / Interesting Research Topics

- **The hunt for genuine Population III** (§2.5): separating true metal-free signatures from Wolf–Rayet / X-ray-binary / AGN contaminants, using combined spectral-hardness and metallicity diagnostics, lensing clusters, and even Pop III tidal-disruption events and supernovae as alternative detection channels.
- **Dark-star confirmation or refutation** (§2.5): whether the JWST candidates resolve as point sources (stars) versus extended sources (galaxies), and whether the He II 1640 absorption feature survives higher-resolution, lensed follow-up.
- **The dense-matter equation of state** (§2.7): neutron-star mass–radius measurements (from NICER, and from gravitational-wave tidal deformability in mergers) are steadily constraining whether quark/strange matter appears — a live intersection of astrophysics and nuclear physics.
- **The neutron-star / black-hole "mass gap"** (~2.5–5 M☉): merger detections are populating this once-empty range, reshaping remnant demographics.
- **Magnetars as fast-radio-burst engines:** an active, rapidly evolving link between an exotic remnant class and a cosmological transient population.
- **Direct-collapse black-hole seeds** (§2.5): whether supermassive/quasi-stars or dark stars explain the too-early supermassive black holes (ties directly to the cosmology document's early-structure problem).

## 4. Hard Constraints — Where Fidelity Matters

- **Color is set by surface temperature, not by fuel or age directly.** A star is red because it is *cool*, whether it's a cool dwarf or a vast cool supergiant — luminosity distinguishes them, not hue. Writing a "hot red star" or a "cold blue star" is a physics error a knowledgeable reader will catch instantly (blue = hot, red = cool, always).
- **The emergent spectrum is photospheric, not nuclear.** Don't have characters "see the fusion" — they see thermalized surface light. The core's gamma rays never escape as gamma rays; only neutrinos do. A neutrino observatory, not a telescope, watches the core.
- **Remnant type is dictated by mass.** Below ~8 M☉ → white dwarf; ~8–20+ → neutron star; above ~20–25 (or direct collapse) → black hole. Don't let a Sun-like star leave a black hole, or a massive star leave a white dwarf, without a very specific justification (mass transfer, mergers).
- **The mass limits are load-bearing.** Chandrasekhar (~1.4 M☉) for white dwarfs and the TOV limit (~2.2 M☉) for neutron stars are not decorative — crossing them triggers collapse or explosion. A 3 M☉ neutron star or a 2 M☉ white dwarf needs an explanation.
- **Black holes are dark; accretion is bright.** A quiescent, non-accreting black hole emits nothing detectable and is found only by its gravity (lensing, orbits). All the fireworks — X-rays, quasar UV, radio jets — come from *material around* it. Conflating the two is a common error.
- **Black dwarfs and blue dwarfs do not exist yet.** The universe is far too young. If your story features them, it is set in the deep future (or you owe the reader an explanation). This is a subtle, high-credibility detail precisely because it's rarely known.
- **Population III cannot exist in the present universe.** Metal-free stars are a first-generation phenomenon; a pristine-composition star in a modern, enriched galaxy is a contradiction unless you invent a pocket of primordial gas and justify it.
- **Neutron-star and pulsar emission is largely non-thermal and beamed.** The radio pulse is a lighthouse beam; you only see it if it sweeps you. A pulsar's "pulsing" is geometry, not intrinsic blinking.

## 5. Fertile Ground for Creative Extrapolation

- **Dark stars as a first-generation setting or mystery.** A dark-matter-powered star — cool-surfaced yet supermassive and luminous, powered by annihilation rather than fusion — is a *published, live* hypothesis (§2.5), not invention. A civilization studying (or arising near) such an object, or discovering that a "galaxy" is actually a single dark star, sits on real, current science.
- **Population III archaeology.** The narrative of hunting the universe's first, unrepeatable stars — visible only through lensing, dying in remnant-less pair-instability blasts, leaving only chemical fingerprints in later stars — is inherently dramatic and scientifically grounded. The *contaminant problem* (is it really a first star, or a Wolf–Rayet impostor?) is a ready-made detective structure.
- **Neutron-star and magnetar environments as extreme stages.** Magnetic fields of 10¹⁵ gauss, surfaces at millions of kelvin, matter at nuclear density, frame-dragging spacetime — the physics is so extreme it needs little embellishment. Magnetar flares as galaxy-scale hazards, or a civilization mining a neutron star's spin or field, are grounded high-concept.
- **Black-hole radiography as reconnaissance.** Because a black hole's entire observable signature is its accretion state, a story can hinge on *reading* that signature — inferring mass, spin, and feeding history from the X-ray/UV/radio mix — or on a black hole going quiet (accretion halting) and vanishing from view. The Kardashev document's black-hole-powered civilizations connect here.
- **The deep-future zoo.** Blue dwarfs, black dwarfs, iron stars, the fading of the last red dwarfs — a story set in the Degenerate or Black Hole era can populate its sky with objects that *cannot exist now*, giving a far-future setting a genuinely alien, physically-earned appearance. Adams & Laughlin's era framework is the scaffolding.
- **Quark/strange matter as an existential substance.** If strange quark matter is the true ground state of matter, a "strangelet" could in principle catalyze the conversion of ordinary matter it touches — a real (if almost certainly harmless in reality) theoretical doomsday concept with impeccable pedigree, ripe for disciplined fictional use.
- **Red-dwarf flares and habitability.** The mismatch between an M dwarf's placid infrared quiescence and its violent UV/X-ray flares is a concrete, physically grounded constraint on life around the galaxy's most common stars — a rich, non-arbitrary source of conflict for any planet-based story.
- **Supermassive-star / direct-collapse seeds.** The birth of a black-hole seed from a monstrous, short-lived supermassive star is a spectacular, epoch-specific event you can stage in the early universe with real theoretical backing.

## 6. Open Questions

- Do Population III stars match theoretical predictions (very massive, top-heavy mass function), and can we ever *robustly* confirm one against contaminants?
- Are the JWST dark-star candidates real dark stars, or ordinary early galaxies? (Resolvable, in principle, by lensed high-resolution follow-up.)
- What is the equation of state of matter above nuclear density — do quark/strange stars exist, and where is the true neutron-star maximum mass?
- What populates the ~2.5–5 M☉ compact-object mass gap, and how?
- Which channel — supermassive stars, dark stars, or something else — seeds the earliest supermassive black holes?
- Does anything prevent black-dwarf and eventual iron-star formation in the deep future (e.g., proton decay), and on what timescales?

## 7. Brainstorm Notes

*(Empty — append dated entries here as we develop ideas together.)*
