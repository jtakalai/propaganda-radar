"""ARCHIVED - not part of the live pipeline. See README.md in this directory.

Pull CRTA's own published example headlines from their monthly "front page
manipulations" reports and turn them into a labelled CSV.

These are the ~80/month examples CRTA quotes to illustrate each category
(crta.plus/media-information-space/front-page-manipulations/). It's not their
full underlying dataset (they haven't shared that - see CLAUDE.md "Open"),
just the hand-picked examples in the public reports. Still real CRTA labels,
so it's the best positive-example seed we have while we wait to hear back.

    python archive/crta/scrape.py

Writes crta_examples.csv next to this file, overwriting it each run (the source reports
don't change once published, so there's no "already done" state to preserve
like the labelling CLI has). Can be run from anywhere.
"""

import csv
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path

# Serbian-language monthly reports. Slugs aren't consistent (most reuse the
# English "<month>-manipulations" slug, February and July have Serbian-only
# slugs) so this list is hand-checked against crta.plus/sr/... rather than
# generated from a pattern.
REPORT_URLS = [
    "https://crta.plus/sr/updates/january-manipulations/",
    "https://crta.plus/sr/updates/manipulacije-u-februaru/",
    "https://crta.plus/sr/updates/march-manipulations/",
    "https://crta.plus/sr/updates/april-manipulations/",
    "https://crta.plus/sr/updates/may-manipulations/",
    "https://crta.plus/sr/updates/june-manipulations/",
    "https://crta.plus/sr/updates/manipulacije-u-julu/",
]

OUT = Path(__file__).resolve().parent / "crta_examples.csv"

USER_AGENT = "Mozilla/5.0 (propaganda-radar university project; contact via github)"

# CRTA's category headings (h4) map to our label names by keyword. Subheadings
# below them (h5/h6, e.g. "Primeri:", "Kosovo:", "Studenti:") just group
# examples by topic within a category and are deliberately not matched here -
# only the h4 category heading should change what we're currently labelling.
CATEGORY_KEYWORDS = [
    ("protivnika", "vilifying_opponents"),
    ("suseda", "vilifying_neighbours"),
    ("kult", "personality_cult"),
    ("eu", "vilifying_eu"),
    ("zapad", "vilifying_eu"),
]

MONTH_NAMES = {
    name: i
    for i, names in enumerate(
        [
            ["januar", "januara"], ["februar", "februara"], ["mart", "marta"],
            ["april", "aprila"], ["maj", "maja"], ["jun", "juna"],
            ["jul", "jula"], ["avgust", "avgusta"], ["septembar", "septembra"],
            ["oktobar", "oktobra"], ["novembar", "novembra"], ["decembar", "decembra"],
        ],
        start=1,
    )
    for name in names
}

# CRTA writes dates as D.M.YYYY, D/M/YYYY, or "D. month YYYY" - inconsistently,
# even within one report - so we search for whichever shows up.
DATE_PATTERNS = [
    re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})\.?"),
    re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})"),
    re.compile(r"(\d{1,2})\.\s*([A-Za-zČčĆćĐđŠšŽž]+)\s*(\d{4})\.?"),
]

# One example item: „headline text" (date; outlet, outlet, ...) - opening
# quote is either a straight or Serbian-style curly quote.
ITEM_RE = re.compile(r'^[„“"](?P<headline>.+?)["”]\s*\((?P<paren>[^()]*)\)')


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def classify_heading(text):
    t = text.lower()
    for keyword, label in CATEGORY_KEYWORDS:
        if keyword in t:
            return label
    return None


def strip_tags(html):
    text = re.sub(r"<[^>]+>", " ", html)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&#8222;", '"').replace("&#8220;", '"').replace("&#8221;", '"')
    return re.sub(r"\s+", " ", text).strip()


def extract_date(paren):
    """Find a date anywhere in the parenthetical; return (iso_date, rest_of_string)."""
    for pattern in DATE_PATTERNS:
        m = pattern.search(paren)
        if not m:
            continue
        day, month, year = m.groups()
        month_num = int(month) if month.isdigit() else MONTH_NAMES.get(month.lower())
        if not month_num:
            continue
        date = f"{int(year):04d}-{month_num:02d}-{int(day):02d}"
        rest = paren[: m.start()] + paren[m.end() :]
        return date, rest
    return None, paren


def parse_item(text):
    """One CRTA example -> (headline, date, [outlets]), or None if it's not
    a headline example (e.g. a direct quote from a Vučić speech has no outlet)."""
    m = ITEM_RE.match(text)
    if not m:
        return None
    date, rest = extract_date(m.group("paren"))
    if not date:
        return None
    outlets = [o.strip(" ;,.") for o in rest.split(",") if o.strip(" ;,.")]
    if not outlets:
        return None
    return m.group("headline").strip(), date, outlets


TOKEN_RE = re.compile(r"<h4[^>]*>(.*?)</h4>|bde-icon-list__text'\s*>(.*?)</span>", re.S)


def parse_report(html, source_url):
    current_label = None
    rows = []
    for m in TOKEN_RE.finditer(html):
        heading_html, item_html = m.groups()
        if heading_html is not None:
            label = classify_heading(strip_tags(heading_html))
            if label:
                current_label = label
            continue
        item_text = strip_tags(item_html)
        if not item_text or current_label is None:
            continue
        parsed = parse_item(item_text)
        if not parsed:
            continue
        headline, date, outlets = parsed
        for outlet in outlets:
            rows.append(
                {
                    "outlet": outlet,
                    "date": date,
                    "headline": headline,
                    "label": current_label,
                    "cluster_id": None,  # filled in after all reports are parsed
                    "source_url": source_url,
                }
            )
    return rows


def assign_cluster_ids(rows):
    """Rows sharing (label, date, headline) are the same story run by
    multiple outlets - CLAUDE.md's near-duplicate leakage case. Tag them so
    a train/test split can group by cluster instead of by row."""
    seen = {}
    for row in rows:
        key = (row["label"], row["date"], row["headline"])
        if key not in seen:
            seen[key] = len(seen) + 1
        row["cluster_id"] = seen[key]


def main():
    all_rows = []
    for url in REPORT_URLS:
        try:
            html = fetch(url)
        except Exception as e:  # network down, page moved, etc.
            print(f"  ! failed to fetch {url}: {e}")
            continue
        rows = parse_report(html, url)
        print(f"{url} -> {len(rows)} outlet-rows")
        all_rows.extend(rows)
        time.sleep(1)  # be polite, it's their server

    assign_cluster_ids(all_rows)

    fieldnames = ["outlet", "date", "headline", "label", "cluster_id", "source_url"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)

    n_clusters = len({r["cluster_id"] for r in all_rows})
    print(f"\nsaved {len(all_rows)} rows ({n_clusters} distinct headlines) to {OUT}")
    for label, n in Counter(r["label"] for r in all_rows).most_common():
        print(f"  {n:3d}  {label}")


if __name__ == "__main__":
    main()
