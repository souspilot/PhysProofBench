from physproofbench.lean.gates import check_gates, restore_item_preamble

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


GOLD_WITH_COMMENTS = """import Foo

-- PHYSPROOFBENCH-ITEM: X
open Foo

/-- The docstring. -/
theorem t (a : Nat) : a = a := by
  sorry
"""


def test_dropped_comments_and_docstring_do_not_count_as_statement_edit():
    sub = "import Foo\nopen Foo\ntheorem t (a : Nat)\n    : a = a := by\n  rfl\n"
    assert check_gates(sub, mode="proof", gold_text=GOLD_WITH_COMMENTS).passed


def test_added_comments_do_not_count_as_statement_edit():
    sub = GOLD_WITH_COMMENTS.replace("sorry", "rfl").replace(
        "theorem t", "/- nested /- comment -/ still comment -/\ntheorem t"
    )
    assert check_gates(sub, mode="proof", gold_text=GOLD_WITH_COMMENTS).passed


def test_changed_conclusion_is_still_a_statement_edit():
    sub = GOLD_WITH_COMMENTS.replace("a = a :=", "True :=").replace("sorry", "trivial")
    r = check_gates(sub, mode="proof", gold_text=GOLD_WITH_COMMENTS)
    assert "gate: statement_edited" in r.failures


def test_shadowing_definition_before_theorem_is_still_a_statement_edit():
    sub = GOLD_WITH_COMMENTS.replace(
        "open Foo\n", "open Foo\ndef Bar := 1\n"
    ).replace("sorry", "rfl")
    r = check_gates(sub, mode="proof", gold_text=GOLD_WITH_COMMENTS)
    assert "gate: statement_edited" in r.failures


def test_added_mathlib_imports_are_not_a_statement_edit():
    for extra in ("import Mathlib\n", "import Mathlib.Analysis.Convex.Jensen\n"):
        sub = GOLD_WITH_COMMENTS.replace("import Foo\n", extra + "import Foo\n").replace("sorry", "rfl")
        assert check_gates(sub, mode="proof", gold_text=GOLD_WITH_COMMENTS).passed, extra


def test_added_non_mathlib_import_is_still_a_statement_edit():
    for extra in ("import Bar\n", "import MathlibExtras\n", "import Batteries\n"):
        sub = GOLD_WITH_COMMENTS.replace("import Foo\n", "import Foo\n" + extra).replace("sorry", "rfl")
        r = check_gates(sub, mode="proof", gold_text=GOLD_WITH_COMMENTS)
        assert "gate: statement_edited" in r.failures, extra


def test_mathlib_import_does_not_excuse_a_shadowing_definition():
    sub = GOLD_WITH_COMMENTS.replace("import Foo\n", "import Mathlib\nimport Foo\n").replace(
        "open Foo\n", "open Foo\ndef Bar := 1\n"
    ).replace("sorry", "rfl")
    r = check_gates(sub, mode="proof", gold_text=GOLD_WITH_COMMENTS)
    assert "gate: statement_edited" in r.failures


def test_marker_inside_a_comment_is_ignored():
    gold = "-- proof goes after := by\ntheorem t : True := by\n  sorry\n"
    sub = "theorem t : True := by\n  trivial\n"
    assert check_gates(sub, mode="proof", gold_text=gold).passed


def test_specialist_prover_header_is_not_a_statement_edit():
    gold = "import Mathlib.Data.Real.Basic\n\ntheorem t (x : ℝ) : x = x := by\n  sorry\n"
    sub = ("import Mathlib\nimport Aesop\n\nset_option maxHeartbeats 400000\n\n"
           "theorem t (x : ℝ) : x = x := by\n  rfl\n")
    assert check_gates(sub, mode="proof", gold_text=gold).passed
    inline = "import Mathlib\nset_option maxHeartbeats 0 in\ntheorem t (x : ℝ) : x = x := by\n  rfl\n"
    assert check_gates(inline, mode="proof", gold_text=gold).passed
    opened = "import Mathlib\nopen Real\ntheorem t (x : ℝ) : x = x := by\n  rfl\n"
    assert not check_gates(opened, mode="proof", gold_text=gold).passed  # `open` still counts


ITEM_GOLD = """import PhysProofBench.Core.Probability

-- PHYSPROOFBENCH-ITEM: X
-- PHYSPROOFBENCH-DECL: thm

open PhysProofBench

/-- doc -/
theorem thm (μ : Fin 2 → ℝ) (h : IsProbDist μ) : 0 ≤ μ 0 := by
  sorry
"""

PROVER_STYLE = """import Mathlib
import Aesop

set_option maxHeartbeats 400000

theorem thm (μ : Fin 2 → ℝ) (h : IsProbDist μ) : 0 ≤ μ 0 := by
  exact h.1 0
"""


def test_restore_item_preamble_for_prover_header():
    restored, changed = restore_item_preamble(PROVER_STYLE, ITEM_GOLD)
    assert changed
    assert restored.startswith("import PhysProofBench.Core.Probability\nimport Mathlib\nimport Aesop\n")
    assert "open PhysProofBench" in restored and "exact h.1 0" in restored
    assert check_gates(restored, mode="proof", gold_text=ITEM_GOLD).passed
    # Without restoration the gate rejects it.
    assert not check_gates(PROVER_STYLE, mode="proof", gold_text=ITEM_GOLD).passed


def test_restore_is_a_no_op_for_complete_submissions():
    complete = ITEM_GOLD.replace("  sorry", "  exact h.1 0")
    assert restore_item_preamble(complete, ITEM_GOLD) == (complete, False)


def test_restore_does_not_hide_real_edits():
    extra_open = PROVER_STYLE.replace("set_option", "open Real\nset_option")
    restored, _ = restore_item_preamble(extra_open, ITEM_GOLD)
    assert not check_gates(restored, mode="proof", gold_text=ITEM_GOLD).passed
    weaker = PROVER_STYLE.replace("0 ≤ μ 0", "0 ≤ μ 0 ∨ True")
    restored, _ = restore_item_preamble(weaker, ITEM_GOLD)
    assert not check_gates(restored, mode="proof", gold_text=ITEM_GOLD).passed
    foreign = PROVER_STYLE.replace("import Aesop", "import Foo")
    restored, _ = restore_item_preamble(foreign, ITEM_GOLD)
    assert not check_gates(restored, mode="proof", gold_text=ITEM_GOLD).passed
