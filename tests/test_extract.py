from physproofbench.extract import extract_lean


def test_extracts_single_fenced_block():
    completion = "Here you go:\n```lean\ntheorem foo : True := by trivial\n```\nDone."
    result = extract_lean(completion)
    assert result.lean == "theorem foo : True := by trivial\n"
    assert not result.used_fallback


def test_extracts_last_of_multiple_fenced_blocks():
    completion = (
        "First attempt:\n```lean\nbad\n```\n"
        "Better:\n```lean\ntheorem foo : True := by trivial\n```\n"
    )
    result = extract_lean(completion)
    assert result.lean == "theorem foo : True := by trivial\n"
    assert not result.used_fallback


def test_falls_back_to_whole_completion_when_no_fence():
    completion = "theorem foo : True := by trivial"
    result = extract_lean(completion)
    assert result.lean == "theorem foo : True := by trivial\n"
    assert result.used_fallback


def test_unterminated_fence_takes_text_after_opening_fence():
    completion = "```lean\nimport Foo\n\ntheorem t : True := by\n  trivial\n"
    result = extract_lean(completion)
    assert result.lean == "import Foo\n\ntheorem t : True := by\n  trivial\n"
    assert result.unterminated_fence
    assert not result.used_fallback
    assert "```" not in result.lean


def test_unterminated_last_fence_wins_over_earlier_closed_block():
    completion = "```lean\nold\n```\nretry:\n```lean\nnew\n"
    result = extract_lean(completion)
    assert result.lean == "new\n"
    assert result.unterminated_fence
