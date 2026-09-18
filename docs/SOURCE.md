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
| 1. Introduction | no | 1: `SM_01_009_001` (Lemma 1.9, seed item, `status: draft`) | 0 |

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
