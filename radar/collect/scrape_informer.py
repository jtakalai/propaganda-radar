"""Pull headlines from Informer politics page and store the new ones.

    uv run python -m radar.collect.scrape_informer      # single pull
    uv run python -m radar.collect.scrape_informer  --interval 900   # keep polling every 900s (ctrl-c to stop)

Safe to run repeatedly or on a timer - headlines already in the store are
skipped. Writes to config.HEADLINES, so it works from any cwd.
"""

import argparse
import time
import traceback
from datetime import date as _date

import requests
import tqdm
from bs4 import BeautifulSoup

from radar.model.classifier import prediction_columns
from radar.store import CsvStore

BASE_URL = "https://informer.rs"
OUTLET = "Informer"


def get_page_url(page: int) -> str:
    return f"{BASE_URL}/politika?page={page}"


def get_date_of_article(link: str, session: requests.Session) -> _date:
    article = session.get(link).text
    soup = BeautifulSoup(article, "html.parser")
    date = soup.select_one("div.single-news-author-time > p")
    return _date.strptime(date.text, "%d.%m.%Y")


def fetch_headlines_dates_and_links_from_page(page: int, session: requests.Session) -> list[tuple[str, _date, str]]:
    """Fetch headlines from a single Informer politics page."""
    try:
        html_text = session.get(get_page_url(page), timeout=30).text
        soup = BeautifulSoup(html_text, "html.parser")
        headlines_elements = soup.select('div.main-content a[href=" /politika "] + h2 a')
        if any(headline_element is None for headline_element in headlines_elements):
            print("There were None headlines on page", page)
        headlines_elements = list(filter(lambda el: el is not None and el.text.strip(), headlines_elements))
        headlines = [el.text.strip() for el in headlines_elements]
        links = [el["href"] for el in headlines_elements]
        dates = [get_date_of_article(f"{BASE_URL}{link.strip()}", session) for link in links]
        return list(zip(headlines, dates, [f"{BASE_URL}{link.strip()}" for link in links]))
    except Exception as e:
        print(f"! error fetching page {page}: {e}")
        print(traceback.format_exc())
        return []


def fetch_new_rows(pages_to_fetch: int) -> list[dict]:
    rows = []
    session = requests.Session()
    for page in tqdm.tqdm(range(1, pages_to_fetch+1)):
        headlines_dates = fetch_headlines_dates_and_links_from_page(page, session)
        for headline, date, url in headlines_dates:
            rows.append(
                {
                    "outlet": OUTLET,
                    "date": date,
                    "headline": headline,
                    "url": url,
                    "summary": "",
                    **prediction_columns(headline),
                    "label": "",
                    "comment": "",
                    "labelled_by": "",
                    "labelled_at": "",
                    "cluster_id": "",
                }
            )
        time.sleep(1)
    return rows


def poll_once(store: CsvStore, pages_to_fetch: int) -> None:
    added = store.upsert(fetch_new_rows(pages_to_fetch))
    print(f"[{_date.today().isoformat()}] added {added} new headlines to {store.path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="keep polling every N seconds instead of pulling once",
    )
    parser.add_argument(
        "--n-pages",
        type=int,
        default=4,
        help="Number of pages to pull"
    )
    args = parser.parse_args()

    store = CsvStore()
    if args.interval is None:
        poll_once(store, args.n_pages)
        return

    try:
        while True:
            poll_once(store, pages_to_fetch=args.n_pages)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nstopping")


if __name__ == "__main__":
    main()
