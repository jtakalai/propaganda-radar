from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit


def split_data(data, test_size: float = 0.25, random_state: int = 42):
    groups = data["group"]
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_indices, test_indices = next(splitter.split(data, data["label"], groups=groups))
    return train_indices, test_indices


def evaluate(y_true, y_pred, labels):
    return {
        "report": classification_report(
            y_true,
            y_pred,
            labels=labels,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels),
    }


def baseline_predictions(y_train, n_rows: int):
    majority = y_train.value_counts().index[0]
    return majority, [majority] * n_rows