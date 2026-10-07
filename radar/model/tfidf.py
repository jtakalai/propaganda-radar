"""Rung 2: character n-grams and logistic regression."""

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from radar.config import LABELS, RUNG2
from radar.model.dataset import labelled
from radar.prepare import normalise
from radar.store import CsvStore

VERSION = "rung2-tfidf"

_model = None


def build():
    return make_pipeline(
        TfidfVectorizer(
            preprocessor=normalise,
            analyzer="char_wb",
            ngram_range=(3, 5),
        ),
        LogisticRegression(class_weight="balanced"),
    )


def train(headlines, labels, path=RUNG2):
    model = build().fit(list(headlines), list(labels))
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return model


def load(path=RUNG2):
    global _model
    if _model is None:
        if not path.exists():
            raise FileNotFoundError(f"no model at {path} - run `make train` first")
        _model = joblib.load(path)
    return _model


def predict(headline: str) -> tuple[str, float, dict[str, float]]:
    model = load()
    probabilities = dict(zip(model.classes_, model.predict_proba([headline])[0]))
    scores = {label: float(probabilities.get(label, 0.0)) for label in LABELS}
    label = max(scores, key=scores.__getitem__)
    return label, scores[label], scores


def main():
    df = labelled(CsvStore().load())
    train(df["headline"], df["label"])
    print(f"fitted on {len(df)} labelled rows -> {RUNG2}")


if __name__ == "__main__":
    main()
