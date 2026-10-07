import re
from collections import Counter

from radar.config import LABELS
from radar.model.rules import fired_rules
from radar.prepare import normalise

VERSION = "rung1-rules"


def predict(headline: str) -> str:
    hits = Counter(rule.label for rule in fired_rules(headline))
    return max(LABELS, key=hits.__getitem__) if hits else "nothing"


def explain(headline: str) -> list[str]:
    patterns = [p for rule in fired_rules(headline) for p in rule.patterns]
    matched = (w for w in re.findall(r"\w+", headline) if any(p.search(normalise(w)) for p in patterns))
    return list(dict.fromkeys(matched))


def prediction_columns(headline: str) -> dict:
    return {"predicted_label": predict(headline), "model_version": VERSION}
