.PHONY: help test validate validate-fixture validate-example validate-runs check

help:
	@echo "Available commands:"
	@echo "  make test                  Run validator unit tests"
	@echo "  make validate RUN=<path>   Validate a saved run directory"
	@echo "  make validate-fixture      Validate the canonical test fixture"
	@echo "  make validate-example      Validate the canonical end-to-end example"
	@echo "  make validate-runs         Validate every saved run under runs/ if present"
	@echo "  make check                 Run tests and validate fixtures, examples, and saved runs"

test:
	python3 -m unittest discover -s tests

validate:
ifndef RUN
	$(error RUN is required. Usage: make validate RUN=runs/<run-name>)
endif
	python3 scripts/validate_run.py $(RUN)

validate-fixture:
	python3 scripts/validate_run.py tests/fixtures/valid-minimal-run

validate-example:
	python3 scripts/validate_run.py examples/trip-approval

validate-runs:
	@if [ ! -d runs ] || ! find runs -mindepth 1 -maxdepth 1 -type d | read _; then \
		echo "No saved runs to validate"; \
	else \
		for run in runs/*; do \
			if [ -d "$$run" ]; then python3 scripts/validate_run.py "$$run" || exit $$?; fi; \
		done; \
	fi

check: test validate-fixture validate-example validate-runs
