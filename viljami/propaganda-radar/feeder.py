"""Pull headlines from RSS feeds, classify them, and store the new ones.

    python feeder.py

Safe to run repeatedly or on a timer - already-seen URLs are skipped.
Output path is anchored to this file's location, so it works from any cwd.
"""

from datetime import date as _date
from pathlib import Path

import feedparser

from classifier import predict
from store import CsvStore

DATA_PATH = Path(__file__).resolve().parent / "data" / "feed.csv"

FEEDS = [
    ("Kurir", "https://www.kurir.rs/rss/politika"),
]


def entry_date(entry) -> str:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if t:
        return f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"
    return _date.today().isoformat()


def entry_url(entry, feed_url: str) -> str:
    return entry.get("link") or entry.get("id") or feed_url


def fetch_new_rows() -> list[dict]:
    rows = []
    for outlet, feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            label, confidence = predict(entry.title)
            rows.append(
                {
                    "outlet": outlet,
                    "date": entry_date(entry),
                    "headline": entry.title,
                    "url": entry_url(entry, feed_url),
                    "predicted_label": label,
                    "predicted_confidence": confidence,
                    "label": "",
                    "labelled_by": "",
                    "labelled_at": "",
                }
            )
    return rows


def main():
    store = CsvStore(DATA_PATH)
    added = store.upsert(fetch_new_rows())
    print(f"added {added} new headlines to {DATA_PATH}")


if __name__ == "__main__":
    main()
