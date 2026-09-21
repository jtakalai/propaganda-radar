"""Re-run the current classifier over every stored headline.

    python repredict.py

Run after changing rules.py so the stored predictions (and the dashboard's
match column) reflect the current model. Human labels are left untouched.
"""

import pandas as pd

from classifier import prediction_columns
from store import DEFAULT_DATA_PATH, CsvStore

store = CsvStore(DEFAULT_DATA_PATH)
df = store.load()
predictions = pd.DataFrame([prediction_columns(h) for h in df["headline"]], index=df.index)
df[predictions.columns] = predictions.astype(str)
store.save(df)
print(f"re-predicted {len(df)} headlines with {predictions['model_version'].iloc[0]}")
