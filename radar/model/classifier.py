"""Classifier interface: predict(headline) -> (label, confidence, probabilities).

Later rungs of the ladder replace the body of `predict` with the same
signature, so the collect scripts and the dashboard don't change.
"""

import json
import re
from collections import Counter

from radar.config import LABELS
from radar.model.rules import fired_rules
from radar.prepare.normalise import normalise

VERSION = "rung1-rules"


def predict(headline: str) -> tuple[str, float, dict[str, float]]:
    hits = Counter(rule.label for rule in fired_rules(headline))
    if not hits:
        return "nothing", 1.0, {label: float(label == "nothing") for label in LABELS}
    probabilities = {label: float(hits[label]) for label in LABELS}
    label = max(LABELS, key=hits.__getitem__)
    return label, hits[label] / sum(hits.values()), probabilities


def explain(headline: str) -> list[str]:
    """The words of `headline` that made the model flag it, as written."""
    words = re.findall(r"\w+", headline)
    matched = []
    for rule in fired_rules(headline):
        for pattern in rule.patterns:
            for word in words:
                if pattern.search(normalise(word)) and word not in matched:
                    matched.append(word)
    return matched


def prediction_columns(headline: str) -> dict:
    """The predicted_* / model_version columns of a store row."""
    label, confidence, probabilities = predict(headline)
    return {
        "predicted_label": label,
        "predicted_confidence": confidence,
        "predicted_probs": json.dumps(probabilities),
        "model_version": VERSION,
    }
