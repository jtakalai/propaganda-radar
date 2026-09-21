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

## Where things are

```
data/raw/          as collected, never edited by hand
data/interim/      staging, safe to clobber
data/processed/    headlines.csv — the one canonical dataset
radar/             all the logic, laid out by data-lifecycle stage
  collect/           2. RSS feeds, Kurir's sitemap archive, CRTA's reports
  prepare/           3. script normalisation, outlet names, raw -> store
  label/             3. hand-labelling CLI, LLM-assisted labelling
  model/             5. the rungs of the model ladder
  evaluate/          5. precision and recall
analysis/eda.py    4. explore — writes to reports/figures/
app/dashboard.py   6. communicate — the review UI
scripts/           entrypoints; `make` calls these
docs/              data dictionary, course requirements
```

## Where it stands

TODO

## The ladder

TODO

## Who

Momir, Viljami, Juuso. University of Helsinki, Introduction to Data Science,
autumn 2026.
