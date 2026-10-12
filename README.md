# Propaganda Radar

Flags Serbian news headlines that match [CRTA's](https://crta.plus/media-information-space/front-page-manipulations/)
manipulation-narrative criteria, so a person can review them.

CRTA is a Serbian watchdog that hand-codes front pages for manipulation
narratives. They read a handful of outlets; hundreds go unread. **The value
here is coverage, not speed** — we're competing against no coverage, not
against their coders.

A flag is not a verdict. Every flag shows which rule fired, and a person
accepts or rejects it on the site.

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
make web          # the site, on http://127.0.0.1:8000
```

Every task is a module behind `make`. `make evaluate` is
`python -m radar.evaluate`, and the rest follow the same shape.

## Where things are

```
data/processed/headlines.csv   every headline we have, with its label
data/raw/                      as collected, never edited by hand
radar/                         all the code
radar/store.py                 the only code that reads or writes headlines.csv
radar/web.py                   serves web/, and writes web/data.json for the deploy
analysis/eda.py                the plots in reports/figures/
web/index.html                 the site, one file, no build step
archive/crta/                  CRTA's examples and the scraper that got them, frozen
docs/                          course requirements and the technical report
```

The modules under `radar/` follow the six stages in
[docs/data-lifecycle.md](docs/data-lifecycle.md).

## Where it stands

TODO

## The ladder

TODO

## Who

Momir, Viljami, Juuso. University of Helsinki, Introduction to Data Science,
autumn 2026.
