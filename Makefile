.PHONY: test

PYTHON := $(shell [ -x venv/bin/python ] && echo venv/bin/python || echo python)

test:
	PYTHONPATH=. $(PYTHON) -m pytest -q
