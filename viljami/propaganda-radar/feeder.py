"""Pull headlines from RSS feeds, classify them, and store the new ones.

    python feeder.py                  # single pull
    python feeder.py --interval 900   # keep polling every 900s (ctrl-c to stop)

Safe to run repeatedly or on a timer - already-seen URLs are skipped.
Output path is anchored to this file's location, so it works from any cwd.
"""

import argparse
import re
import time
from datetime import date as _date
from html import unescape

import feedparser

from classifier import prediction_columns
from store import DEFAULT_DATA_PATH, CsvStore

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


def entry_summary(entry) -> str:
    """Best-effort text snippet from the feed - strip HTML, collapse whitespace.

    RSS summaries are often just a thumbnail <img> with no real text (true
    for Kurir's feed), so this can legitimately come back empty. There's no
    full article body here - that would mean scraping each article page,
    which isn't built yet.
    """
    text = re.sub(r"<[^>]+>", " ", entry.get("summary", ""))
    return re.sub(r"\s+", " ", unescape(text)).strip()


def fetch_new_rows() -> list[dict]:
    rows = []
    for outlet, feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            rows.append(
                {
                    "outlet": outlet,
                    "date": entry_date(entry),
                    "headline": entry.title,
                    "url": entry_url(entry, feed_url),
                    "summary": entry_summary(entry),
                    **prediction_columns(entry.title),
                    "label": "",
                    "labelled_by": "",
                    "labelled_at": "",
                    "cluster_id": "",
                }
            )
    return rows


def poll_once(store: CsvStore) -> None:
    added = store.upsert(fetch_new_rows())
    print(f"[{_date.today().isoformat()}] added {added} new headlines to {store.path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="keep polling every N seconds instead of pulling once",
    )
    args = parser.parse_args()

    store = CsvStore(DEFAULT_DATA_PATH)
    if args.interval is None:
        poll_once(store)
        return

    try:
        while True:
            poll_once(store)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nstopping")


if __name__ == "__main__":
    main()
