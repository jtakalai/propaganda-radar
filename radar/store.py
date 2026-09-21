"""CSV-backed storage for scraped headlines, predictions, and human labels.

Swap for another backend later (e.g. SQLite) by writing a class with the
same methods - load / save / upsert / set_label - and pointing the collect
scripts and the dashboard at it instead of CsvStore.

`config.HEADLINES` is the one canonical data file for the whole project -
everything reads and writes here. Don't add another data file; if a new
source needs to feed in, write it into this one via CsvStore.upsert.

Row identity is (url, headline, outlet), not url alone. Most sources give one
URL per headline, but CRTA's rows all share their monthly report's URL -
twenty-odd rows from one link - and the same headline runs in several outlets
on the same day, which is the near-duplicate clustering CLAUDE.md warns
about. url alone collides 86 times in the current store and (url, headline)
still collides 86 times; all three columns together are unique.

Keying on url alone silently dropped CRTA rows on insert and, worse, made
labelling one of them label every other row from the same report.
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
        """Append rows we don't already have. Returns count added.

        This is the single chokepoint every source passes through, so it is
        also where outlet names get canonicalised - see prepare/outlets.py.
        """
        df = self.load()
        rows = [{**r, "outlet": canonical_outlet(r.get("outlet", ""))} for r in rows]
        seen = {tuple(t) for t in df[KEY].itertuples(index=False)}
        new_rows = [r for r in rows if tuple(r[k] for k in KEY) not in seen]
        if new_rows:
            df = pd.concat([df, pd.DataFrame(new_rows, columns=COLUMNS)], ignore_index=True)
            self.save(df)
        return len(new_rows)

    def set_label(self, row, label: str, labelled_by: str, comment: str = "") -> None:
        """Label the one row matching `row`'s KEY columns.

        `row` is any mapping with url/headline/outlet - a dict built here, or
        a pandas Series straight off `load()`.
        """
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
