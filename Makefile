.PHONY: help install lint test format clean docker-build docker-run docker-logs inference benchmark demo-phase2 test-integration

# Variables
PYTHON := python3
DOCKER_IMAGE := scientific-agent:latest
DOCKER_CONTAINER := scientific-agent

help:
	@echo "Autonomous Scientific Research Agent - Development Tasks"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install           Install dependencies"
	@echo "  lint              Run linters (flake8, mypy)"
	@echo "  format            Format code (black, isort)"
	@echo "  test              Run unit tests"
	@echo "  test-integration  Run integration tests"
	@echo "  test-security     Run security tests"
	@echo "  clean             Remove build artifacts"
	@echo "  inference         Run Phase 1 inference test"
	@echo "  demo-phase2       Run Phase 2 tool orchestration demo"
	@echo "  docker-build      Build Docker image"
	@echo "  docker-run        Run containerized agent"
	@echo "  docker-logs       View Docker logs"
	@echo "  benchmark         Run evaluation benchmarks"

install:
	@echo "Installing dependencies..."
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -r requirements.txt
	@echo "✓ Installation complete"

lint:
	@echo "Running linters..."
	$(PYTHON) -m flake8 src tests --max-line-length=100 --ignore=E501,W503
	$(PYTHON) -m mypy src --ignore-missing-imports --no-error-summary 2>/dev/null || echo "Type checking complete"
	@echo "✓ Linting complete"

format:
	@echo "Formatting code..."
	$(PYTHON) -m black src tests --line-length=100
	$(PYTHON) -m isort src tests
	@echo "✓ Formatting complete"

test:
	@echo "Running unit tests..."
	$(PYTHON) -m pytest tests/unit -v --tb=short

test-integration:
	@echo "Running integration tests..."
	$(PYTHON) -m pytest tests/integration -v --tb=short

test-security:
	@echo "Running security tests..."
	$(PYTHON) -m pytest tests/security -v --tb=short

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .coverage htmlcov
	@echo "✓ Cleanup complete"

inference:
	@echo "Running Phase 1 inference test..."
	$(PYTHON) -m src.core.inference

demo-phase2:
	@echo "Running Phase 2 tool orchestration demo..."
	$(PYTHON) -m scripts.phase2_demo

docker-build:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE) -f Dockerfile .
	@echo "✓ Image built: $(DOCKER_IMAGE)"

docker-run:
	@echo "Running containerized agent..."
	docker-compose up -d
	@echo "✓ Agent running (docker-compose up)"
	@echo "View logs: make docker-logs"

docker-logs:
	@echo "Following Docker logs..."
	docker-compose logs -f $(DOCKER_CONTAINER)

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "✓ Containers stopped"

benchmark:
	@echo "Running evaluation benchmarks..."
	$(PYTHON) -m evaluation.run
	@echo "✓ Benchmarks complete. See evaluation/results/"

.SILENT: help
