import pytest
from pydantic import ValidationError

from physproofbench.schema import ItemMeta, load_item_meta

BASE = {
    "id": "PI_D_001",
    "lean_file": "lean/PhysProofBench/Items/PI_D_001.lean",
    "decl_name": "PI_D_001",
}


def test_minimal_item_parses_with_defaults():
    item = ItemMeta.model_validate(BASE)
    assert (item.status, item.role, item.category, item.modes) == (
        "draft", "benchmark", "-", ["proof"])
    assert item.metadata == {}


def test_metadata_is_free_form():
    data = dict(BASE, metadata={"source": {"collection": "USAPhO", "year": 2024},
                                "anything": [1, 2]})
    assert ItemMeta.model_validate(data).metadata["source"]["year"] == 2024


def test_unknown_top_level_field_rejected():
    with pytest.raises(ValidationError):
        ItemMeta.model_validate(dict(BASE, source={"book": "SM"}))


@pytest.mark.parametrize("item_id", ["PI_A_001", "PI_T_003", "SM_01_E06_001", "CAN_00_001_001"])
def test_ids_accepted(item_id):
    assert ItemMeta.model_validate(dict(BASE, id=item_id)).id == item_id


@pytest.mark.parametrize("item_id", ["not-an-id", "pi_a_001", "PI__001", "PI_A_001_"])
def test_bad_ids_rejected(item_id):
    with pytest.raises(ValidationError):
        ItemMeta.model_validate(dict(BASE, id=item_id))


def test_active_requires_two_reviewers():
    data = dict(BASE, status="active", reviewed_by=["alice"])
    with pytest.raises(ValidationError):
        ItemMeta.model_validate(data)
    data["reviewed_by"] = ["alice", "bob"]
    ItemMeta.model_validate(data)  # should not raise


def _write_item(tmp_path, nl_text, item_id="PI_D_001"):
    d = tmp_path / item_id
    d.mkdir()
    (d / "meta.yaml").write_text(
        f"id: {item_id}\nlean_file: lean/x.lean\ndecl_name: x\n", encoding="utf-8")
    if nl_text is not None:
        (d / "nl.md").write_text(nl_text, encoding="utf-8")
    return d / "meta.yaml"


def test_has_nl_proof_read_from_nl_md(tmp_path):
    path = _write_item(tmp_path, "# t\n\n## statement\n\nS.\n\n## proof\n\nP.\n")
    assert load_item_meta(path).has_nl_proof


@pytest.mark.parametrize("nl_text", [None, "## statement\n\nS.\n", "## statement\nS.\n## proof\n\n"])
def test_no_nl_proof(tmp_path, nl_text):
    assert not load_item_meta(_write_item(tmp_path, nl_text)).has_nl_proof


def test_id_must_match_directory(tmp_path):
    path = _write_item(tmp_path, None, item_id="PI_D_002")
    path.write_text("id: PI_D_001\nlean_file: x\ndecl_name: x\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_item_meta(path)
