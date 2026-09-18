# Decisions

Answers to `plan.md` §12's open questions, and other project-shaping calls,
recorded as they're made. Each entry says who decided and when reasonable to
track (this file predates most timestamps, so only the substantive record
matters).

1. **Census book and edition.** Friedli & Velenik, *Statistical Mechanics: A
   Mathematical Introduction*, "Revised version, August 22 2017" draft. See
   `docs/SOURCE.md#sm`. This overrides `plan.md`'s continuum-mechanics
   placeholder — the actual book present in the repo (`book/main.pdf`) is the
   stat-mech text, and the maintainer confirmed it as the target rather than
   the plan's example.

2. **Tensors: `Matrix` vs `LinearMap`.** Not yet relevant — `SM` is a finite
   probability-space / statistical mechanics text, not a continuum-mechanics
   one, so `plan.md` §5.2's tensor question doesn't apply to the seed item.
   Revisit if a later chapter needs tensor machinery (unlikely for this
   book; magnetism chapters use scalar/vector fields on `ℤᵈ`, not tensors).

3. **Units/dimensions by default?** Open. `SM`'s early chapters are
   dimensionless (probabilities, entropies, coupling constants as bare
   reals), so the seed item doesn't need `Core/Units.lean`. Decide once a
   chapter with genuine physical dimensions (temperature, energy density) is
   ingested.

4. **Prover-assisted bridging (L3 step 3) in the headline config?** Open —
   not exercised until M1's bridge-check implementation.

5. **Fixed vs. free `approximation` encoding per item?** Open — no
   `proof_kind: approximation` item exists yet.

6. **Public data licence.** Open — deferred to M4 per `plan.md`.

## Project naming

Working name is **PhysProofBench** (matching this directory), not `plan.md`'s
placeholder `PhysForm`. Applies consistently to: the Python package
(`src/physproofbench/`), the CLI entry point (`physproofbench`), and the Lean
library (`lean/PhysProofBench/`). Every `PhysForm` reference in `plan.md`
should be read as `PhysProofBench` going forward; `plan.md` itself is left
as-is (it's the original brief, not living documentation).

## Repo split

Two git repos, per `plan.md` §3:

- **Public:** this directory (`PhysProofBench/`), git-initialized directly.
  Contains statements (`sorry`-terminated), the pipeline, docs, and tests.
- **Private:** `../physproofbench-solutions` (sibling directory, also
  git-initialized). Contains reference proofs. Stands in for a private GitHub
  repo — push it there and wire it up as a git submodule at
  `lean/PhysProofBenchSolutions/` when a remote exists. Never merge its
  contents into the public tree.

## Seed item

`plan.md` §9's seed item (characterization of rigid motions) is from a
continuum-mechanics text and doesn't exist in `SM`. Replaced with **Lemma
1.9** (p. 21): the uniform distribution uniquely maximizes Shannon entropy on
a finite probability space. Picked because it's the first non-trivial
numbered result in the book, entirely self-contained (no physics modeling
ambiguity — it's a clean analysis fact used to motivate the microcanonical
ensemble), and its proof (Jensen's inequality on the concave map
`x ↦ -x log x`) is realistic to formalize `sorry`-free against Mathlib.
See `items/SM_01_009_001/` and `docs/SOURCE.md`.
