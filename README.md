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

| Label                  | CRTA's criterion                                            |
| ---------------------- | ----------------------------------------------------------- |
| `vilifying_opponents`  | discrediting opposition, protesters, the student blockades   |
| `vilifying_neighbours` | Croatia, Montenegro, Kosovo framed as hostile to Serbs       |
| `personality_cult`     | Vučić as indispensable / heroic                              |
| `vilifying_eu`         | the EU and the West as hostile or hypocritical               |
| `nothing`              | none of the above — roughly 98% of headlines                 |

## Run it

```sh
nix-shell          # or: pip install -r requirements.txt && pip install -e .
make               # lists every task
make app           # the review dashboard
```

Everything runs from the repo root. The Makefile prepends the repo to
`PYTHONPATH`; `pip install -e .` does the same job permanently.

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

`docs/data-dictionary.md` explains every column and where each file comes from.

## Where it stands

Rung 1 of the model ladder (keyword and entity rules). Against 265 labelled
headlines it flags at **0.99 precision / 0.48 recall**.

Treat that recall as the real number and that precision as optimistic: the
rules were written while looking at these same headlines, and a rule-based
rung has no held-out split. Rung 2 onwards will have one.

Two things have to land before any model number means much:

- **Inter-annotator agreement is unmeasured.** Until we know how often two
  people agree on these categories, we don't know what score is even possible.
- **Outlet is a confound.** 145 of 265 labelled headlines are Kurir. A model
  can score well by learning "this is Kurir", so performance is always
  reported with the outlet held out.

## The ladder

Simplest first. Each rung has to beat the one below it or we stop.

0. always predict `nothing` — the baseline nobody should lose to
1. **keyword + entity rules** ← we are here
2. TF-IDF + linear model
3. sentence embeddings + logistic regression
4. SetFit on BERTić, only if 3 justifies it

## Who

Momir, Viljami, Juuso. University of Helsinki, Introduction to Data Science,
autumn 2026.
