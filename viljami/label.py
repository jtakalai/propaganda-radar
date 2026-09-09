"""
Scrape headlines from one site's RSS feed and label them by hand.

    pip install feedparser deep-translator
    python label.py              # headlines only
    python label.py --translate  # also show an English gloss (Google Translate)

Labels are appended to labels.csv as you go, so quitting never loses work.
Headlines you've already labelled are skipped on the next run.
"""

import argparse
import csv
import os


FEED = "https://www.kurir.rs/rss/politika"  # politics section only; check in a browser first
OUTLET = "Kurir"
OUT = "labels.csv"

BUCKETS = {
    "1": "vilifying_opponents",
    "2": "vilifying_neighbours",
    "3": "personality_cult",
    "4": "vilifying_eu",
    "0": "nothing",
}


def already_labelled():
    if not os.path.exists(OUT):
        return set()
    with open(OUT, encoding="utf-8") as f:
        return {row["headline"] for row in csv.DictReader(f)}


def save(row):
    new_file = not os.path.exists(OUT)
    with open(OUT, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["outlet", "date", "headline", "label", "url"])
        if new_file:
            w.writeheader()
        w.writerow(row)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--translate",
    action="store_true",
    help="show an English gloss of each headline via Google Translate",
)
args = parser.parse_args()

translate = None
if args.translate:
    from deep_translator import GoogleTranslator

    def translate(text):
        try:
            return GoogleTranslator(source="sr", target="en").translate(text)
        except Exception as e:  # network down, rate limit, etc.
            return f"(translation failed: {e})"

import feedparser

feed = feedparser.parse(FEED)
if not feed.entries:
    raise SystemExit(f"No entries from {FEED} — check the URL in a browser.")

seen = already_labelled()
todo = [e for e in feed.entries if e.title not in seen]

print(f"{len(feed.entries)} headlines, {len(todo)} unlabelled\n")
for k, v in BUCKETS.items():
    print(f"  {k} = {v}")
print("  s = skip    q = quit\n")

counts = {}

try:
    for i, entry in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {entry.title}")
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
                save(
                    {
                        "outlet": OUTLET,
                        "date": entry.get("published", ""),
                        "headline": entry.title,
                        "label": label,
                        "url": entry.get("link", ""),
                    }
                )
                break
            print("  ? use 0-4, s, or q")
        print()
except (KeyboardInterrupt, EOFError):
    print("\nstopping")

print(f"\nsaved to {OUT}")
for label, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {n:3d}  {label}")
