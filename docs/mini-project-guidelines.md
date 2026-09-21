# Mini-project guidelines (course summary)

Source: Introduction to Data Science, University of Helsinki, "Mini-project guidelines"
(courses.mooc.fi/org/uh-cs/courses/introduction-to-data-science/mp-guidelines).

## Deadlines

| What                                                   | When                               |
| ------------------------------------------------------ | ---------------------------------- |
| Group forming submitted                                | Mon 7 Sep (done)                   |
| Mini-project canvas submitted (PDF, with member names) | Mon 14 Sep (done)                  |
| **Spotlight presentations**                            | **Week 42, during workshop slots** |
| **Group project deliverables**                         | **Mon 26 Oct, 23:59**              |
| Solo project deliverables (not us)                     | Mon 30 Nov, 23:59                  |

The page says "14.-16.10.2025" for week 42. That year is left over from last
year's page. Week 42 of 2026 is 12-18 Oct, so confirm the exact workshop date with the TA.

Submission is at the Mini-Project Submission Hub. The TA is also the project coach.

## Spotlight presentation

- Exactly 3 minutes: "no more - no less".
- Aimed at the predefined target group, so **not technical**.
- Stress the selling points: why is this useful, and why is it interesting to this audience?
- Slides or a demo of the application are both fine.
- Each group also gives feedback on other groups through an online form.
- The TA grades it, taking the student feedback into account.
- Graded on preparation, not fluency. Rehearse several times.
- Not everyone has to present, as long as everyone contributes some other way.

## Deliverables (both required)

1. **Web app, website or blogpost.**
   - Put a link in the submission.
   - Written for the target audience, with no technical terms.
   - It should communicate the added value.
2. **Technical report.**
   - A PDF essay, **max 5 pages**.
   - Covers the backend and methods, and is not aimed at the target audience.
   - Reflect on the original canvas:
     - what worked
     - what didn't, and why
     - what changed from the plan, and why
     - what you would do differently
     - possible future steps
   - Also cover the technical implementation and learning outcomes.
   - Structure is free. Canvas headings are a suggestion: data collection,
     preprocessing, visualisations, machine learning, communication of results,
     building the platform.

## Assessment criteria

- **Presentation**: how clear the problem and solution are, and how convincing the pitch is for the target audience.
- **Value**: how useful the final deliverable and its results are.
- **Effort**: whether there was enough work.
- **Idea**: originality and usefulness, and whether it has wider applications.
- **Topic scope**: fit for the course, and whether **all stages of the data life cycle** are covered.
- **Actionable**: could it be used in a real application?
- **Deliverables**:
  - Is the outcome understandable and useful to the end user?
  - Is the added value clear?
  - Is the technical report clear and sound?
  - Are the learning outcomes stated?
- **Project analysis**: data wrangling, analysis and communication of results.
  - Visualisations are judged on how well they make the point.
  - Also: could other available variables have added value?

The guidelines say a project with one clean dataset and a simple prediction task should be
enriched, for example with more advanced ML or interactive visualisations. Most
canvas columns should contain real challenges.

## What this means for us (my notes, not from the course page)

- **The spotlight is about 3 weeks away and needs a non-technical demo.** The
  dashboard is the natural thing to show. Decide the demo flow and who presents soon.
- **Two audiences.** The web deliverable is for the target user (CRTA-style
  monitors and journalists). Precision@k, kappa and leave-one-outlet-out results go
  in the 5-page report.
- **"Data life cycle" is graded.** Scraping, cleaning, labelling, modelling,
  evaluation and communication are all in scope. The label-quality work
  (inter-annotator agreement, outlet confound) counts as data-wrangling effort,
  so put it in the report.
- **The report explicitly rewards honesty about what didn't work.** That suits the
  "boring method we can defend" approach in CLAUDE.md.
- **Assessment mentions "Actionable" and "Value".** The coverage-not-speed framing
  (outlets CRTA can't read) is the strongest pitch line.
- **The page says nothing about LLM use.** Check with the TA whether LLM-generated
  labels need to be disclosed, and disclose them in the report either way.
