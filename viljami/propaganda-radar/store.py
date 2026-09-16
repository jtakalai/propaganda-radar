"""CSV-backed storage for scraped headlines, predictions, and human labels.

Swap for another backend later (e.g. SQLite) by writing a class with the
same three methods - load / upsert / set_label - and pointing feeder.py
and dashboard.py at it instead of CsvStore.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd

COLUMNS = [
    "outlet",
    "date",
    "headline",
    "url",
    "summary",
    "predicted_label",
    "predicted_confidence",
    "predicted_probs",
    "model_version",
    "label",
    "labelled_by",
    "labelled_at",
]


class CsvStore:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        if not self.path.exists():
            return pd.DataFrame(columns=COLUMNS)
        return pd.read_csv(self.path, dtype=str).fillna("")

    def save(self, df: pd.DataFrame) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.path, index=False)

    def upsert(self, rows: list[dict]) -> int:
        """Append rows whose url isn't already stored. Returns count added."""
        df = self.load()
        seen = set(df["url"])
        new_rows = [r for r in rows if r["url"] not in seen]
        if new_rows:
            df = pd.concat([df, pd.DataFrame(new_rows, columns=COLUMNS)], ignore_index=True)
            self.save(df)
        return len(new_rows)

    def set_label(self, url: str, label: str, labelled_by: str) -> None:
        df = self.load()
        df.loc[
            df["url"] == url, ["label", "labelled_by", "labelled_at"]
        ] = [label, labelled_by, datetime.now().isoformat(timespec="seconds")]
        self.save(df)
