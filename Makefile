.PHONY: help install install-dev test test-cov lint format format-check type-check clean build run

PYTHON := python3
PIP := pip3

help:
	@echo "Available targets:"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install with development dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run all linting checks"
	@echo "  format       - Format code with black and ruff"
	@echo "  format-check - Check code formatting without modifying"
	@echo "  type-check   - Run mypy type checking"
	@echo "  clean        - Remove build artifacts"
	@echo "  build        - Build the package"
	@echo "  run          - Run the password generator (use ARGS='...' for arguments)"

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

test:
	pytest tests/

test-cov:
	pytest --cov=password_generator --cov-report=term-missing --cov-report=html tests/

lint:
	ruff check src tests

format:
	black src tests
	ruff check --fix src tests

format-check:
	black --check src tests
	ruff check src tests

type-check:
	mypy src

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

build:
	$(PYTHON) -m build

run:
	passgen $(ARGS)

smoke-test: install
	passgen --help
	passgen --dictionary "apple,banana" --max-permutations 10 --output /tmp/test_passwords.txt
	@echo "Smoke test complete. Check /tmp/test_passwords.txt"
