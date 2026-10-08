"""Two Mathlib pins (docs/DECISIONS.md): every item must state the same
theorem in both Lean projects, so results on either pin are comparable.

Text equality of the statement (comments, whitespace and `import Mathlib...`
lines ignored) is the check: ported differences belong in Core, never in
item statements. Whether Core definitions still mean the same thing on both
pins is a review obligation (items/<id>/notes.md, docs/DECISIONS.md).
"""

from pathlib import Path

import pytest

from physproofbench.lean.gates import _statement_prefix

REPO = Path(__file__).parent.parent
MAIN = REPO / "lean" / "PhysProofBench"
OTHER_PINS = [p for p in REPO.glob("lean-v*") if (p / "PhysProofBench").is_dir()]


@pytest.mark.parametrize("pin", OTHER_PINS, ids=lambda p: p.name)
def test_item_statements_identical_across_pins(pin):
    main_items = sorted((MAIN / "Items").glob("*.lean"))
    assert main_items
    for item in main_items:
        other = pin / "PhysProofBench" / "Items" / item.name
        assert other.exists(), f"{item.name} missing from pin {pin.name}"
        assert _statement_prefix(other.read_text()) == _statement_prefix(item.read_text()), \
            f"{item.name}: statement differs on pin {pin.name}"


@pytest.mark.parametrize("pin", OTHER_PINS, ids=lambda p: p.name)
def test_core_modules_present_on_every_pin(pin):
    for core in (MAIN / "Core").glob("*.lean"):
        assert (pin / "PhysProofBench" / "Core" / core.name).exists(), core.name
