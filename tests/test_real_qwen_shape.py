"""Regression for a real Qwen3 (--no-thinking) completion: an unterminated
```lean fence, correct imports/statement, but the item's tag comments and
docstring dropped. Before the fix this was gate_fail/statement_edited no
matter what the proof was."""

from pathlib import Path

from physproofbench.extract import extract_lean
from physproofbench.lean.gates import check_gates
from physproofbench.render import gold_statement_prefix

REPO = Path(__file__).parent.parent


def test_qwen_shaped_completion_reaches_the_compiler():
    gold = (REPO / "lean/PhysProofBench/Items/SM_01_009_001.lean").read_text()
    completion = (
        "```lean\n"
        "import PhysProofBench.Core.Probability\n\n"
        "open PhysProofBench\n\n"
        "theorem shannonEntropy_le_log_card {Ω : Type*} [Fintype Ω] [Nonempty Ω]\n"
        "    (μ : Ω → ℝ) (hμ : IsProbDist μ) :\n"
        "    shannonEntropy μ ≤ Real.log (Fintype.card Ω) ∧\n"
        "      (shannonEntropy μ = Real.log (Fintype.card Ω) ↔ ∀ ω, μ ω = uniformDist ω) := by\n"
        "  have h : 0 < Fintype.card Ω := Fintype.card_pos\n"
        "  -- rest of proof\n"
        "  exact test_placeholder\n"
    )
    extraction = extract_lean(completion)
    assert extraction.unterminated_fence
    assert not extraction.lean.startswith("```")
    result = check_gates(extraction.lean, mode="proof", gold_text=gold)
    assert result.passed, result.failures
    assert gold_statement_prefix(gold).endswith(":= by")
