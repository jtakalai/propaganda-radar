# Technical Report

Skeleton. 5 pages max, PDF, not for CRTA. Numbers from 2026-09-30, rerun first.

## 1. Purpose

Pro-government outlets dominate the Serbian media landscape and systematically push narratives that favour the ruling party. These outlets often wage smear campaigns against actors deemed hostile to the authorities. On the othe other hand, their coverage of the authorities is overwhelmingly positive.

The CRTA watchdog organisation monitors the front pages of pro-government media for such manipulations and publishes monthly media manipulation reports. CRTA identifies four categories of media manipulation in Serbia:

1. Vilifying opponents: Coverage shaming the student movement, portraying them as criminals or as wanting to destroy Serbia
2. Vilifying neighbours: Coverage painting neighbouring countries and their leaders as part of a conspiracy against Serbia
3. Personality cult: Coverage praising former president Aleksandar Vučić, framing him as an indispensable political mastermind and his achievements as historic
4. Vilifying the EU: Anti-EU content portraying it as unfriendly to Serbia and opposed to its interests.

While these reports successfully identify patterns in Serbian pro-regime media, they are published too infrequently, and no report has been published since August. Moreover, the headlines are hand-labelled, which is labour-intensive and time-consuming. Additionally, coverage is limited to the front pages and does not extend to the inner pages.

This project aims to develop a web service that automatically identifies and categorises headlines on pro-regime outlet websites using classification algorithms. This approach would enable real-time narrative monitoring and expand the scope of analysis. However, because machine learning models may incorrectly flag some headlines, CRTA’s reports should remain the main source of truth. 

The main users of this service would be watchdog organisations in Serbia and foreign policymakers. Since Serbia is due to have presidential elections this year, the project could also be used for monitoring election integrity during the campaign period.

# Data

The headlines for training machine learning models were collected by scraping the politics sections of [Kurir](kurir.rs) and [Informer](informer.rs). Both web pages and RSS feeds were scraped. The data was labelled using Claude Sonnet 5.5, and all labels were verified by a Serbian speaker. A small number of labelled example headlines were collected from CRTA’s website. The dataset contains approximately 1300 headlines.

## 3. Preprocessing [0.5 p]

A mixture of the Latin and Cyrillic scripts was used in the headlines. All headlines were first normalised to Latin, and diacritic folding was applied.

- Cyrillic and Latin mixed. Normalise both plus diacritic-folded.
- Row identity (url, headline, outlet).

## 4. Labelling [1 p]

- crta 162, llm 287, hand 6.
- 84 of 455 labelled rows are "nothing". Real base rate is 2%.
- 7 of 27 CRTA Kurir rows are multi-label. We forced single.

## 5. EDA [0.5 p]

- Two or three figures from analysis/eda.py.
- What they changed about the modelling.

## 6. Modelling [1 p]

- Ladder: each rung beats the one below or we stop.
- Rung 1 rules: precision 0.99, recall 0.45. Not held out.
  Per label: opponents 0.51, neighbours 0.29, eu 0.27, personality_cult 0.08.
- Rung 2 TF-IDF char_wb 3-5 + logreg: 0.86 / 0.92, stratified 5-fold.
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

