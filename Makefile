# Everything runs from the repo root. PYTHONPATH is prepended, not replaced -
# shell.nix puts the dependencies on it, so overwriting it breaks every import.
PY := PYTHONPATH=.:$$PYTHONPATH python3

.PHONY: help ingest collect watch batch scrape label label-llm predict evaluate eda app test clean

help:
	@echo "Data"
	@echo "  make scrape     re-scrape CRTA's published examples into data/raw/"
	@echo "  make ingest     load data/raw/ into the store (safe to re-run)"
	@echo "  make collect    pull the latest headlines from the RSS feeds"
	@echo "  make watch      keep pulling every 15 minutes"
	@echo "  make batch      stage unlabelled headlines for the LLM labeller"
	@echo ""
	@echo "Labelling"
	@echo "  make label      label by hand, one headline at a time"
	@echo "  make label-llm  label the unlabelled ones with an LLM (costs money)"
	@echo ""
	@echo "Modelling"
	@echo "  make predict    re-run the classifier over the whole store"
	@echo "  make evaluate   precision and recall against every labelled headline"
	@echo "  make eda        exploratory plots into reports/figures/"
	@echo ""
	@echo "  make app        open the review dashboard"
	@echo "  make test       run the test suite"

scrape:
	$(PY) scripts/scrape_crta.py

ingest:
	$(PY) scripts/ingest.py

collect:
	$(PY) scripts/collect.py

watch:
	$(PY) scripts/collect.py --interval 900

batch:
	$(PY) scripts/pull_batch.py

label:
	$(PY) scripts/label_cli.py

label-llm:
	$(PY) scripts/label_llm.py

predict:
	$(PY) scripts/repredict.py

evaluate:
	$(PY) scripts/evaluate.py

eda:
	$(PY) analysis/eda.py

app:
	PYTHONPATH=.:$$PYTHONPATH streamlit run app/dashboard.py

test:
	PYTHONPATH=.:$$PYTHONPATH python3 -m pytest -q

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
