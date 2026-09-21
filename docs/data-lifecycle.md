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

| Stage             | Status                                                                                                            | Gap                                                                                                                                                                                             |
| ----------------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Purpose        | Drafted in CLAUDE.md. A: CRTA reads a handful of outlets by hand. B: flagged headlines from outlets nobody reads. | The target audience is not confirmed with anyone. CRTA hasn't replied. Say who the end user is: CRTA-style monitors, journalists, or the public.                                                |
| 1. Ethics         | The "flag, never verdict" and human-in-the-loop rules are in CLAUDE.md.                                           | Put this in the report as an explicit ethics section. Cover the risk of wrongly flagging an outlet, the risk of a tool that tells people what to think about news, and CRTA's political stance. |
| 2. Collect        | Kurir RSS feeder, CRTA examples scraped (162), Claude labelling.                                                  | Kurir only. Check robots.txt and terms for `crta.plus` and each new outlet before scraping. RSS is the polite default. Record what was checked.                                                 |
| 3. Preprocess     | Not started.                                                                                                      | Cyrillic/Latin normalisation, diacritic folding, near-duplicate clustering, dedupe across files.                                                                                                |
| 4. Explore        | `viljami/eda/eda.py` exists (class balance, leakage, outlet crosstab, top words).                                 | Re-run it after the dataset is merged. The outlet-confound crosstab is the key output.                                                                                                          |
| 5. Learn          | Rung 0 dummy only.                                                                                                | Rungs 1-3, with the evaluation rules in CLAUDE.md.                                                                                                                                              |
| 6. Operationalise | Streamlit dashboard exists.                                                                                       | It needs a non-technical framing for the spotlight, and the flag reason should be shown.                                                                                                        |

## Report angle

The course asks how the plan changed and what didn't work, so the iterations
here are worth writing up. Examples: the labelling approach changing from manual to
LLM-assisted, the discovery of the outlet confound, and the 5-way multi-class question.
