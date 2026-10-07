# Propaganda Radar

Flags Serbian news headlines that match [CRTA's](https://crta.plus/media-information-space/front-page-manipulations/)
manipulation-narrative criteria, so a person can review them.

CRTA is a Serbian watchdog that hand-codes front pages for manipulation
narratives. They read a handful of outlets; hundreds go unread. **The value
here is coverage, not speed** — we're competing against no coverage, not
against their coders.

A flag is not a verdict. Every flag shows which rule fired, and a person
accepts or rejects it in the dashboard.

## Categories

| Label                  | CRTA's criterion                                           |
| ---------------------- | ---------------------------------------------------------- |
| `vilifying_opponents`  | discrediting opposition, protesters, the student blockades |
| `vilifying_neighbours` | Croatia, Montenegro, Kosovo framed as hostile to Serbs     |
| `personality_cult`     | Vučić as indispensable / heroic                            |
| `vilifying_eu`         | the EU and the West as hostile or hypocritical             |
| `nothing`              | none of the above — roughly 98% of headlines               |

## Run it

```sh
make              # lists every task
make setup        # install dependencies
make app          # the review dashboard
```

Every task is a module behind `make`. `make evaluate` is
`python -m radar.evaluate`, and the rest follow the same shape.

## Where things are

```
data/raw/          as collected, never edited by hand
data/interim/      staging, safe to clobber
data/processed/    headlines.csv — the one canonical dataset
radar/             all the logic, laid out by data-lifecycle stage
  store.py           the only reader/writer of headlines.csv
  collect/           2. RSS feeds, Kurir's sitemap archive
  prepare.py         3. script normalisation, outlet names
  label/             3. hand-labelling CLI, LLM-assisted labelling
  model/             5. the rungs of the model ladder
  evaluate.py        5. precision and recall
  web.py             6. communicate — serves web/ and its three endpoints
analysis/eda.py    4. explore — writes to reports/figures/
app/dashboard.py   6. communicate — our own review UI, never shown to CRTA
web/index.html     6. communicate — the site for CRTA; one file, no build step
archive/crta/      frozen — CRTA's examples and the scraper that got them
docs/              course requirements, technical report
```

## Where it stands

TODO

## The ladder

TODO

## Who

Momir, Viljami, Juuso. University of Helsinki, Introduction to Data Science,
autumn 2026.
