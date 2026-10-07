# Technical Report

Skeleton. 5 pages max, PDF, not for CRTA. Numbers from 2026-09-30, rerun first.

## 1. Purpose [0.5 p]

- CRTA hand-codes a few outlets, hundreds go unread. We cover the rest.
- Categories are CRTA's. Cite the page.
- Ethics: flag, not verdict. Human in the loop.

## 2. Data [0.5 p]

- 162 frozen CRTA examples, rest by RSS. Scraping etiquette.
- 554 rows, 369 unique, 455 labelled. Kurir is 414 of 554.

## 3. Preprocessing [0.5 p]

- Cyrillic and Latin mixed. Normalise both plus diacritic-folded.
- Row identity (url, headline, outlet). Near-duplicates leak.

## 4. Labelling [1 p]

Decides whether anything later means anything.

- crta 162, sonnet 183, claude-code 104, hand 6. Only 168 human-verified.
- Stopped hand-labelling 2026-09-30, no time. LLM self-consistency instead of
  annotator agreement.
- 84 of 455 labelled rows are "nothing". Real base rate is 2%.
- 7 of 27 CRTA Kurir rows are multi-label. We forced single. Known wrong.

## 5. EDA [0.5 p]

- Two or three figures from analysis/eda.py. Ones we use later.
- What they changed about the modelling.

## 6. Modelling [1 p]

- Ladder: each rung beats the one below or we stop. Rungs 3-4 not started.
- Rung 1 rules: precision 0.99, recall 0.45. Not held out.
  Per label: opponents 0.51, neighbours 0.29, eu 0.27, personality_cult 0.08.
- Rung 2 TF-IDF char_wb 3-5 + logreg: 0.86 / 0.92, stratified 5-fold.
- Three non-default params, one sentence each. Without balanced, 0.82 and it
  collapses to one label.
- Rung 2 never predicts vilifying_eu (11 examples). Rung 1 catches 0.27.

## 7. What evaluation doesn't tell us [0.75 p]

- Accuracy is useless at 2%. Precision and recall separately.
- Precision@k is 1.00 everywhere, meaningless on a 77% positive set.
- 0.99 is a number about a curated set, never deployment precision.
- No held-out split. No leave-one-outlet-out, which is the number that matters.
- The grouped split groups nothing. CRTA clusters are one headline string
  repeated across outlets, so the dedupe removes them before groups() runs.
  All 369 rows end up their own group. Near-duplicate leakage is unhandled.

## 8. The app [0.75 p]

- Alpine, no build step, reads the store live.
- Dashboard, relabel, fetch. Blog-post draft button planned.
- Still runs rung 1: explain() names the rule that fired. Rung 2 would flag
  with nothing to show. Needs a linear explain() first.

## 9. Canvas reflection [0.75 p]

Five short paragraphs, the five the guidelines ask for.

- Worked / didn't / changed / would do differently / next.
- Didn't: 80 positives, no held-out split, personality_cult 0.08, CRTA never
  replied.

## 10. Learning outcomes [0.25 p]

- Graded. One line each.

## While writing

- Budget adds to 5.5. Cut 2 and 3.
- Write 4 and 7 first.
