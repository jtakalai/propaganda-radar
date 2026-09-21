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
