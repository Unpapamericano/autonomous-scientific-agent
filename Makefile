.PHONY: help install install-dev test test-unit test-integration test-all lint format clean setup run-agent run-dashboard benchmark docs

help:
	@echo "Autonomous Scientific Research Agent - Build Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install             Install base dependencies"
	@echo "  make install-dev         Install dev + base dependencies"
	@echo "  make setup               Initialize database & config"
	@echo ""
	@echo "Testing:"
	@echo "  make test                Run all tests"
	@echo "  make test-unit           Run unit tests only"
	@echo "  make test-integration    Run integration tests only"
	@echo "  make test-security       Run security tests only"
	@echo "  make test-all            Run all tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                Run linters (pylint, ruff)"
	@echo "  make format              Format code (black, isort)"
	@echo "  make clean               Remove cache & build files"
	@echo ""
	@echo "Running:"
	@echo "  make run-agent           Run agent interactively"
	@echo "  make run-dashboard       Start dashboard (http://localhost:5000)"
	@echo "  make benchmark           Run Phase 11 benchmarks"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs                Build Sphinx documentation"
	@echo ""

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

setup:
	python scripts/init_db.py
	cp config/config.yaml.example config/config.yaml
	@echo "Setup complete! Edit config/config.yaml with your settings."

test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/unit/ -v --tb=short

test-integration:
	pytest tests/integration/ -v --tb=short

test-security:
	pytest tests/security/ -v --tb=short

test-evaluation:
	pytest tests/evaluation/ -v --tb=short

test-dashboard:
	pytest tests/dashboard/ -v --tb=short

test-all:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

lint:
	pylint src/ --exit-zero
	ruff check src/

format:
	black src/ tests/ scripts/
	isort src/ tests/ scripts/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/
	rm -rf build/ dist/ *.egg-info/

run-agent:
	python -m src.core.orchestration

run-dashboard:
	python scripts/run_dashboard.py --port 5000

benchmark:
	python scripts/benchmark.py --all

docs:
	sphinx-build -b html docs/ docs/_build/

.DEFAULT_GOAL := help
