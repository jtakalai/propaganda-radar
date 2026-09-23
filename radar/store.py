"""CSV-backed storage for headlines, predictions, and labels.

`config.HEADLINES` is the one canonical data file - everything reads and
writes here, via CsvStore.upsert. Row identity is (url, headline, outlet).
"""

from datetime import datetime
from pathlib import Path

import pandas as pd

from radar.config import HEADLINES
from radar.prepare.outlets import canonical_outlet

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
    "comment",
    "labelled_by",
    "labelled_at",
    "cluster_id",
]

KEY = ["url", "headline", "outlet"]


def new_row(**values) -> dict:
    """A store row with every column present; the ones not given are empty."""
    return {**dict.fromkeys(COLUMNS, ""), **values}


class CsvStore:
    def __init__(self, path: Path = HEADLINES):
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        if not self.path.exists():
            return pd.DataFrame(columns=COLUMNS)
        df = pd.read_csv(self.path, dtype=str).fillna("")
        return df.reindex(columns=COLUMNS, fill_value="")

    def save(self, df: pd.DataFrame) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.path, index=False)

    def upsert(self, rows: list[dict]) -> int:
        """Append rows we don't already have. Returns count added."""
        df = self.load()
        rows = [{**r, "outlet": canonical_outlet(r.get("outlet", ""))} for r in rows]
        seen = {tuple(t) for t in df[KEY].itertuples(index=False)}
        new_rows = []
        for r in rows:
            key = tuple(r[k] for k in KEY)
            if key not in seen:
                seen.add(key)
                new_rows.append(r)
        if new_rows:
            df = pd.concat([df, pd.DataFrame(new_rows, columns=COLUMNS)], ignore_index=True)
            self.save(df)
        return len(new_rows)

    def set_label(self, row, label: str, labelled_by: str, comment: str = "") -> None:
        """Label the one row matching `row`'s KEY columns."""
        df = self.load()
        match = pd.Series(True, index=df.index)
        for column in KEY:
            match &= df[column] == row[column]
        df.loc[match, ["label", "comment", "labelled_by", "labelled_at"]] = [
            label,
            comment,
            labelled_by,
            datetime.now().isoformat(timespec="seconds"),
        ]
        self.save(df)
