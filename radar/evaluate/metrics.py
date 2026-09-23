"""Score the current classifier against every labelled headline.

    python scripts/evaluate.py
"""

import pandas as pd

from radar.config import BACKGROUND_HEADLINES, MANIPULATIONS
from radar.model.classifier import predict
from radar.store import CsvStore


def precision_recall(true: pd.Series, predicted: pd.Series) -> tuple[float, float]:
    hits = (true & predicted).sum()
    precision = hits / predicted.sum() if predicted.sum() else float("nan")
    return precision, hits / true.sum()


def main():
    df = CsvStore().load()
    df = df[df["label"] != ""].drop_duplicates("headline").copy()
    df["predicted"] = [predict(h)[0] for h in df["headline"]]

    print(f"{len(df)} unique labelled headlines: {df['label'].value_counts().to_dict()}\n")

    print("Flagged at all (any manipulation label)   precision  recall")
    flagged, predicted_flagged = df["label"] != "nothing", df["predicted"] != "nothing"
    print(f"  rung 0 (always nothing)                     -       {0:.2f}")
    print("  rung 1 (rules)                            %.2f       %.2f" % precision_recall(flagged, predicted_flagged))

    print("\nPer label (rung 1)                        precision  recall  support")
    for label in MANIPULATIONS:
        p, r = precision_recall(df["label"] == label, df["predicted"] == label)
        print(f"  {label:<38}  {p:.2f}       {r:.2f}    {(df['label'] == label).sum()}")

    print("\nRecall by outlet (rung 1, flagged at all)")
    by_outlet = df[flagged].groupby("outlet")["predicted"].agg(lambda s: (s != "nothing").mean())
    counts = df[flagged].groupby("outlet").size()
    for outlet, recall in by_outlet.items():
        print(f"  {outlet:<20} {recall:.2f}  (n={counts[outlet]})")

    background = pd.read_csv(BACKGROUND_HEADLINES)["Naslov"]
    rate = (background.apply(lambda h: predict(h)[0]) != "nothing").mean()
    print(f"\nFlag rate on the {len(background)} unlabelled headlines in data/raw/background_headlines.csv: {rate:.1%}")
    print("  (not a false-positive rate - that file is pro-government tabloid politics, not a neutral pool)")


if __name__ == "__main__":
    main()
