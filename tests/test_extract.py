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
