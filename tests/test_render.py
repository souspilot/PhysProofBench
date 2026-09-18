from physproofbench.render import gold_statement_prefix, render_proof_prompt

GOLD = "theorem add_comm' (a b : Nat) : a + b = b + a := by\n  sorry\n"


def test_gold_statement_prefix_strips_sorry():
    prefix = gold_statement_prefix(GOLD)
    assert prefix == "theorem add_comm' (a b : Nat) : a + b = b + a := by"
    assert "sorry" not in prefix


def test_gold_statement_prefix_missing_marker_raises():
    import pytest

    with pytest.raises(ValueError):
        gold_statement_prefix("theorem foo : True")


def test_render_a1_contains_statement_and_no_nl_paragraph():
    prompt = render_proof_prompt(
        gold_statement_lean="theorem foo : True := by", condition="no_nl_proof"
    )
    assert "theorem foo : True := by" in prompt
    assert "textbook's own proof" not in prompt
    assert "```lean fenced code block" in prompt


def test_render_a2_inserts_nl_proof_before_statement():
    prompt = render_proof_prompt(
        gold_statement_lean="theorem foo : True := by",
        condition="with_nl_proof",
        nl_proof="Trivially true by definition.",
    )
    assert "Trivially true by definition." in prompt
    assert prompt.index("Trivially true") < prompt.index("theorem foo : True := by")


def test_render_a2_without_nl_proof_raises():
    import pytest

    with pytest.raises(ValueError):
        render_proof_prompt(gold_statement_lean="theorem foo : True := by", condition="with_nl_proof")
