"""Regression tests for a real failure seen against a Qwen3 reasoning model
on vLLM: the token budget was spent thinking, `content` came back empty
with finish_reason "length", and the runner graded the empty string,
reporting a misleading `gate_fail: statement_edited`.
"""

from pathlib import Path
from types import SimpleNamespace

from physproofbench import run as run_module
from physproofbench.models import openai_client
from physproofbench.models.openai_client import Completion

REPO = Path(__file__).parent.parent


def test_empty_completion_is_not_graded(monkeypatch, tmp_path):
    monkeypatch.setattr(
        run_module,
        "complete",
        lambda *a, **k: Completion(
            text="", model="m", finish_reason="length", reasoning="thinking..."
        ),
    )
    result = run_module.run_item_once(
        item_id="SM_01_009_001",
        model="m",
        items_dir=REPO / "items",
        lean_project_dir=REPO / "lean",  # never reached: nothing to grade
        out_dir=tmp_path,
    )
    assert result.grade is None
    assert result.finish_reason == "length"
    assert result.had_reasoning
    assert (result.run_dir / "reasoning.txt").read_text() == "thinking..."
    assert not (result.run_dir / "grade.json").exists()


def _fake_client(message, captured):
    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            model="m",
            choices=[SimpleNamespace(message=message, finish_reason="stop")],
        )

    return SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )


def test_complete_captures_reasoning_content_and_thinking_flag(monkeypatch):
    captured = {}
    message = SimpleNamespace(content="answer", reasoning_content="why")
    monkeypatch.setattr(openai_client, "get_client", lambda *a, **k: _fake_client(message, captured))
    out = openai_client.complete("hi", model="m", enable_thinking=False)
    assert out.text == "answer"
    assert out.reasoning == "why"
    assert captured["extra_body"] == {"chat_template_kwargs": {"enable_thinking": False}}


def test_complete_omits_extra_body_by_default(monkeypatch):
    captured = {}
    message = SimpleNamespace(content="answer")
    monkeypatch.setattr(openai_client, "get_client", lambda *a, **k: _fake_client(message, captured))
    out = openai_client.complete("hi", model="m")
    assert out.reasoning is None
    assert captured["extra_body"] is None


def test_max_tokens_zero_negative_or_none_means_uncapped(monkeypatch):
    for value in (0, -1, None):
        captured = {}
        message = SimpleNamespace(content="x")
        monkeypatch.setattr(
            openai_client, "get_client", lambda *a, **k: _fake_client(message, captured)
        )
        openai_client.complete("hi", model="m", max_tokens=value)
        assert "max_tokens" not in captured, f"max_tokens={value!r} must be omitted"


def test_positive_max_tokens_is_sent(monkeypatch):
    captured = {}
    message = SimpleNamespace(content="x")
    monkeypatch.setattr(
        openai_client, "get_client", lambda *a, **k: _fake_client(message, captured)
    )
    openai_client.complete("hi", model="m", max_tokens=123)
    assert captured["max_tokens"] == 123


def test_client_has_no_retries_and_custom_timeout(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://127.0.0.1:1/v1")
    client = openai_client.get_client(timeout=None)
    assert client.max_retries == 0
    assert client.timeout is None


def test_cli_accepts_minus_one_max_tokens(monkeypatch, tmp_path):
    from click.testing import CliRunner

    from physproofbench import cli

    seen = {}

    def fake_complete(*a, **k):
        seen.update(k)
        return Completion(text="", model="m", finish_reason="length", reasoning="hm")

    monkeypatch.setattr(run_module, "complete", fake_complete)
    result = CliRunner().invoke(
        cli.main,
        ["run", "--item", "SM_01_009_001", "--model", "m", "--out-dir", str(tmp_path),
         "--max-tokens", "-1", "--timeout", "0"],
    )
    assert result.exit_code == 2, result.output
    assert seen["max_tokens"] == -1
    assert seen["timeout"] is None
    assert "Uncapped" in result.output
