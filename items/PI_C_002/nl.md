# PI_C_002: Joule expansion of a weakly attracting gas

*Paraphrased from USAPhO 2020, B3 d-f (official solution by the AAPT committee).*

## statement

`N` atoms of a monatomic gas with weak pairwise attraction and negligible
volume occupy volume `V` at temperature `T`. Their mean-field energy is
`E = (3/2)NkT - aN²/V`. The gas expands freely into an equal evacuated
volume inside an insulated box. Find the final temperature, and the entropy
increase to first order in `ε = aN/(VkT)`.

## proof

**[Physical decision]** The ideal-gas model predicts no temperature change.
The leading effect of the attraction is the mean-field energy, with the 1/2
for pair counting already in `aN²/V`. Free expansion conserves `E`:
`(3/2)NkT' - aN²/(2V) = (3/2)NkT - aN²/V`, so `T' = T - aN/(3kV)`.
For the entropy, the first law with `P = NkT/V - aN²/V²` gives
`dS = (3/2)Nk dT/T + Nk dV/V`. Then
`ΔS = Nk ln 2 + (3/2)Nk ln(T'/T) ≈ Nk ln 2 - aN²/(2VT)`.
