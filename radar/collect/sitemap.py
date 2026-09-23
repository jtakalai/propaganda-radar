"""Pull unlabelled headlines and dump them to a plain batch file.

    python scripts/pull_batch.py              # latest from the RSS feed
    python scripts/pull_batch.py --random 40  # 40 headlines spread across
                                              # random days in the archive

The RSS feed only carries the last ~100 headlines, all from one news cycle.
--random samples Kurir's sitemap archive instead, so a batch can span many
days. Headlines already in the store are dropped; the output file is staging
and is overwritten each run.
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

import feedparser

from radar.collect.rss import entry_date, entry_url
from radar.config import HEADLINES, LLM_BATCH_PENDING

FEED = "https://www.kurir.rs/rss/politika"
OUTLET = "Kurir"
SITEMAP_INDEX = "https://www.kurir.rs/sitemaps-v2/index.xml"
POLITIKA_PATH = "/vesti/politika/"
USER_AGENT = "Mozilla/5.0 (propaganda-radar university project; contact via github)"
MONTHS_TO_SAMPLE = 6

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def already_seen():
    if not os.path.exists(HEADLINES):
        return set()
    with open(HEADLINES, encoding="utf-8") as f:
        return {row["headline"] for row in csv.DictReader(f)}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def list_monthly_sitemaps():
    root = ET.fromstring(fetch(SITEMAP_INDEX))
    locs = [el.text for el in root.iter(f"{NS}loc")]
    return [u for u in locs if re.search(r"/articles-\d{4}-\d{2}\.xml$", u)]


def politika_urls_from_month(sitemap_url):
    """The archived sitemaps carry <loc> + <lastmod> only, no title."""
    root = ET.fromstring(fetch(sitemap_url))
    out = []
    for url_el in root.findall(f"{NS}url"):
        loc = url_el.findtext(f"{NS}loc")
        lastmod = url_el.findtext(f"{NS}lastmod")
        if loc and POLITIKA_PATH in loc:
            out.append((loc, lastmod[:10] if lastmod else None))
    return out


def fetch_headline(url, fallback_date):
    """og:title is the un-truncated headline; datePublished beats lastmod."""
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
        except Exception as e:
            print(f"    ! skipped: {e}")
            continue
        if entry:
            results.append(entry)
        time.sleep(0.3)
    return results


def pull_latest():
    feed = feedparser.parse(FEED)
    if not feed.entries:
        raise SystemExit(f"No entries from {FEED} — check the URL in a browser.")

    print(f"{len(feed.entries)} in feed")
    return [
        {"headline": e.title, "url": entry_url(e, FEED), "date": entry_date(e)}
        for e in feed.entries
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--random",
        type=int,
        metavar="N",
        help="sample N headlines from random days across the sitemap archive "
        "instead of pulling the latest RSS items",
    )
    args = parser.parse_args()

    candidates = pull_random(args.random) if args.random else pull_latest()

    seen = already_seen()
    todo = [c for c in candidates if c["headline"] not in seen]

    LLM_BATCH_PENDING.parent.mkdir(parents=True, exist_ok=True)
    with open(LLM_BATCH_PENDING, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["outlet", "date", "headline", "url"])
        w.writeheader()
        for c in todo:
            w.writerow({"outlet": OUTLET, "date": c["date"], "headline": c["headline"], "url": c["url"]})

    print(f"{len(candidates)} pulled, {len(todo)} unlabelled -> {LLM_BATCH_PENDING}")


if __name__ == "__main__":
    main()
