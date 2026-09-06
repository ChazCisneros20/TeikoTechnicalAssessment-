PYTHON ?= python
ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: setup pipeline dashboard

setup:
	cd "$(ROOT)" && $(PYTHON) -m pip install -r requirements.txt

pipeline: setup
	cd "$(ROOT)" && $(PYTHON) load_data.py
	cd "$(ROOT)" && $(PYTHON) part2_analysis.py
	cd "$(ROOT)" && $(PYTHON) part3_stats.py
	cd "$(ROOT)" && $(PYTHON) part4_queries.py

dashboard:
	cd "$(ROOT)" && $(PYTHON) -m streamlit run dashboard.py
