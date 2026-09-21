# Data lifecycle (course summary)

Source: Introduction to Data Science, Chapter 2, "Data lifecycle: Stages of a data science
project". Pasted by Viljami on 2026-09-21 and condensed. The assessment criteria
in [mini-project-guidelines.md](mini-project-guidelines.md) grade "all stages of the data life cycle".

The cycle is iterative. Findings at a later stage should feed back into
collection, preprocessing and modelling.

## The six stages

1. **Define your purpose.**
   - Name the target audience.
   - Describe the current state A and the desired state B from their point of view.
   - Scale the idea down until it is manageable, ideally with members of the audience.
   - **Consider the ethics**, including for people outside the audience. "Don't only think
     how to do, but whether to do". The examples of bad projects are ethnic profiling
     and inferring sexual orientation from faces. Weighing benefits against harms is our responsibility.
2. **Collect data.**
   - Options: surveys, APIs, scraping.
   - Scraping is flagged as a "danger zone": respect each site's terms and conditions,
     its policies and scraping etiquette.
3. **Preprocess.**
   - Cleaning: missing values, noise, duplicates.
   - Integration: combining different representations.
   - Transformation: normalisation and standardisation.
   - Reduction: feature selection and aggregation.
   - Discretisation.
   - Subsampling.
4. **Explore (EDA).**
   - "Look at the data!"
   - Use it to spot errors from collection or preprocessing, to find outliers, and to form
     hypotheses that guide the choice of method.
5. **Learn.** The learning task must be aligned with the purpose from step 1.
6. **Operationalise and communicate.**
   - State the added value for the target audience explicitly.
   - Pick a form that suits them: app, service, presentation, report.
   - A clear pitch beats a technical write-up for non-technical clients.

## Where we stand (my notes, not from the course page)

| Stage             | Status                                                                                                                  | Gap                                                                                                                                                              |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. Purpose        | Drafted in CLAUDE.md and README. A: CRTA reads a handful of outlets by hand. B: flagged headlines from outlets nobody reads. | The target audience is not confirmed with anyone. CRTA hasn't replied. Say who the end user is: CRTA-style monitors, journalists, or the public.                   |
| 1. Ethics         | The "flag, never verdict" and human-in-the-loop rules are in CLAUDE.md and stated on the README.                          | Put this in the report as an explicit ethics section. Cover the risk of wrongly flagging an outlet, the risk of a tool that tells people what to think about news, and CRTA's political stance. |
| 2. Collect        | `radar/collect/` — Kurir RSS and Kurir's sitemap archive. CRTA's published reports (162 rows / 76 headlines) were pulled once and are frozen in `archive/crta/`. | Kurir only for live headlines. Check robots.txt and terms for `crta.plus` and each new outlet before scraping. RSS is the polite default. Record what was checked.  |
| 3. Preprocess     | `radar/prepare/` — Cyrillic/Latin + diacritic normalisation, outlet canonicalisation. One canonical store, deduped on (url, headline, outlet). | Near-duplicate clustering only exists for CRTA rows (`cluster_id`); RSS-collected headlines have none, so cluster-grouped splits don't cover them yet.              |
| 4. Explore        | `analysis/eda.py` — class balance, cluster-size leakage, outlet crosstab, headline length, script check, top words. Figures land in `reports/figures/`. | Nothing blocking. Re-run after each labelling round.                                                                                                                |
| 5. Learn          | Rung 0 baseline and rung 1 rules (`radar/model/`), scored by `radar/evaluate/`. 0.99 precision / 0.48 recall on 265 labelled headlines, optimistic — no held-out split. | Rungs 2-3. Leave-one-outlet-out is not implemented yet, and it is the number that matters: 145 of 265 labelled headlines are Kurir.                                |
| 6. Operationalise | Streamlit dashboard (`app/dashboard.py`) shows the flag, the rule that fired, and lets a reviewer accept or correct it.     | It needs a non-technical framing for the spotlight.                                                                                                                 |

## Report angle

The course asks how the plan changed and what didn't work, so the iterations
here are worth writing up. Examples: the labelling approach changing from manual to
LLM-assisted, the discovery of the outlet confound, and the 5-way multi-class question.
