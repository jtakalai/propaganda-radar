import re
from collections import Counter

import pandas as pd

from radar.config import LABELS
from radar.model.rules import fired_rules
from radar.prepare import normalise
from radar.store import CsvStore

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


def main():
    """python -m radar.model.classifier - re-predict every stored headline.

    Run after changing the rules so the stored predictions match the current
    model. Labels are left untouched.
    """
    store = CsvStore()
    df = store.load()
    predictions = pd.DataFrame([prediction_columns(h) for h in df["headline"]], index=df.index)
    df[predictions.columns] = predictions.astype(str)
    store.save(df)
    print(f"re-predicted {len(df)} headlines with {predictions['model_version'].iloc[0]}")


if __name__ == "__main__":
    main()
