"""Score the rungs of the ladder against every labelled headline.

    python -m radar.evaluate
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from radar.config import BACKGROUND_HEADLINES, MANIPULATIONS
from radar.model.classifier import predict as rung1_predict
from radar.model.dataset import labelled
from radar.model.tfidf import build
from radar.store import CsvStore

FOLDS = 5


def precision_recall(true: pd.Series, predicted: pd.Series) -> tuple[float, float]:
    hits = (true & predicted).sum()
    precision = hits / predicted.sum() if predicted.sum() else float("nan")
    return precision, hits / true.sum() if true.sum() else float("nan")


def rung2_cross_val(df) -> tuple[np.ndarray, np.ndarray]:
    splitter = StratifiedKFold(n_splits=FOLDS, shuffle=True, random_state=0)
    split = list(splitter.split(df["headline"], df["label"]))
    predicted = cross_val_predict(build(), df["headline"], df["label"], cv=split)
    probabilities = cross_val_predict(
        build(), df["headline"], df["label"], cv=split, method="predict_proba"
    )
    nothing = sorted(df["label"].unique()).index("nothing")
    return predicted, 1.0 - probabilities[:, nothing]


def precision_at_k(flagged: pd.Series, score: np.ndarray, k: int) -> float:
    top = np.argsort(-score)[:k]
    return flagged.to_numpy()[top].mean()


def main():
    df = labelled(CsvStore().load()).drop_duplicates("headline").reset_index(drop=True)
    df["rung1"] = [rung1_predict(h) for h in df["headline"]]
    df["rung2"], flag_score = rung2_cross_val(df)

    print(f"{len(df)} unique labelled headlines: {df['label'].value_counts().to_dict()}")
    print(f"rung 2 out-of-fold, {FOLDS} folds, exact duplicates dropped first\n")

    flagged = df["label"] != "nothing"
    print("Flagged at all (any manipulation)          precision  recall")
    print("  rung 0  always nothing                      -        0.00")
    for rung, note in (("rung1", "  (not held out)"), ("rung2", "")):
        p, r = precision_recall(flagged, df[rung] != "nothing")
        print(f"  {rung}                                    {p:.2f}       {r:.2f}{note}")

    print("\nPer label                       rung1 p/r   rung2 p/r   support")
    for label in MANIPULATIONS:
        true = df["label"] == label
        cells = ""
        for rung in ("rung1", "rung2"):
            p, r = precision_recall(true, df[rung] == label)
            cells += f"  {p:.2f} {r:.2f}  "
        print(f"  {label:<28}{cells}   {true.sum()}")

    print("\nPrecision@k for rung 2's ranked queue")
    for k in (10, 20, 50, 100):
        print(f"  top {k:<4} {precision_at_k(flagged, flag_score, k):.2f}")

    print("\nRecall by outlet (flagged at all)         rung1  rung2")
    for outlet, rows in df[flagged].groupby("outlet"):
        r1 = (rows["rung1"] != "nothing").mean()
        r2 = (rows["rung2"] != "nothing").mean()
        print(f"  {outlet:<38}  {r1:.2f}   {r2:.2f}  (n={len(rows)})")

    background = pd.read_csv(BACKGROUND_HEADLINES)["Naslov"]
    rate = (background.apply(rung1_predict) != "nothing").mean()
    print(f"\nRung 1 flags {rate:.1%} of the {len(background)} unlabelled background headlines")
    print("  (not a false-positive rate - that file is pro-government tabloid politics, not a neutral pool)")


if __name__ == "__main__":
    main()
