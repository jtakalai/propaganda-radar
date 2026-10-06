from data import load_data, load_stopwords, make_groups
from evaluation import baseline_predictions, evaluate, split_data
from model import build_model


def run(stopword_filtering: bool):
    data = load_data()
    data["group"] = make_groups(data)
    train_indices, test_indices = split_data(data)
    train = data.iloc[train_indices]
    test = data.iloc[test_indices]

    stopwords = load_stopwords() if stopword_filtering else None
    model = build_model(stopwords)
    model.fit(train["headline"], train["label"])
    predictions = model.predict(test["headline"])
    labels = sorted(data["label"].unique())
    return data, model, evaluate(test["label"], predictions, labels), (train_indices, test_indices)


def main():
    for stopword_filtering in (False, True):
        data, model, metrics, _ = run(stopword_filtering)
        vocabulary_size = len(model.named_steps["tfidf"].vocabulary_)
        print(f"stopword_filtering={stopword_filtering}")
        print(f"rows={len(data)} features={vocabulary_size}")
        for label, scores in metrics["report"].items():
            if isinstance(scores, dict):
                print(f"{label}: f1={scores['f1-score']:.3f}")


if __name__ == "__main__":
    main()
