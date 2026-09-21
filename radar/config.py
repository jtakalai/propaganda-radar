"""Paths and the label taxonomy - the one place either of them is defined.

Before this module existed the five labels were spelled out in four separate
files, so adding or renaming a category meant finding all four. Import from
here instead.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"

# The canonical store: every headline we have ever seen, with its prediction
# and its label if someone (or something) has given it one. See docs/data-dictionary.md.
HEADLINES = PROCESSED / "headlines.csv"

# Raw inputs, immutable once collected - regenerate with radar.collect.*, never edit.
CRTA_EXAMPLES = RAW / "crta_examples.csv"
BACKGROUND_HEADLINES = RAW / "background_headlines.csv"

# Staging, safe to clobber.
LLM_BATCH_PENDING = INTERIM / "llm_batch_pending.csv"

FIGURES = ROOT / "reports" / "figures"

LABELS = [
    "vilifying_opponents",
    "vilifying_neighbours",
    "personality_cult",
    "vilifying_eu",
    "nothing",
]

# Everything that isn't the non-event class. "nothing" dominates at roughly a
# 2% base rate, so most metrics are only meaningful over these four.
MANIPULATIONS = [label for label in LABELS if label != "nothing"]
