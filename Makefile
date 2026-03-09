# Itero project Makefile
.PHONY: install test list run

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=itero --cov-report=term-missing

# Demo: run from .examples (requires copying to .itero first)
list:
	@echo "Use from your project root with .itero/ configured:"
	@echo "  itero list"
	@echo ""
	@echo "Or from this dir after: cp -r .examples .itero && cp .examples/* .itero/"
	itero list 2>/dev/null || true

run:
	@echo "Usage: itero run <workflow> <input_file>"
	@echo "Example: itero run simple-dev-tester instructions.md"
