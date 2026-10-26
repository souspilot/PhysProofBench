# PI_E_001: Light curve of a tidal disruption event

*Paraphrased from USAPhO 2025, A2 g (official solution by the AAPT committee).*

## statement

A star torn apart by a supermassive black hole of mass `M` leaves bound
debris whose specific orbital energies are spread uniformly between
`ε_min < 0` and `0`. Each piece falls back after one orbital period and is
accreted, and the luminosity is proportional to the rate at which mass
returns. Show that after the first return the luminosity falls as a power
law `t^{-n}`, and find `n`.

## proof

**[Physical decision]** Fall-back time is the Kepler period, and Kepler's
third law ties it to energy: `a = -GM/(2ε)`, `T = 2π√(a³/GM)`, so
`ε ∝ -T^{-2/3}`. The mass returned by time `t` is `μ·(ε(t) - ε_min)`,
where `ε(t)` is the energy whose period is `t`. Differentiating gives
`dM/dt = μ dε/dt ∝ t^{-5/3}`, so `n = 5/3`.
