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

5. **Fixed vs. free `approximation` encoding per item?** Decided for the
   first batch: the **gold encoding is fixed per item** and recorded in
   `approximation.encoding`, and encodings are deliberately **varied across
   items**. The four approximation items use `asymptotic`/`IsBigO`
   (`SM_01_Q43_001`), `error_bound` (`SM_02_Q11_001`), `model_substitution`
   (`SM_02_002_001`) and `asymptotic`/`Tendsto` (`SM_03_009_001`). Whether an
   *autoform* submission may pick a different encoding and still count as
   `equivalent` is still open, since L3 isn't built. No `Core/Approx.lean` was
   needed: Mathlib's `Asymptotics.IsBigO` and `Filter.Tendsto` sufficed, and
   the error-bound item states its bound directly.

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

## First item batch (12 items, statement-first)

Grew the benchmark from the one seed item to 12, before building more
pipeline, to get real model outputs to look at early. Maintainer's choices:

- **Mix:** 4 each of `proof_kind` `exact`, `approximation`,
  `hidden_assumption` (the seed counts as one `exact`). `mixed` not yet used.
- **Statements first:** each new item has a compiling gold statement (with
  `sorry`), `meta.yaml`, `nl.md` and `notes.md`, but **no reference proof**
  yet. Consequences: `difficulty.decl_count` is an estimate (flagged in each
  `notes.md`), and a false or unprovable gold statement would not have been
  caught by a proof. Every statement was sanity-checked numerically where
  applicable while drafting (see each `notes.md`), which reduces that risk
  without removing it.
- **Chapters 1–3 only**, to keep `Core` small. New `Core` modules:
  `Spin`, `Ising`, `CurieWeiss`, `LatticeGas`, `Thermo`.
- **Exercises have no `nl.proof`.** The source gives no proof for its
  exercises (or for eqn. (2.11)), so per `plan.md` §4 `nl.proof` is omitted
  there, and those 6 items (`E01`, `E02`, `E03`, `E05`, `E06`, `Q11`) run
  only in the `no_nl_proof` conditions.
- **Partial items:** where a source result has several independent parts or
  boundary conditions, only one is formalized as `_001`, noted in its
  `notes.md`: Lemma 3.5 (free boundary condition only), Theorem 2.2 (part 1
  only), Theorem 3.9 (periodic volumes only).
