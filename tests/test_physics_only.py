"""Physics-only test: prompts carry no answer, runs resume, answers are kept."""

import json
from pathlib import Path

import pytest
import yaml

from physproofbench.batch import FORCE_ANSWER_PHRASE, GenerationConfig, build_plan
from physproofbench.lean.gates import check_gates
from physproofbench.models.openai_client import Completion
from physproofbench.physics_only import (
    PROMPT,
    PhysicsConfig,
    final_answer,
    load_items,
    run_physics_only,
)

REPO = Path(__file__).parent.parent
ITEMS, LEAN = REPO / "items", REPO / "lean"
PI_ITEMS = [f"PI_{c}_00{n}" for c in "ABCDE" for n in (1, 2)]


def _answer_strings(expected):
    if isinstance(expected, dict):
        return [str(v) for v in expected.values()]
    return [str(expected)]


def test_load_items_takes_answer_blank_items_with_their_answers():
    items = {i.item_id: i for i in load_items(ITEMS)}
    assert len(items) == 8
    assert "PI_B_001" not in items and "PI_T_001" not in items
    assert items["PI_D_001"].expected == {"gamma": "11/9"}
    assert "5/3" in items["PI_D_001"].trap


def test_physics_prompts_do_not_contain_expected_answers_or_traps():
    for item in load_items(ITEMS):
        prompt = PROMPT.format(statement=item.statement)
        assert "expected" not in prompt.lower() and "trap" not in prompt.lower()
        for answer in _answer_strings(item.expected):
            if len(answer) >= 3:  # "3" or "2" alone also occur as ordinary numbers
                assert answer not in prompt, (item.item_id, answer)


def test_final_answer_takes_the_last_line_without_markdown():
    assert final_answer("FINAL ANSWER: 1/2\nno, wait\n**FINAL ANSWER:** γ = 11/9\n") == "γ = 11/9"
    assert final_answer("no marker here") is None


class Model:
    def __init__(self, answer="reasoning\nFINAL ANSWER: 7", fail=False, think_too_long=False):
        self.answer, self.fail, self.think_too_long = answer, fail, think_too_long
        self.calls = []

    def __call__(self, prompt, **kw):
        self.calls.append(prompt)
        if self.fail:
            raise RuntimeError("server down")
        if self.think_too_long:
            return Completion(text="", model="m", finish_reason="length", reasoning="hmm")
        return Completion(text=self.answer, model="m", finish_reason="stop", completion_tokens=9)


def _run(run_dir, model, samples=2, config=None, **kw):
    return run_physics_only(
        config=config or PhysicsConfig(model="m"), items=load_items(ITEMS, ["PI_D_001"]),
        run_dir=run_dir, samples=samples, concurrency=2, log=lambda s: None, chat_fn=model, **kw)


def test_run_saves_answers_resumes_and_writes_summary(tmp_path):
    model = Model()
    assert _run(tmp_path, model)["done"] == 2
    record = json.loads((tmp_path / "samples/PI_D_001/000.json").read_text())
    assert record["final_answer"] == "7" and "piston" in record["prompt"]
    summary = (tmp_path / "summary.md").read_text()
    assert "11/9" in summary and "5/3" in summary and "| 7 |" in summary
    assert _run(tmp_path, model)["done"] == 0
    assert len(model.calls) == 2
    assert _run(tmp_path, model, samples=3)["done"] == 1


def test_run_forces_an_answer_when_thinking_runs_out(tmp_path):
    prefixes = []

    def cont(prompt, prefix, **kw):
        prefixes.append(prefix)
        return Completion(text="done\nFINAL ANSWER: 11/9", model="m", finish_reason="stop")

    _run(tmp_path, Model(think_too_long=True), samples=1, continue_fn=cont)
    assert prefixes == ["<think>\nhmm" + FORCE_ANSWER_PHRASE]
    record = json.loads((tmp_path / "samples/PI_D_001/000.json").read_text())
    assert record["forced_answer"] is True and record["final_answer"] == "11/9"


def test_run_stops_after_repeated_failures_and_saves_nothing(tmp_path):
    stats = _run(tmp_path, Model(fail=True), samples=8, max_consecutive_errors=3)
    assert stats["aborted"] is True and stats["done"] == 0
    assert not list(tmp_path.glob("samples/*/*.json"))


def test_run_refuses_changed_settings(tmp_path):
    _run(tmp_path, Model(), samples=1)
    with pytest.raises(ValueError, match="new --run-dir"):
        _run(tmp_path, Model(), samples=1, config=PhysicsConfig(model="m", max_tokens=1))


# --- leak-free proof prompts -----------------------------------------------------


def _plan(strip):
    config = GenerationConfig(model="m", strip_statement_comments=strip)
    return build_plan(config=config, item_ids=PI_ITEMS, conditions=["no_nl_proof"], samples=1,
                      items_dir=ITEMS, lean_project_dir=LEAN)


def test_stripped_prompts_remove_answers_and_keep_the_statement():
    with_comments, stripped = _plan(False), _plan(True)
    assert any("Expected" in p.text for p in with_comments.prompts.values())
    for (item_id, _), prompt in stripped.prompts.items():
        assert "Expected" not in prompt.text and "trap" not in prompt.text, item_id
        assert f"theorem {item_id}" in prompt.text and ":= by" in prompt.text
    assert stripped.gold_shas == with_comments.gold_shas  # same gold files


def test_stripped_statement_passes_the_statement_gate():
    plan = _plan(True)
    for item_id in PI_ITEMS:
        gold = (LEAN / "PhysProofBench/Items" / f"{item_id}.lean").read_text(encoding="utf-8")
        prompt = plan.prompts[(item_id, "no_nl_proof")].text
        statement = prompt.split("```lean\n", 1)[1].split("\n```", 1)[0]
        result = check_gates(statement + "\n  trivial\n", gold_text=gold, mode="proof")
        assert "gate: statement_edited" not in result.failures, item_id


def test_older_config_without_the_field_still_resumes(tmp_path):
    from physproofbench.batch import _write_json, check_resume_compatible

    config = GenerationConfig(model="m")
    stored = {k: v for k, v in config.__dict__.items() if k != "strip_statement_comments"}
    _write_json(tmp_path / "config.json", {"generation": stored})
    check_resume_compatible(tmp_path, config)
    with pytest.raises(ValueError):
        check_resume_compatible(tmp_path, GenerationConfig(model="m",
                                                           strip_statement_comments=True))


def test_item_metadata_is_valid_yaml_for_every_pi_item():
    for item_id in PI_ITEMS:
        assert yaml.safe_load((ITEMS / item_id / "meta.yaml").read_text(encoding="utf-8"))
