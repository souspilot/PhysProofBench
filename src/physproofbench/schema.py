"""Pydantic models for `items/<id>/meta.yaml`. See plan.md §4."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator

ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*_\d{2}_\d{3}_\d{3}$")

Status = Literal["active", "draft", "retired", "semiformal"]
ProofKind = Literal["exact", "approximation", "hidden_assumption", "mixed"]
ApproxFlavor = Literal["disguised_limit", "controlled", "uncontrolled"]
ApproxEncoding = Literal["model_substitution", "asymptotic", "error_bound", "postulate"]
AssumptionKind = Literal["regularity", "domain", "modeling", "validity_range"]
Justification = Literal[
    "source_stated", "source_implied", "encoding_artifact", "strengthening"
]
DifficultyBand = Literal["very_small", "small", "moderate", "large", "very_large"]
Mode = Literal["proof", "autoform"]


class Source(BaseModel):
    book: str
    chapter: int
    item_label: str
    pages: list[int]


class Approximation(BaseModel):
    flavor: ApproxFlavor | None = None
    encoding: ApproxEncoding | None = None


class HiddenAssumption(BaseModel):
    id: str
    kind: AssumptionKind
    lean: str
    justification: Justification
    note: str


class NlAnchors(BaseModel):
    statement: str
    proof: str | None = None


class Difficulty(BaseModel):
    decl_count: int = Field(ge=0)
    band: DifficultyBand


class ItemMeta(BaseModel):
    id: str
    schema_version: int
    status: Status
    source: Source
    topic: list[str] = Field(default_factory=list)

    proof_kind: ProofKind
    approximation: Approximation | None = None
    hidden_assumptions: list[HiddenAssumption] = Field(default_factory=list)

    lean_file: str
    decl_name: str
    solution_file: str
    imports_physlib: bool = False
    modes: list[Mode]
    nl: NlAnchors

    difficulty: Difficulty
    depends_on: list[str] = Field(default_factory=list)
    core_deps: list[str] = Field(default_factory=list)
    library_gaps: list[str] = Field(default_factory=list)
    contributed_by: str
    reviewed_by: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_id_pattern(self) -> "ItemMeta":
        if not ID_PATTERN.match(self.id):
            raise ValueError(
                f"id {self.id!r} does not match <BOOK>_<CH>_<ITEM>_<SEQ> "
                "(e.g. SM_01_009_001) — see docs/SOURCE.md"
            )
        return self

    @model_validator(mode="after")
    def _check_proof_kind_consistency(self) -> "ItemMeta":
        touches_approx = self.proof_kind in ("approximation", "mixed")
        if touches_approx and self.approximation is None:
            raise ValueError(
                "proof_kind touches 'approximation' but no `approximation` block given"
            )
        if not touches_approx and self.approximation is not None:
            raise ValueError(
                "`approximation` block given but proof_kind doesn't touch 'approximation'"
            )
        return self

    @model_validator(mode="after")
    def _check_active_requirements(self) -> "ItemMeta":
        if self.status == "active":
            if len(set(self.reviewed_by)) < 2:
                raise ValueError(
                    "status: active requires >= 2 distinct reviewers (plan.md §4)"
                )
            strengthened = [
                a for a in self.hidden_assumptions if a.justification == "strengthening"
            ]
            if strengthened:
                raise ValueError(
                    "status: active is blocked while a hidden_assumptions[].justification "
                    "is 'strengthening' (plan.md §4) — see docs/TAXONOMY.md; this schema "
                    "check cannot see notes.md, so promoting anyway requires "
                    "`physproofbench ingest promote --force-strengthening` with a documented "
                    "justification, once that command exists"
                )
        return self


def load_item_meta(path: Path) -> ItemMeta:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ItemMeta.model_validate(data)
