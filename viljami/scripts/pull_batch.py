"""
Pull unlabelled headlines and dump them to a plain batch file - no labelling
here, just the fetch+dedupe half of label.py.

    python scripts/pull_batch.py              # latest from the RSS feed
    python scripts/pull_batch.py --random 40   # 40 random headlines spread
                                                # across random days/months,
                                                # not just whatever's newest

The RSS feed only ever shows the last ~100 headlines, which all land in
whatever news cycle happens to be running that day (we found this out the
hard way - a "zvučni top" batch that was 53% one category). --random instead
samples from Kurir's public sitemap archive (sitemaps-v2/articles-YYYY-MM.xml,
back to 2024-09), which carries title + publish date for every article
without needing to fetch each one - so a batch can span many different days.

Checks headlines against BOTH data/labels.csv (human-labelled) and
data/llm_labels.csv (LLM-labelled) so nothing gets sent through twice.
Overwrites data/llm_batch_pending.csv each run - it's a staging file, not a
record, so there's nothing to lose by clobbering it.
"""

import argparse
import csv
import datetime
import html
import os
import random
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import feedparser

FEED = "https://www.kurir.rs/rss/politika"  # same feed label.py uses
OUTLET = "Kurir"
SITEMAP_INDEX = "https://www.kurir.rs/sitemaps-v2/index.xml"
POLITIKA_PATH = "/vesti/politika/"
USER_AGENT = "Mozilla/5.0 (propaganda-radar university project; contact via github)"

# how many distinct months to draw from for a --random pull, so a batch of
# (say) 40 headlines doesn't all land on the same one or two days
MONTHS_TO_SAMPLE = 6

DATA = Path(__file__).resolve().parent.parent / "data"
SOURCES = [DATA / "labels.csv", DATA / "llm_labels.csv"]
OUT = DATA / "llm_batch_pending.csv"


def already_seen():
    seen = set()
    for path in SOURCES:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            seen |= {row["headline"] for row in csv.DictReader(f)}
    return seen


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def list_monthly_sitemaps():
    root = ET.fromstring(fetch(SITEMAP_INDEX))
    locs = [el.text for el in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    return [u for u in locs if re.search(r"/articles-\d{4}-\d{2}\.xml$", u)]


def politika_urls_from_month(sitemap_url):
    """The archived monthly sitemaps only carry <loc> + <lastmod> (no title/
    date-published - those only exist in Google's 48h-window news sitemap),
    so this just gives us which URLs exist and a fallback date; the real
    headline has to come from the article page itself."""
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    root = ET.fromstring(fetch(sitemap_url))
    out = []
    for url_el in root.findall(f"{ns}url"):
        loc = url_el.findtext(f"{ns}loc")
        lastmod = url_el.findtext(f"{ns}lastmod")
        if loc and POLITIKA_PATH in loc:
            out.append((loc, lastmod[:10] if lastmod else None))
    return out


def fetch_headline(url, fallback_date):
    """og:title is the full un-truncated headline (JSON-LD's "headline" field
    is cut short by schema.org convention); JSON-LD's datePublished is more
    precise than the sitemap's lastmod, so prefer it when present."""
    page = fetch(url).decode("utf-8", errors="replace")
    m = re.search(r'<meta property="og:title" content="(.*?)"\s*/?>', page)
    if not m:
        return None
    headline = html.unescape(m.group(1))
    date = fallback_date
    date_m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', page)
    if date_m:
        date = date_m.group(1)
    return {"headline": headline, "url": url, "date": date or datetime.date.today().isoformat()}


def pull_random(n):
    months = list_monthly_sitemaps()
    sample_months = random.sample(months, min(MONTHS_TO_SAMPLE, len(months)))
    pool = []
    for month_url in sample_months:
        urls = politika_urls_from_month(month_url)
        print(f"  {month_url.rsplit('/', 1)[-1]}: {len(urls)} politika articles")
        pool.extend(urls)
    random.shuffle(pool)
    chosen = pool[:n]

    results = []
    for i, (url, fallback_date) in enumerate(chosen, 1):
        print(f"  fetching {i}/{len(chosen)}: {url}")
        try:
            entry = fetch_headline(url, fallback_date)
        except Exception as e:  # network hiccup, page removed, etc.
            print(f"    ! skipped: {e}")
            continue
        if entry:
            results.append(entry)
        time.sleep(0.3)  # be polite, it's their server
    return results


def pull_latest():
    feed = feedparser.parse(FEED)
    if not feed.entries:
        raise SystemExit(f"No entries from {FEED} — check the URL in a browser.")

    def entry_date(entry):
        t = entry.get("published_parsed") or entry.get("updated_parsed")
        if t:
            return f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"
        return datetime.date.today().isoformat()

    print(f"{len(feed.entries)} in feed")
    return [
        {"headline": e.title, "url": e.get("link") or e.get("id") or FEED, "date": entry_date(e)}
        for e in feed.entries
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--random",
        type=int,
        metavar="N",
        help="sample N headlines from random days across the sitemap archive "
        "(2024-09 onward) instead of pulling the latest RSS items",
    )
    args = parser.parse_args()

    candidates = pull_random(args.random) if args.random else pull_latest()

    seen = already_seen()
    todo = [c for c in candidates if c["headline"] not in seen]

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["outlet", "date", "headline", "url"])
        w.writeheader()
        for c in todo:
            w.writerow({"outlet": OUTLET, "date": c["date"], "headline": c["headline"], "url": c["url"]})

    print(f"{len(candidates)} pulled, {len(todo)} unlabelled -> {OUT}")


if __name__ == "__main__":
    main()
