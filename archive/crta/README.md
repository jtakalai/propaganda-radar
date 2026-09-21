# CRTA examples — archived

Frozen on 2026-09-21. **Nothing in the live pipeline reads this directory.**

## What it is

CRTA publishes a monthly "front page manipulations" report and quotes a
handful of example headlines under each category. `scrape.py` pulled those
examples out of the seven 2026 reports into `crta_examples.csv`:

- **162 outlet-rows, 76 distinct headlines** across 13 outlets
- `cluster_id` groups the rows where the same story ran in several outlets on
  one day — the near-duplicate problem train/test splits have to respect
- labels are CRTA's own, so these are the only labels in the project that came
  from the people who defined the categories

`import_to_store.py` loaded them into `data/processed/headlines.csv` with
`labelled_by="crta"`. That already happened; those 162 rows are in the store
and committed.

## Why it's archived rather than deleted

We are not pulling from CRTA again, so the scraper is dead code in the live
tree. But the rows it produced are still most of the project's verified
labels, and the report has to explain where they came from. Keeping the
scraper and its raw output together is that explanation — readable, and
runnable if anyone ever needs to check a row against the source.

## What it is not

These are the examples CRTA *quotes to illustrate* each category, not their
full underlying dataset. They asked-for-but-never-shared dataset is still
the gap noted in CLAUDE.md. Counts skew hard: 93 of the 162 rows are
`vilifying_opponents`, and `personality_cult` has 4 distinct headlines.

## Running them anyway

Both scripts still work from the repo root, with the venv active:

```sh
python archive/crta/scrape.py            # re-scrapes, overwrites the CSV
python archive/crta/import_to_store.py   # idempotent; adds 0 rows today
```

`scrape.py` hits crta.plus seven times with a 1s delay. Don't run it casually.
