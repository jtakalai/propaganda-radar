"""Classifier interface: predict(headline) -> (label, confidence, probabilities).

This is rung 0 of CLAUDE.md's model ladder - always predict "nothing", the
baseline nobody should lose to. Later rungs (keyword rules, TF-IDF,
embeddings, SetFit) replace the body of `predict` with the same signature,
so feeder.py and dashboard.py never need to change.

`probabilities` is a score per label (they don't need to sum to 1 - whatever
the model naturally produces). The dashboard shows these in a collapsed
debug panel, not the main view - keep the interface honest even when the
model behind it is a dummy.
"""

VERSION = "rung0-dummy"

LABELS = [
    "vilifying_opponents",
    "vilifying_neighbours",
    "personality_cult",
    "vilifying_eu",
    "nothing",
]


def predict(headline: str) -> tuple[str, float, dict[str, float]]:
    probabilities = {label: 0.0 for label in LABELS}
    probabilities["nothing"] = 1.0
    return "nothing", 1.0, probabilities
