# Notes: CAN_00_004_001

Canary (`role: canary`): any working model should prove this. It is reported
separately in `summary.md` and excluded from every benchmark aggregate. If a
capable model fails it, suspect the pipeline (prompt, extraction, grading,
Core-in-context) before the model.

## Reference proof

`lean/PhysProofBenchSolutions/CAN_00_004_001.lean` (private repo). Graded `pass` by
the real grader (axioms: propext, Classical.choice, Quot.sound), 2026-10-08.
