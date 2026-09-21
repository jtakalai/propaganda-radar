# Data dictionary

Every file in `data/`, what its columns mean, and how it got there.

## The pipeline

```
Kurir RSS ──────── radar/collect/rss.py ─────→ data/processed/headlines.csv
                                                             │
Kurir sitemap ──── radar/collect/sitemap.py ─→ data/interim/llm_batch_pending.csv
                                                             │
                                                             ↓
                    radar/label/{cli,llm}.py, app/dashboard.py ──→ label columns

archive/crta/ ──── ran once in Sept 2026, 162 rows, not repeated
```

Raw is immutable: nothing edits `data/raw/` after collection.

## `data/processed/headlines.csv` — the canonical store

Every headline we have ever seen, one row per (headline, outlet). Read and
written through `radar/store.py`; nothing touches the file directly.

| Column                 | Meaning                                                                        |
| ---------------------- | ------------------------------------------------------------------------------ |
| `outlet`               | Canonical outlet name — see `radar/prepare/outlets.py`                          |
| `date`                 | Publication date, `YYYY-MM-DD`                                                  |
| `headline`             | The headline as published, original script and casing                           |
| `url`                  | The article. For CRTA rows, the monthly report plus a `#cluster-N` fragment     |
| `summary`              | Feed snippet where the feed provides one. Kurir's usually doesn't — often empty |
| `predicted_label`      | What the current model says                                                     |
| `predicted_confidence` | Model's own confidence, comparable only within one `model_version`              |
| `predicted_probs`      | JSON, a score per label. Need not sum to 1                                      |
| `model_version`        | Which model produced the three columns above, e.g. `rung1-rules`                |
| `label`                | The accepted label. Empty means nobody has judged it yet                        |
| `comment`              | Why. The LLM writes its reasoning here; reviewers write their own               |
| `labelled_by`          | Provenance — see below. The most important column in the file                   |
| `labelled_at`          | ISO timestamp of the labelling                                                  |
| `cluster_id`           | Same story across outlets on one day. Only CRTA rows have it                    |

**Row identity is `(url, headline, outlet)`.** Not `url` — CRTA's rows all
share their monthly report's URL, and the same headline runs in several
outlets on the same day.

### `labelled_by`

Never pool these without saying so. Only two of them have been checked by a
person, and they are the minority.

| Value             | Who                                     | Verified? |
| ----------------- | --------------------------------------- | --------- |
| `crta`            | CRTA's own published examples           | yes       |
| `hand`            | us, through `make label`                | yes       |
| `ui`              | us, through the dashboard               | yes       |
| `claude-sonnet-5` | an LLM, via `make label-llm`            | **no**    |
| `claude-code`     | an LLM, via `make label-llm`            | **no**    |
| *(empty)*         | not yet labelled                        | —         |

## `archive/crta/crta_examples.csv` — frozen

CRTA's published example headlines. **Archived — we are not pulling from
CRTA again**, and nothing in the live pipeline reads this file. Its 162 rows
are already in the store with `labelled_by="crta"`. See
`archive/crta/README.md`.

Columns: `outlet`, `date`, `headline`, `label`, `cluster_id`, `source_url`.

These are the examples CRTA quotes to illustrate each category — **not**
their full underlying dataset, which they haven't shared. 162 outlet-rows
covering 76 distinct headlines: the gap between those two numbers is the
near-duplicate problem, and it's why splits are grouped on `cluster_id`.

## `data/raw/background_headlines.csv`

2605 Serbian headlines with a topic label (`ekonomija`, `politika`, `sport`),
left over from an unrelated headline→topic classifier. Columns: an unnamed
index, `Naslov` (headline), `Kategorija` (topic).

**This is not a neutral negative pool, and must never be treated as
`nothing`.** About 4% of it contains "blokaderi", and it also carries
"ustaše", "srbomrsci" and Picula. It looks like pro-government tabloid
politics; the outlet is unknown. Rung 1 flags 5.5% of it.

Its one legitimate use is the one `radar/evaluate/metrics.py` makes of it:
a flag *rate* on a large unlabelled pool, reported as a rate and never as a
false-positive rate. It is otherwise a source of unlabelled headlines worth
labelling.

## `data/interim/llm_batch_pending.csv`

Staging only, rewritten by every `make batch`, gitignored. Columns:
`outlet`, `date`, `headline`, `url`.

## Files that used to exist

`labels.csv`, `llm_labels.csv` and `data.csv` were separate per-person label
files from before the store existed. Every row in them is in
`data/processed/headlines.csv`; they were removed once that was verified.
Git history has them if anyone needs to check.

`data/raw/crta_examples.csv` moved to `archive/crta/` when CRTA collection
stopped.
