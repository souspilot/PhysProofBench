# PI_B_001: When does a two-isobar, two-isotherm engine reach Carnot efficiency?

*Paraphrased from USAPhO 2023, A3 a (official solution by the AAPT committee).*

## statement

One mole of monatomic ideal gas runs a reversible cycle between temperatures
`T₀` and `(1+β)T₀`:
1. heat at constant pressure `P₀` to `(1+β)T₀`;
2. expand isothermally until the pressure is `P₀/α`;
3. cool at constant pressure back to `T₀`;
4. compress isothermally back to `P₀`.

In what regime of `(α, β)` does the efficiency approach the Carnot
efficiency `1 - 1/(1+β)` between the same extreme temperatures?

## proof

Heat in: `Q₁ = (5/2)βP₀V₀` (isobaric) and `Q₂ = (1+β)P₀V₀ ln α`
(isothermal at the top temperature). Net work `W = βP₀V₀ ln α`. So

`η / η_Carnot = 1 / (1 + (5/2)·β/((1+β) ln α))`.

**[Physical decision]** Carnot efficiency is recovered when the heat taken in
below the top temperature is negligible, `Q₁ ≪ Q₂`, i.e.
`β/((1+β) ln α) → 0`. This condition is necessary and sufficient.

*Note on the source.* The official solution also asks for `|Q₃| ≪ |Q₄|`
and concludes the stricter `β ≪ ln α`. That condition is sufficient but not
necessary. For example, `β = n²`, `ln α = n` approaches Carnot while
`β/ln α → ∞` (see review).
