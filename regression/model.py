import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def _stopword_label_tokenizer(stopwords: list[str]):
    stopword_set = set(stopwords)

    def tokenizer(text: str) -> list[str]:
        tokens = re.findall(r"(?u)\b\w\w+\b", text.lower())
        return ["stopword" if token in stopword_set else token for token in tokens]

    return tokenizer


def build_vectorizer(stopwords: list[str] | None = None) -> TfidfVectorizer:
    vectorizer_options = {
        "ngram_range": (1, 2),
        "sublinear_tf": True,
        "min_df": 1,
    }
    if stopwords is not None:
        vectorizer_options["tokenizer"] = _stopword_label_tokenizer(stopwords)
        vectorizer_options["token_pattern"] = None

    return TfidfVectorizer(**vectorizer_options)


def build_model(stopwords: list[str] | None = None) -> Pipeline:
    classifier = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )
    return Pipeline(
        [
            ("tfidf", build_vectorizer(stopwords)),
            ("classifier", classifier),
        ]
    )


def feature_names(model: Pipeline):
    return model.named_steps["tfidf"].get_feature_names_out()


def top_features(model: Pipeline, limit: int = 10) -> dict[str, list[tuple[str, float]]]:
    names = feature_names(model)
    classifier = model.named_steps["classifier"]
    return {
        label: sorted(zip(names, weights), key=lambda item: item[1], reverse=True)[:limit]
        for label, weights in zip(classifier.classes_, classifier.coef_)
    }