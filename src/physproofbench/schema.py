"""Item metadata: `items/<id>/meta.yaml` (schema v2, docs/SCHEMA.md).

Top-level fields are only what the pipeline acts on. Provenance (source,
topic, physics notes, review notes, ...) lives in the free-form `metadata`
block, which the pipeline carries but never interprets.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

ID_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)*$")

Status = Literal["draft", "active", "retired"]
Mode = Literal["proof", "autoform"]
# `canary`: pipeline checks kept out of every benchmark number and reported
# separately. Items meant to run and be reported alongside the benchmark
# (e.g. the trivial `T` category) are `benchmark` with their own `category`.
Role = Literal["benchmark", "canary"]


class ItemMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    status: Status = "draft"
    role: Role = "benchmark"
    # Report grouping: A-E (physics-intuition categories), T (trivial
    # environment checks), SM, CAN, ...
    category: str = "-"
    lean_file: str
    decl_name: str
    modes: list[Mode] = Field(default_factory=lambda: ["proof"])
    core_deps: list[str] = Field(default_factory=list)
    reviewed_by: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    # Set by `load_item_meta` from nl.md (a non-empty `## proof` section);
    # not written in meta.yaml.
    has_nl_proof: bool = False

    @model_validator(mode="after")
    def _check_id(self) -> "ItemMeta":
        if not ID_PATTERN.match(self.id):
            raise ValueError(
                f"id {self.id!r}: use capitalised, underscore-separated alphanumerics "
                "(e.g. PI_A_001, SM_01_009_001)"
            )
        return self

    @model_validator(mode="after")
    def _check_active_requirements(self) -> "ItemMeta":
        if self.status == "active" and len(set(self.reviewed_by)) < 2:
            raise ValueError("status: active requires >= 2 distinct reviewers")
        return self


_NL_PROOF = re.compile(r"^## proof\s*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)


def load_item_meta(path: Path) -> ItemMeta:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    meta = ItemMeta.model_validate(data)
    if meta.id != path.parent.name:
        raise ValueError(f"{path}: id {meta.id!r} does not match directory name")
    nl = path.parent / "nl.md"
    if nl.exists():
        match = _NL_PROOF.search(nl.read_text(encoding="utf-8"))
        meta.has_nl_proof = bool(match and match.group(1).strip())
    return meta
