# Technical Report

Skeleton. 5 pages max, PDF, not for CRTA. Numbers from 2026-09-30, rerun first.

## 1. Purpose

Pro-government outlets dominate the Serbian media landscape and systematically push narratives that favour the ruling party [1]. These outlets often wage smear campaigns against actors deemed hostile to the authorities [2]. On the other hand, their coverage of the authorities is overwhelmingly positive.

The CRTA watchdog organisation monitors the front pages of pro-government media for such manipulations and publishes monthly media manipulation reports [3]. CRTA identifies four categories of media manipulation in Serbia:

1. Vilifying opponents: Coverage shaming the student movement, portraying them as criminals or as wanting to destroy Serbia
2. Vilifying neighbours: Coverage painting neighbouring countries and their leaders as part of a conspiracy against Serbia
3. Personality cult: Coverage praising former president Aleksandar Vučić, framing him as an indispensable political mastermind and his achievements as historic
4. Vilifying the EU: Anti-EU content portraying it as unfriendly to Serbia and opposed to its interests.

While these reports successfully identify patterns in Serbian pro-regime media, they are published too infrequently, and no report has been published since August [3]. Moreover, the headlines appear to be hand-labelled, which is labour-intensive and time-consuming. Additionally, coverage is limited to the front pages and does not extend to the inner pages.

This project aims to develop a web service that automatically identifies and categorises headlines on pro-regime outlet websites using classification algorithms. This approach would enable real-time narrative monitoring and expand the scope of analysis. However, because machine learning models may incorrectly flag some headlines, CRTA’s reports should remain the main source of truth. 

The main users of this service would be watchdog organisations in Serbia and foreign policymakers. Since Serbia is due to hold presidential elections this year due to Vučić's resignation, the project could also be used to monitor election integrity during the campaign period.

# 2. Data

The headlines for training machine learning models were collected by scraping the politics sections of [Kurir](kurir.rs) and [Informer](informer.rs) portals. Both web pages and RSS feeds were scraped. The data was labelled using Claude Sonnet 5.5, and all labels were verified by a Serbian speaker. A small number of labelled example headlines were collected from CRTA’s website. 

The dataset is stored as a CSV file and contains approximately 1300 headlines. The file contains the following columns: headline, label, source (outlet), url and date.

## 3. Preprocessing

A mixture of the Latin and Cyrillic scripts was used in the headlines. All headlines were first normalised to Latin, and diacritic folding was applied. Next, stopwords were removed. However, stopword removal was skipped for the model based on Sentence Transformer embeddings. Finally, the headlines were deduplicated.

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

## 8. The app

We present the headline classification results in a web app inspired by CRTA's monthly media manipulation reports. Users can specify a time period and check the number of headlines in each category. Labellers can verify AI-labelled headlines. We plan to add support for posting blog posts to the platform. Keywords important to determining a headline's category are highlighted.

The frontend is built with Alpine.js, a lightweight JavaScript framework that enables dynamic updates without a build step. The app reads the data store live, providing real-time updates to the user interface. The backend is implemented using Python's built-in http package to minimise complexity.

## 9. Canvas reflection [0.75 p]

Five short paragraphs, the five the guidelines ask for.

- Worked / didn't / changed / would do differently / next.
- Didn't: 80 positives, no held-out split, personality_cult 0.08, CRTA never
  replied.

## 10. Learning outcomes

We have delivered an end-to-end data science project covering all stages of the data lifecycle. By creating a data science project canvas, we learned how to plan a project. Scraping multiple websites taught us how to organise data from different sources. During the preprocessing and modelling stage, we learned how to work with textual data. Finally, through the spotlight presentation, we enhanced our ability to convey results to stakeholders efficiently.

## References 
[1] Media Pluralism Monitor 2026, https://cmpf.eui.eu/country/serbia-2026/
[2] CRTA Media and Information Space Page, https://crta.plus/media-information-space/
[3] CRTA Front Page Manipulations Overview, https://crta.plus/media-information-space/front-page-manipulations/