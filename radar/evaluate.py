"""Score the rungs of the ladder against the labelled headlines."""

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from radar.config import BACKGROUND_HEADLINES, CRTA_SAMPLE, MANIPULATIONS
from radar.model.classifier import predict as rung1_predict
from radar.model.dataset import labelled
from radar.model.tfidf import build
from radar.store import CsvStore


FOLDS = 5


def precision_recall(true: pd.Series, predicted: pd.Series) -> tuple[float, float]:
    hits = (true & predicted).sum()
    precision = hits / predicted.sum() if predicted.sum() else float("nan")
    return precision, hits / true.sum() if true.sum() else float("nan")


def print_flag_row(name: str, true, predicted, note: str = "") -> None:
    p, r = precision_recall(np.asarray(true), np.asarray(predicted))
    print(f"  {name:<41}{p:.2f}       {r:.2f}{note}")


def rung2_cross_val(df) -> tuple[np.ndarray, np.ndarray]:
    splitter = StratifiedKFold(n_splits=FOLDS, shuffle=True, random_state=0)
    split = list(splitter.split(df["headline"], df["label"]))
    predicted = cross_val_predict(build(), df["headline"], df["label"], cv=split)
    probabilities = cross_val_predict(
        build(), df["headline"], df["label"], cv=split, method="predict_proba"
    )
    nothing = sorted(df["label"].unique()).index("nothing")
    return predicted, 1.0 - probabilities[:, nothing]


def rung2_held_out(df, train: pd.Series) -> np.ndarray:
    model = build().fit(df.loc[train, "headline"], df.loc[train, "label"])
    return model.predict(df.loc[~train, "headline"])


def precision_at_k(flagged: pd.Series, score: np.ndarray, k: int) -> float:
    top = np.argsort(-score)[:k]
    return flagged.to_numpy()[top].mean()


def main():
    df = labelled(CsvStore().load()).drop_duplicates("headline").reset_index(drop=True)
    df["rung1"] = [rung1_predict(h) for h in df["headline"]]
    df["rung2"], flag_score = rung2_cross_val(df)

    print(
        f"{len(df)} unique labelled headlines: {df['label'].value_counts().to_dict()}"
    )
    print(f"rung 2 out-of-fold, {FOLDS} folds, exact duplicates dropped first")

    flagged = df["label"] != "nothing"
    print("Flagged at all (any manipulation)          precision  recall")
    print("  rung 0  always nothing                      -        0.00")
    print_flag_row(
        "always flag",
        flagged,
        np.ones(len(df), bool),
        "  (the set's positive rate)",
    )
    print_flag_row("rung1", flagged, df["rung1"] != "nothing", "  (not held out)")
    print_flag_row("rung2", flagged, df["rung2"] != "nothing")

    print("\nPer label                       rung1 p/r   rung2 p/r   support")
    for label in MANIPULATIONS:
        true = df["label"] == label
        cells = ""
        for rung in ("rung1", "rung2"):
            p, r = precision_recall(true, df[rung] == label)
            cells += f"  {p:.2f} {r:.2f}  "
        print(f"  {label:<28}{cells}   {true.sum()}")
    nothing = df["label"] == "nothing"
    print(
        f"  rung 2 gets {(df.loc[nothing, 'rung2'] == 'nothing').mean():.2f} of the 'nothing' rows right"
    )

    print("\nPrecision@k for rung 2's ranked queue")
    for k in (10, 20, 50, 100):
        print(f"  top {k:<4} {precision_at_k(flagged, flag_score, k):.2f}")

    print("\nRecall by outlet (flagged at all)         rung1  rung2")
    for outlet, rows in df[flagged].groupby("outlet"):
        r1 = (rows["rung1"] != "nothing").mean()
        r2 = (rows["rung2"] != "nothing").mean()
        print(f"  {outlet:<38}  {r1:.2f}   {r2:.2f}  (n={len(rows)})")

    print("\nRung 2 with one outlet held out           precision  recall")
    for train_outlet, test_outlet in (
        ("Kurir", "Informer"),
        ("Informer", "Kurir"),
    ):
        train = df["outlet"] == train_outlet
        test = df["outlet"] == test_outlet
        predicted = rung2_held_out(df[train | test], train[train | test])
        print_flag_row(
            f"train {train_outlet}, test {test_outlet}",
            flagged[test],
            predicted != "nothing",
        )
        print_flag_row("  always flag", flagged[test], np.ones(test.sum(), bool))

    crta = df["sample"] == CRTA_SAMPLE
    predicted = rung2_held_out(df, ~crta)
    truth = df.loc[crta, "label"].to_numpy()
    print(f"\nAgainst CRTA's own labels ({crta.sum()} headlines, all manipulations)")
    print("  rung 2 is trained on everything else")
    print(
        f"  rung 2 flags {(predicted != 'nothing').mean():.2f}, same category as CRTA {(predicted == truth).mean():.2f}"
    )
    print(
        f"  rung 1 flags {(df.loc[crta, 'rung1'] != 'nothing').mean():.2f}, same category as CRTA {(df.loc[crta, 'rung1'] == truth).mean():.2f}"
    )

    background = pd.read_csv(BACKGROUND_HEADLINES)
    politics = background[background["Kategorija"] == "politika"]["Naslov"]
    rate1 = (politics.apply(rung1_predict) != "nothing").mean()
    rate2 = (
        build().fit(df["headline"], df["label"]).predict(politics) != "nothing"
    ).mean()
    print(f"\nShare of the {len(politics)} unlabelled politics headlines flagged")
    print(f"  rung 1 {rate1:.1%}   rung 2 {rate2:.1%}")
    print("  (we only ever collect politics, so the other sections are not scored)")


if __name__ == "__main__":
    main()
