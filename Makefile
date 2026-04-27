.PHONY: help test validate validate-fixture validate-example check

help:
	@echo "Available commands:"
	@echo "  make test                  Run validator unit tests"
	@echo "  make validate RUN=<path>   Validate a saved run directory"
	@echo "  make validate-fixture      Validate the canonical test fixture"
	@echo "  make validate-example      Validate the canonical end-to-end example"
	@echo "  make check                 Run tests and validate fixtures and examples"

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

check: test validate-fixture validate-example
