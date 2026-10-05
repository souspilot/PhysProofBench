# Source books

Every item's `source.book` field is a key into this file. Adding a new book
means adding a section here first, with edition and provenance nailed down,
before any items are ingested from it.

## `SM` — Statistical Mechanics: A Mathematical Introduction

- **Authors:** Sacha Friedli and Yvan Velenik
- **Title:** *Statistical Mechanics: A Mathematical Introduction*
- **Publisher:** Cambridge University Press
- **Edition used:** "Revised version, August 22 2017" — the authors' self-hosted
  draft (`www.unige.ch/math/folks/velenik/smbook`), distributed under that
  header as "To be published by Cambridge University Press (2017)".
- **ISBN:** not printed on the draft PDF; **TBD** — confirm against the
  published CUP hardcover/paperback ISBN before citing this book externally.
  Cross-check page numbers against the published edition once known, since
  draft and final pagination can diverge.
- **Local copy:** `book/main.pdf` (the draft above), `book/errata.pdf`
  (author-maintained errata for the same draft).
- **Why this book:** rigorous (proof-first) treatment, self-contained finite
  probability-space setup in ch. 1, well suited to item-by-item formalization
  without requiring a physics library beyond finite sums and real analysis for
  the earliest chapters.

### Coverage ledger

Chapter-by-chapter formalization coverage lives in the ledger produced by
`physproofbench ingest status --book SM` (not yet implemented — `ingest/` is
post-M0). As of this writing only the hand-picked seed item exists; no
chapter has been censused (S1 ledger extraction hasn't run).

| Chapter | Ledger extracted (S1) | Items formalized | Items active |
|---|---|---|---|
| 1. Introduction | no | 8: `SM_01_009_001` (Lemma 1.9, seed), `SM_01_E06_001`, `SM_01_E05_001`, `SM_01_Q43_001`, `SM_01_E01_001`, `SM_01_E02_001`, `SM_01_E03_001`, `SM_01_006_001` | 0 |
| 2. The Curie–Weiss Model | no | 2: `SM_02_Q11_001`, `SM_02_002_001` | 0 |
| 3. The Ising Model | no | 2: `SM_03_005_001`, `SM_03_009_001` | 0 |

All 12 are `status: draft`. Only `SM_01_009_001` has a reference proof; the
other 11 are statement-only (see `docs/DECISIONS.md`, "First item batch").

### Item ID convention for this book

Friedli–Velenik numbers definitions/lemmas/theorems/propositions
**consecutively within a chapter**, not per-subsection (e.g. "Definition 1.8"
is immediately followed by "Lemma 1.9"). `plan.md`'s original
`<BOOK>_<CHAPTER>_<SECTION>_<SEQ>` id scheme assumed per-section numbering
from a different book. For `SM`, adapt it as:

```
SM_<CHAPTER two-digit>_<ITEM NUMBER three-digit>_<SEQ three-digit>
```

where `<ITEM NUMBER>` is the book's own chapter-local number (e.g. `009` for
"Lemma 1.9") and `<SEQ>` disambiguates when one book item is split into
several Lean items (`001`, `002`, ... — see `plan.md` §9 for why splitting is
sometimes necessary). A book item that is not split still gets `_001`.

Friedli–Velenik number **exercises** in a separate per-chapter sequence
(Exercise 1.6 and Example 1.6 both exist), and some results worth
formalizing are stated in running text at a numbered equation rather than as
a numbered lemma/theorem. `<ITEM NUMBER>` therefore also takes two lettered
forms, each a letter plus two digits so the field stays three characters:

- `E<nn>`: Exercise `<chapter>.<nn>`, e.g. `SM_01_E06_001` = Exercise 1.6.
- `Q<nn>`: the result at equation `(<chapter>.<nn>)`, e.g. `SM_02_Q11_001`
  = eqn. (2.11), `SM_01_Q43_001` = eqn. (1.43).

`schema.ID_PATTERN` accepts exactly these three forms.
