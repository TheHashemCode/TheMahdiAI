.PHONY: test

PYTHON := $(shell [ -x venv/bin/python ] && echo venv/bin/python || echo python)
ARGS ?= -q

test:
	PYTHONPATH=. $(PYTHON) -m pytest $(ARGS)
