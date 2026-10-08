"""Thinking-budget curves: natural answers kept, long traces cut and forced,
too-short traces skipped. Fake tokenizer (1 token = 1 char) and model."""

import json
from pathlib import Path

from physproofbench.batch import FORCE_ANSWER_PHRASE, GenerationConfig, build_plan, generate_run
from physproofbench.budget import budget_curve, budget_run_dir, curve_table
from physproofbench.models.openai_client import Completion

REPO = Path(__file__).parent.parent
ITEMS, LEAN = REPO / "items", REPO / "lean"


def _source(tmp_path):
    src = tmp_path / "src"
    config = GenerationConfig(model="m", max_tokens=100)
    plan = build_plan(config=config, item_ids=["SM_01_009_001"], conditions=["no_nl_proof"],
                      samples=2, items_dir=ITEMS, lean_project_dir=LEAN)
    calls = []

    def gen(prompt, **kw):
        calls.append(kw)
        if len(calls) == 1:
            return Completion(text="```lean\nnatural\n```", model="m", finish_reason="stop",
                              reasoning="r" * 30, completion_tokens=40)
        return Completion(text="", model="m", finish_reason="length", reasoning="t" * 100,
                          completion_tokens=100)

    generate_run(config=config, plan=plan, run_dir=src, complete_fn=gen, concurrency=1,
                 log=lambda s: None)
    return src


def count(text, max_tokens, **kw):
    return len(text), text[:max_tokens]


class Force:
    def __init__(self):
        self.calls = []

    def __call__(self, prompt, prefix, **kw):
        self.calls.append(prefix)
        return Completion(text="```lean\nforced\n```", model="m", finish_reason="stop")


def test_budget_curve(tmp_path):
    src = _source(tmp_path)
    force = Force()
    stats = budget_curve(source_dir=src, budgets=[20, 50, 200], continue_fn=force,
                         count_fn=count, log=lambda s: None)
    by = {s.budget: s for s in stats}
    # 20: both traces longer than the budget -> both cut and forced.
    assert (by[20].natural, by[20].forced) == (0, 2)
    # 50: the natural 30-token trace fits; the 100-token one is cut.
    assert (by[50].natural, by[50].forced) == (1, 1)
    # 200: natural fits; the other was itself cut off at 100 -> can't evaluate.
    assert (by[200].natural, by[200].skipped_short_trace) == (1, 1)
    cut_prefixes = [p for p in force.calls if p.startswith("<think>\nt")]
    assert all(p.endswith(FORCE_ANSWER_PHRASE) for p in force.calls)
    assert any(p == "<think>\n" + "t" * 50 + FORCE_ANSWER_PHRASE for p in cut_prefixes)
    d50 = budget_run_dir(src, 50)
    natural = json.loads((d50 / "samples/SM_01_009_001/no_nl_proof/000/completion.json").read_text())
    assert natural["text"] == "```lean\nnatural\n```" and not natural.get("forced_answer")
    forced = json.loads((d50 / "samples/SM_01_009_001/no_nl_proof/001/completion.json").read_text())
    assert forced["forced_answer"] and forced["thinking_budget"] == 50
    assert json.loads((d50 / "config.json").read_text())["budget_curve"]["thinking_budget"] == 50
    # Resume does nothing; the table renders (ungraded -> no pass rates yet).
    again = Force()
    budget_curve(source_dir=src, budgets=[20, 50], continue_fn=again, count_fn=count,
                 log=lambda s: None)
    assert again.calls == []
    assert "| 50 | no_nl_proof |" in curve_table([budget_run_dir(src, b) for b in (20, 50)], ITEMS)
