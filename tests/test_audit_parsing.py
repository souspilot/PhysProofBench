import pytest

from physproofbench.lean.audit import (
    SignatureParseError,
    audit_axioms,
    build_statement_preservation_source,
    namespace_wrap,
    parse_print_axioms_output,
    parse_theorem_signature,
)


def test_parse_no_axioms():
    text = "'add_comm'' does not depend on any axioms"
    assert parse_print_axioms_output(text, "add_comm'") == set()


def test_parse_some_axioms():
    text = "'foo' depends on axioms: [propext, Classical.choice]"
    assert parse_print_axioms_output(text, "foo") == {"propext", "Classical.choice"}


def test_parse_missing_returns_none():
    assert parse_print_axioms_output("no relevant output here", "foo") is None


def test_audit_axioms_allows_standard_three():
    result = audit_axioms(
        "'foo' depends on axioms: [propext, Classical.choice, Quot.sound]", "foo"
    )
    assert result.passed


def test_audit_axioms_rejects_sorry():
    result = audit_axioms("'foo' depends on axioms: [sorryAx]", "foo")
    assert not result.passed
    assert "audit: sorry_in_axiom_closure" in result.failures


def test_audit_axioms_rejects_unknown_axiom():
    result = audit_axioms("'foo' depends on axioms: [myWeirdAxiom]", "foo")
    assert not result.passed
    assert any("disallowed_axioms" in f for f in result.failures)


SIMPLE_GOLD = "theorem add_comm' (a b : Nat) : a + b = b + a := by\n  sorry\n"


def test_parse_theorem_signature_simple():
    sig = parse_theorem_signature(SIMPLE_GOLD, "add_comm'")
    assert sig.binder_groups == ["(a b : Nat)"]
    assert sig.result_type == "a + b = b + a"
    assert sig.explicit_arg_names == ["a", "b"]


def test_parse_theorem_signature_no_binders():
    text = "theorem trivial_true : True := by trivial\n"
    sig = parse_theorem_signature(text, "trivial_true")
    assert sig.binder_groups == []
    assert sig.result_type == "True"
    assert sig.explicit_arg_names == []


def test_parse_theorem_signature_mixed_binders():
    text = (
        "theorem foo {α : Type*} [Fintype α] (x : α) (h : x = x) : True := by trivial\n"
    )
    sig = parse_theorem_signature(text, "foo")
    assert sig.explicit_arg_names == ["x", "h"]
    assert sig.binder_groups == ["{α : Type*}", "[Fintype α]", "(x : α)", "(h : x = x)"]


def test_parse_theorem_signature_missing_decl_raises():
    with pytest.raises(SignatureParseError):
        parse_theorem_signature(SIMPLE_GOLD, "does_not_exist")


def test_build_statement_preservation_source():
    src = build_statement_preservation_source(
        submission_module="Submission",
        gold_text=SIMPLE_GOLD,
        decl_name="add_comm'",
    )
    assert "import Submission" in src
    assert "import GraderFixtures.Gold" not in src
    assert "example (a b : Nat) : a + b = b + a := Submission.add_comm' a b" in src


def test_namespace_wrap_moves_imports_before_namespace():
    wrapped = namespace_wrap(
        "import Mathlib\n\ntheorem foo : True := by trivial\n", "Submission"
    )
    lines = [l for l in wrapped.splitlines() if l.strip()]
    assert lines[0] == "import Mathlib"
    assert "namespace Submission" in wrapped
    assert "end Submission" in wrapped
    assert wrapped.index("namespace Submission") < wrapped.index("theorem foo")
    assert wrapped.index("theorem foo") < wrapped.index("end Submission")


def test_namespace_wrap_with_no_imports():
    wrapped = namespace_wrap("theorem foo : True := by trivial\n", "Submission")
    assert wrapped.startswith("namespace Submission")
    assert "theorem foo" in wrapped
