"""Re-run the current classifier over every stored headline.

    python scripts/repredict.py

Run after changing radar/model/rules.py so the stored predictions (and the
dashboard's match column) reflect the current model. Human labels are left
untouched.
"""

import pandas as pd

from radar.model.classifier import prediction_columns
from radar.store import CsvStore


def main():
    store = CsvStore()
    df = store.load()
    predictions = pd.DataFrame([prediction_columns(h) for h in df["headline"]], index=df.index)
    df[predictions.columns] = predictions.astype(str)
    store.save(df)
    print(f"re-predicted {len(df)} headlines with {predictions['model_version'].iloc[0]}")


if __name__ == "__main__":
    main()
