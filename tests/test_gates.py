from physproofbench.lean.gates import check_gates

GOLD = "theorem foo (a b : Nat) : a + b = b + a := by"


def test_clean_submission_passes():
    result = check_gates(
        "theorem foo (a b : Nat) : a + b = b + a := by exact Nat.add_comm a b",
        mode="proof",
        gold_text=GOLD,
    )
    assert result.passed
    assert result.failures == []


def test_sorry_is_rejected():
    result = check_gates("theorem foo : True := by sorry", mode="proof")
    assert not result.passed
    assert "gate: sorry_present" in result.failures


def test_axiom_declaration_is_rejected():
    result = check_gates("axiom foo : True", mode="proof")
    assert not result.passed
    assert "gate: axiom_declared" in result.failures


def test_native_decide_is_rejected():
    result = check_gates("theorem foo : True := by native_decide", mode="proof")
    assert not result.passed
    assert "gate: forbidden_tactic:native_decide" in result.failures


def test_statement_edit_is_rejected():
    result = check_gates(
        "theorem foo (a b : Nat) : a + b = a + b := by rfl",
        mode="proof",
        gold_text=GOLD,
    )
    assert not result.passed
    assert "gate: statement_edited" in result.failures


def test_identifier_substring_is_not_falsely_flagged():
    # "stop" must not fire on "stopwatch", "admit" must not fire on
    # "readmit", "sorry" must not fire on "sorryAx" appearing in a comment.
    result = check_gates(
        "-- computing stopwatch_readmit_sorryAx_value\n"
        "theorem foo : True := by trivial",
        mode="proof",
    )
    assert result.passed, result.failures


def test_autoform_mode_skips_statement_edit_gate():
    result = check_gates(
        "theorem bar (n : Nat) : n = n := by rfl", mode="autoform", gold_text=GOLD
    )
    assert result.passed
