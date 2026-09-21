"""Load the raw collected files into the canonical store.

    python scripts/ingest.py

This is the raw -> processed edge of the pipeline. data/raw/ is immutable:
it holds each source exactly as collected, and this is the only thing that
reads it. Re-running is safe - upsert skips rows already in the store, so
this is how you rebuild data/processed/headlines.csv from scratch after
deleting it.

CRTA's examples arrive already labelled, so they go in with labelled_by
"crta" and keep their cluster_id - the marker for the same story running
across several outlets on one day, which is what train/test splits have to
be grouped on.

Their url is the monthly report plus a #cluster-N fragment. CRTA doesn't
link individual headlines, so the report is the most specific source a
reviewer can be sent to; the fragment keeps one cluster's rows distinguishable
from another's in the same report.
"""

import pandas as pd

from radar.config import CRTA_EXAMPLES
from radar.model.classifier import prediction_columns
from radar.store import CsvStore


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
