"""Scrape headlines from one site's RSS feed and label them by hand.

    python scripts/label_cli.py              # headlines only
    python scripts/label_cli.py --translate  # also show an English gloss

Labels go straight into the store as you go, so quitting never loses work
and headlines you've already labelled are skipped next run. They are marked
labelled_by="hand".
"""

import argparse
import random

import feedparser

from radar.collect.rss import entry_date, entry_url
from radar.model.classifier import prediction_columns
from radar.store import CsvStore, new_row

FEED = "https://www.kurir.rs/rss/politika"
OUTLET = "Kurir"

BUCKETS = {
    "1": "vilifying_opponents",
    "2": "vilifying_neighbours",
    "3": "personality_cult",
    "4": "vilifying_eu",
    "0": "nothing",
}


def store_row(entry):
    return new_row(
        outlet=OUTLET,
        date=entry_date(entry),
        headline=entry.title,
        url=entry_url(entry, FEED),
        **prediction_columns(entry.title),
    )


def make_translator():
    from deep_translator import GoogleTranslator

    def translate(text):
        try:
            return GoogleTranslator(source="sr", target="en").translate(text)
        except Exception as e:
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
            print(f"    {entry_url(entry, FEED)}")
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
