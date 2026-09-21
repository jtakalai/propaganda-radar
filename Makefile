PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python

.PHONY: help setup collect eda app

help:
	@echo "Setup"
	@echo "  make setup      create venv/ and install dependencies (idempotent)"
	@echo "  make collect    pull the latest headlines from the RSS feeds"
	@echo "  make eda        exploratory plots into reports/figures/"
	@echo "  make app        open the review dashboard"

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt

collect:
	$(PYTHON_VENV) scripts/collect.py

eda:
	$(PYTHON_VENV) analysis/eda.py

app:
	$(PYTHON_VENV) -m streamlit run app/dashboard.py
