"""Classifier interface: predict(headline) -> (label, confidence).

This is rung 0 of CLAUDE.md's model ladder - always predict "nothing", the
baseline nobody should lose to. Later rungs (keyword rules, TF-IDF,
embeddings, SetFit) replace the body of `predict` with the same signature,
so feeder.py and dashboard.py never need to change.
"""

LABELS = [
    "vilifying_opponents",
    "vilifying_neighbours",
    "personality_cult",
    "vilifying_eu",
    "nothing",
]


def predict(headline: str) -> tuple[str, float]:
    return "nothing", 0.0
