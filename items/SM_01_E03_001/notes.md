# Notes: SM_01_E03_001

## Formalization decisions

- `freeEnergyHat` (`Core/Thermo.lean`) is an `iInf` over `U : Set.Ioi 0`.
  Lean's conditionally complete `iInf` returns a junk value when the range is
  unbounded below, so the finiteness hypothesis is load-bearing, not
  decorative.
- Convexity is joint in `(V, N)` on `V, N > 0`. The source says "convex in `V`
  and `N`", which could be read as separately convex. Joint convexity is the
  stronger reading, true, and what the physics (thermodynamic stability)
  uses.
- Concavity in `β` is on `β > 0` (positive temperature, as assumed in the
  source's (1.4)).
- `S` concave is a hypothesis (Exercise 1.2, item `SM_01_E02_001`).
- **No `## proof` in `nl.md`.** The source leaves this as an exercise and
  gives no proof, so per `plan.md` §4 `nl.proof` is omitted. Only the
  `no_nl_proof` conditions (A1, B1) apply to this item.

## Hidden assumptions

See `meta.yaml` `hidden_assumptions`: `finite_infimum` (domain), `energy_positive` (domain).

## Witness

`S(U, V, N) = N log(U/N) + N log(V/N)` is jointly concave on `PosOrthant` (each term is the perspective of the concave `log`), and `U ↦ βU - N log(U/N)` is bounded below on `U > 0` for `β > 0` (minimum at `U = N/β`). So the hypotheses are jointly satisfiable. This is the ideal-gas entropy with `c = 1`.

## Difficulty

`difficulty.decl_count` (8) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.
