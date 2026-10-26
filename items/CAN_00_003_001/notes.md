# Notes: CAN_00_003_001

Canary (`role: canary`): any working model should prove this. It is reported
separately in `summary.md` and excluded from every benchmark aggregate. If a
capable model fails it, suspect the pipeline (prompt, extraction, grading,
Core-in-context) before the model.

## Reference proof

`tests/fixtures/reference_proofs/CAN_00_003_001.lean` (public: canaries are not
benchmark items). Also passes on the `lean-v4.9` pin. Graded `pass` by
the real grader (axioms: propext, Classical.choice, Quot.sound), 2026-10-08.
