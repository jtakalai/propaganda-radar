"""ARCHIVED - not part of the live pipeline. See README.md in this directory.

Load the archived CRTA examples into the canonical store.

    python archive/crta/import_to_store.py

This ran once. Its 162 rows are already in data/processed/headlines.csv with
labelled_by="crta", and the store is committed, so there is nothing to
re-run. It is kept because it is the only mechanical record of how those
rows got their columns. Re-running is safe: upsert skips rows already there,
so it is also how you would rebuild them if the store were ever lost.

CRTA's examples arrive already labelled, so they go in with labelled_by
"crta" and keep their cluster_id - the marker for the same story running
across several outlets on one day, which is what train/test splits have to
be grouped on.

Their url is the monthly report plus a #cluster-N fragment. CRTA doesn't
link individual headlines, so the report is the most specific source a
reviewer can be sent to; the fragment keeps one cluster's rows distinguishable
from another's in the same report.
"""

from pathlib import Path

import pandas as pd

from radar.model.classifier import prediction_columns
from radar.store import CsvStore

CRTA_EXAMPLES = Path(__file__).resolve().parent / "crta_examples.csv"


def crta_rows() -> list[dict]:
    df = pd.read_csv(CRTA_EXAMPLES, dtype=str).fillna("")
    return [
        {
            "outlet": r["outlet"],
            "date": r["date"],
            "headline": r["headline"],
            "url": f"{r['source_url']}#cluster-{r['cluster_id']}",
            "summary": "",
            **prediction_columns(r["headline"]),
            "label": r["label"],
            "comment": "",
            "labelled_by": "crta",
            "labelled_at": "",
            "cluster_id": r["cluster_id"],
        }
        for _, r in df.iterrows()
    ]


def main():
    store = CsvStore()
    added = store.upsert(crta_rows())
    print(f"CRTA examples: {added} new rows -> {store.path}")
    print(f"store now holds {len(store.load())} headlines")


if __name__ == "__main__":
    main()
