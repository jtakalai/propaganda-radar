# Propaganda Radar

Classify Serbian news headlines into CRTA's manipulation categories, or "nothing".

University data science mini-project. Momir, Viljami, Juuso. Due 26 Oct.

## What this is

CRTA (crta.plus) is a Serbian watchdog that hand-codes front pages and TV news
headlines for manipulation narratives. They publish monthly counts — 207 in July
2026 — but not the underlying per-item labels.

We automate the coding and point it at outlets they don't have capacity to monitor.

**The value is coverage, not speed.** They read a handful of outlets by hand;
hundreds go unread. We're competing against no coverage, not against their coders.

## Categories

1. `vilifying_opponents` — discrediting opposition, protesters, the student blockade movement
2. `vilifying_neighbours` — Croatia, Montenegro, Kosovo framed as hostile to Serbs
3. `personality_cult` — Vučić as indispensable / heroic
4. `vilifying_eu` — EU and the West as hostile or hypocritical
5. `nothing`

Definitions are CRTA's, from crta.plus/media-information-space/front-page-manipulations/

## Approach

Two stages: first is-it-a-manipulation (binary), then which bucket (4-way).
Binary first because "nothing" dominates everything.

Model ladder, simplest first. Each rung must beat the one below it or we stop:

0. always predict "nothing" — the baseline nobody should lose to
1. keyword + entity rules
2. TF-IDF + linear model
3. sentence embeddings + logistic regression
4. SetFit on BERTić (only if 3 justifies it)

## Constraints worth remembering

- **~80 labelled positives.** CRTA's published examples. That's it unless they share
  their data. Everything is designed around this.
- **Base rate is tiny.** Roughly 2% of random headlines. Accuracy is a useless metric
  here — use precision and recall separately, and precision@k for the ranked output.
- **Near-duplicate leakage.** The same frame runs across 4 outlets in one day. Split
  train/test by cluster, never by row.
- **Outlet is a confound.** A model can hit good scores by learning "this is Informer".
  Always check performance with the outlet held out.
- **Serbian is Cyrillic and Latin**, often mixed. Normalise both ways plus a
  diacritic-folded variant.

## Language on outputs

Flag, never verdict. "Matches CRTA's coding criteria" — not "is propaganda", never
"is false". Human in the loop, always. Show which rule or feature fired so a person
can accept or reject it.

## Course requirements

Read these only when the task touches grading, deliverables, the report, the
spotlight presentation, or scoping. They are not needed for modelling work.

- `docs/mini-project-guidelines.md` — deadlines, spotlight rules, deliverables
  (web app + 5-page report), assessment criteria
- `docs/data-lifecycle.md` — the six lifecycle stages the course grades, and
  where we stand on each

## Repo

Run everything from the repo root; `make` lists the tasks. Layout mirrors the
six lifecycle stages — see README.md for the tree and
`docs/data-dictionary.md` for every column and where each file came from.

- `radar/` — the package. `collect/` `prepare/` `label/` `model/` `evaluate/`
- `data/processed/headlines.csv` — the one canonical dataset, via `radar/store.py`.
  Row identity is `(url, headline, outlet)`; `labelled_by` carries provenance
  and separates verified labels from the LLM's guesses
- `data/raw/` — immutable
- `archive/crta/` — frozen. CRTA's 162 example rows are already in the store
  (`labelled_by="crta"`); we aren't pulling from them again
- `scripts/` — thin entrypoints, no logic
- `app/dashboard.py`, `analysis/eda.py`, `tests/`

Labels and paths live in `radar/config.py`. Don't re-spell them anywhere else.

## Open

- CRTA emailed about sharing their labelled data — no answer yet
- Some of their own examples look multi-label (7/27 Kurir is both personality cult
  and vilifying opponents). If that's common, 5-way multi-class is the wrong shape.
  The store has one `label` column, so multi-label would be a schema change.
- Inter-annotator agreement not yet measured. Every model number is uninterpretable
  until it is.

## Style

Keep it simple. Explain choices in the report, not in comments. Prefer the boring
method that we can defend over the interesting one we can't evaluate.
