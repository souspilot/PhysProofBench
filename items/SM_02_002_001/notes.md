# Notes: SM_02_002_001

## Formalization decisions

- **Only part 1 (`β ≤ β_c`) is this item (`_001`).** Part 2 (`β > β_c`:
  concentration near `±m*`) needs the spontaneous magnetization `m*(β)` as an
  object (the positive root of the mean-field equation). It is a natural
  follow-up `_002`.
- **Approximation encoding: `model_substitution`, flavor `uncontrolled`.** The
  Curie–Weiss model is the source's mean-field approximation of the Ising
  model (§2.1). The gold statement is an exact theorem about the substituted
  model; nothing in it bounds the error relative to Ising.
- `0 ≤ β` is included because `β` is an inverse temperature (the source works
  on `β ≥ 0` throughout). `1 ≤ d` excludes the degenerate `d = 0`, where
  `β_c` would be `1/0`.
- "For large enough `N`" is `∀ᶠ N in atTop`. The `N = 0` junk case
  (`magnetization` divides by `N`) is therefore excluded automatically.
- `cwProb` sums the Gibbs weights over a `Set` via `Set.indicator`. The event
  `{ω | |m_N(ω)| < ε}` is not decidable, so classical indicators avoid
  threading decidability instances through the statement.

## Hidden assumptions

None beyond the approximation encoding above.

## Witness

Not needed (no added hypotheses).

## Difficulty

`difficulty.decl_count` (45) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.
