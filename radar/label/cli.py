"""Scrape headlines from one site's RSS feed and label them by hand.

    python scripts/label_cli.py              # headlines only
    python scripts/label_cli.py --translate  # also show an English gloss (Google Translate)

Labels go straight into the canonical store as you go, so quitting never
loses work and headlines you've already labelled are skipped next run.

Hand labels are the only ones anybody has actually verified. They're marked
labelled_by="hand" so the EDA can tell them apart from CRTA's own examples
and from the LLM's guesses.
"""

import argparse
import datetime
import random

from radar.model.classifier import prediction_columns
from radar.store import CsvStore

FEED = "https://www.kurir.rs/rss/politika"  # politics section only; check in a browser first
OUTLET = "Kurir"

BUCKETS = {
    "1": "vilifying_opponents",
    "2": "vilifying_neighbours",
    "3": "personality_cult",
    "4": "vilifying_eu",
    "0": "nothing",
}


def entry_date(entry):
    """Publish date as YYYY-MM-DD; fall back to today if the feed omits it."""
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if t:
        return f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"
    return datetime.date.today().isoformat()


def entry_url(entry):
    """Article link; fall back to the guid, then the feed URL."""
    return entry.get("link") or entry.get("id") or FEED


def store_row(entry):
    """A full store row for a feed entry, prediction included but unlabelled."""
    return {
        "outlet": OUTLET,
        "date": entry_date(entry),
        "headline": entry.title,
        "url": entry_url(entry),
        "summary": "",
        **prediction_columns(entry.title),
        "label": "",
        "comment": "",
        "labelled_by": "",
        "labelled_at": "",
        "cluster_id": "",
    }


def make_translator():
    from deep_translator import GoogleTranslator

    def translate(text):
        try:
            return GoogleTranslator(source="sr", target="en").translate(text)
        except Exception as e:  # network down, rate limit, etc.
            return f"(translation failed: {e})"

    return translate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--translate",
        action="store_true",
        help="show an English gloss of each headline via Google Translate",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="label in random order instead of feed order",
    )
    args = parser.parse_args()

    translate = make_translator() if args.translate else None

    import feedparser

    feed = feedparser.parse(FEED)
    if not feed.entries:
        raise SystemExit(f"No entries from {FEED} - check the URL in a browser.")

    store = CsvStore()
    df = store.load()
    already = set(df.loc[df["label"] != "", "headline"])
    todo = [e for e in feed.entries if e.title not in already]
    if args.random:
        random.shuffle(todo)

    print(f"{len(feed.entries)} headlines, {len(todo)} unlabelled\n")
    for k, v in BUCKETS.items():
        print(f"  {k} = {v}")
    print("  s = skip    q = quit\n")

    counts = {}

    try:
        for i, entry in enumerate(todo, 1):
            print(f"[{i}/{len(todo)}] {entry.title}")
            print(f"    {entry_url(entry)}")
            if translate:
                print(f"    en: {translate(entry.title)}")
            while True:
                key = input("> ").strip().lower()
                if key == "q":
                    raise KeyboardInterrupt
                if key == "s":
                    break
                if key in BUCKETS:
                    label = BUCKETS[key]
                    counts[label] = counts.get(label, 0) + 1
                    row = store_row(entry)
                    store.upsert([row])
                    store.set_label(row, label, labelled_by="hand")
                    break
                print("  ? use 0-4, s, or q")
            print()
    except (KeyboardInterrupt, EOFError):
        print("\nstopping")

    print(f"\nsaved to {store.path}")
    for label, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {n:3d}  {label}")


if __name__ == "__main__":
    main()
