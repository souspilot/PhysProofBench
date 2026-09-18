import pytest
from pydantic import ValidationError

from physproofbench.schema import ItemMeta

BASE = {
    "id": "SM_01_009_001",
    "schema_version": 1,
    "status": "draft",
    "source": {
        "book": "SM",
        "chapter": 1,
        "item_label": "Lemma 1.9",
        "pages": [21],
    },
    "topic": ["statistical-mechanics", "entropy"],
    "proof_kind": "exact",
    "hidden_assumptions": [],
    "lean_file": "lean/PhysProofBench/Items/SM_01_009_001.lean",
    "decl_name": "shannonEntropy_le_log_card",
    "solution_file": "lean/PhysProofBenchSolutions/SM_01_009_001.lean",
    "imports_physlib": False,
    "modes": ["proof"],
    "nl": {"statement": "nl.md#statement", "proof": "nl.md#proof"},
    "difficulty": {"decl_count": 4, "band": "small"},
    "contributed_by": "harshitbiitk@gmail.com",
    "reviewed_by": [],
}


def test_valid_draft_item_parses():
    item = ItemMeta.model_validate(BASE)
    assert item.id == "SM_01_009_001"


def test_bad_id_pattern_rejected():
    data = dict(BASE, id="not-an-id")
    with pytest.raises(ValidationError):
        ItemMeta.model_validate(data)


def test_active_requires_two_reviewers():
    data = dict(BASE, status="active", reviewed_by=["alice"])
    with pytest.raises(ValidationError):
        ItemMeta.model_validate(data)
    data["reviewed_by"] = ["alice", "bob"]
    ItemMeta.model_validate(data)  # should not raise


def test_strengthening_blocks_active():
    data = dict(
        BASE,
        status="active",
        reviewed_by=["alice", "bob"],
        proof_kind="hidden_assumption",
        hidden_assumptions=[
            {
                "id": "extra_reg",
                "kind": "regularity",
                "lean": "ContDiff ℝ 2 f",
                "justification": "strengthening",
                "note": "made the Lean proof easier",
            }
        ],
    )
    with pytest.raises(ValidationError):
        ItemMeta.model_validate(data)


def test_approximation_block_required_when_proof_kind_touches_it():
    data = dict(BASE, proof_kind="approximation")
    with pytest.raises(ValidationError):
        ItemMeta.model_validate(data)
    data["approximation"] = {"flavor": "controlled", "encoding": "error_bound"}
    ItemMeta.model_validate(data)  # should not raise
