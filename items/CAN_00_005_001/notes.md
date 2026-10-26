# Notes: CAN_00_005_001

Plain-Mathlib canary (`role: canary`): no custom definitions, the kind of
goal specialist provers are trained on. Any working model on either Mathlib
pin should prove it, so a failure here means a prompt/format or pipeline
problem, not a gap in physics knowledge.

## Reference proof

`tests/fixtures/reference_proofs/CAN_00_005_001.lean` (public: canaries are not benchmark
items). Graded `pass` on both pins (`lean`, `lean-v4.9`), 2026-10-12.
