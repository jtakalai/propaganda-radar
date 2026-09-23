"""Paths and the label taxonomy - the one place either of them is defined."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"

HEADLINES = PROCESSED / "headlines.csv"
BACKGROUND_HEADLINES = RAW / "background_headlines.csv"
LLM_BATCH_PENDING = INTERIM / "llm_batch_pending.csv"

FIGURES = ROOT / "reports" / "figures"

LABELS = [
    "vilifying_opponents",
    "vilifying_neighbours",
    "personality_cult",
    "vilifying_eu",
    "nothing",
]

MANIPULATIONS = [label for label in LABELS if label != "nothing"]
