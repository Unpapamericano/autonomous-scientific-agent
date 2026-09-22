# AGENTS.md - Defense Intelligence Platform Development Guide

## Project Overview
**Defense Intelligence Analysis Platform** - Enterprise AI system for multi-source intelligence synthesis, built for BWI GmbH's Software Data Analytics division.

**Monorepo Structure**: Organized as a modular Python/Go/C++ project with integrated CI/CD, testing, and deployment automation.

---

## Dev Environment Setup

### Prerequisites
```bash
# Python 3.11+
python --version

# Go 1.21+ (for performance services)
go version

# C++ toolchain (for quantum/math modules)
cmake --version

# Git
git config user.name "Doncho"
git config user.email "doncho.ap@gmail.com"
```

### Project Navigation
```bash
# Jump to specific module
cd src/api                    # FastAPI application
cd src/services              # Business logic services
cd src/infrastructure        # Database, cache, external APIs
cd tests                     # Test suites (600+)
cd k8s                       # Kubernetes manifests
cd .github/workflows         # CI/CD pipelines
cd scripts                   # Deployment & utility scripts
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
python -m pytest tests/ -v --tb=short

# Install pre-commit hooks
pre-commit install
```

---

## Module Structure & Naming Conventions

### Main Modules

| Module | Purpose | Language | Location |
|--------|---------|----------|----------|
| **api** | FastAPI REST endpoints | Python | `src/api/` |
| **services** | Business logic layer | Python | `src/services/` |
| **domain** | Domain models & entities | Python | `src/domain/` |
| **infrastructure** | Database, cache, external APIs | Python | `src/infrastructure/` |
| **ml** | Model management & inference | Python | `src/ml/` |
| **security** | Authentication, encryption, audit | Python | `src/security/` |
| **go-service** | High-performance operations | Go | `services/go-service/` |
| **cpp-quantum** | Quantum computing module | C++ | `cpp/quantum/` |
| **cpp-math** | Mathematical optimization | C++ | `cpp/math_test/` |
| **frontend** | Web UI & dashboards | JavaScript/React | `mobile/` |

### Module Discovery
```bash
# List all Python modules
find src -name "__init__.py" | sort

# List all Go packages
find services -name "go.mod"

# Find specific service
ls -la src/services/intelligence/
ls -la src/services/ml/
ls -la src/services/security/
```

### Adding a New Module

**Python Module**:
```bash
# Create module structure
mkdir -p src/services/new_feature
touch src/services/new_feature/__init__.py
touch src/services/new_feature/service.py
touch src/services/new_feature/models.py

# Create tests
mkdir -p tests/unit/services/new_feature
touch tests/unit/services/new_feature/test_service.py
```

**Go Service**:
```bash
# Create Go package
mkdir -p services/new-service
cd services/new-service
go mod init github.com/defense-ai/new-service
touch main.go
touch go.sum
```

---

## Testing Instructions

### Test Architecture
```
tests/
├── unit/                          # Fast, isolated tests
│   ├── services/                 # Service logic tests
│   ├── domain/                   # Domain model tests
│   └── shared/                   # Utility tests
├── integration/                   # Component interaction tests
│   ├── api/                      # Endpoint tests
│   ├── services/                 # Cross-service tests
│   └── database/                 # DB integration
├── performance/                   # Load & stress tests
│   ├── api_latency.py
│   ├── throughput.py
│   └── memory_usage.py
├── security/                      # Security tests
│   ├── injection_detection.py
│   ├── encryption.py
│   └── auth.py
└── fixtures/                      # Test data
    ├── mock_data.py
    ├── test_contexts.py
    └── factories.py
```

### Running Tests

**All Tests**:
```bash
# Full suite (all tests, all modules)
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
pytest tests/ --cov=src --cov-report=term-missing

# Parallel execution (faster)
pytest tests/ -n auto
```

**Specific Test Categories**:
```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests (slower)
pytest tests/integration/ -v

# Performance tests (long-running)
pytest tests/performance/ -v -s

# Security tests
pytest tests/security/ -v

# Single test file
pytest tests/unit/services/intelligence/test_analyzer.py -v

# Single test function
pytest tests/unit/services/intelligence/test_analyzer.py::test_analyze -v
```

**Test Filtering**:
```bash
# Run tests matching a pattern
pytest -k "intelligence" -v

# Run tests for specific marker
pytest -m "slow" -v

# Skip slow tests
pytest -m "not slow" -v

# Run only tests that failed last time
pytest --lf
```

### Test-Driven Development

**Development Workflow**:
```bash
# 1. Write the test first
vim tests/unit/services/intelligence/test_new_feature.py

# 2. Run test (should fail - RED)
pytest tests/unit/services/intelligence/test_new_feature.py -v

# 3. Implement feature
vim src/services/intelligence/service.py

# 4. Run test (should pass - GREEN)
pytest tests/unit/services/intelligence/test_new_feature.py -v

# 5. Refactor
# ... improve code structure ...

# 6. Run all related tests
pytest tests/unit/services/intelligence/ -v

# 7. Run all tests before commit
pytest tests/ -v
```

### Performance Testing

```bash
# API latency test (should be <50ms)
pytest tests/performance/test_api_latency.py -v -s

# Throughput test (should handle 1000+ req/sec)
pytest tests/performance/test_throughput.py -v -s

# Memory test (should stay <4GB)
pytest tests/performance/test_memory_usage.py -v -s

# Profile a specific function
python -m cProfile -s cumulative scripts/profile_analysis.py
```

### Test Coverage Goals

```bash
# Current coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Enforce minimum coverage (fail if below 95%)
pytest tests/ --cov=src --cov-fail-under=95

# Coverage by module
pytest tests/ --cov=src.services --cov-report=term-missing
```

---

## Code Quality & Linting

### Pre-Commit Checks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run all checks
pre-commit run --all-files

# Run specific check
pre-commit run pylint --all-files
```

### Code Formatting
```bash
# Format with Black
black src/ tests/

# Check formatting (no changes)
black --check src/ tests/

# Format specific file
black src/services/intelligence/analyzer.py
```

### Linting
```bash
# Full lint check
pylint src/ tests/

# Lint specific module
pylint src/services/intelligence/

# Fix some issues automatically
autopep8 --in-place -r src/

# Check import order
isort --check-only src/
isort src/  # Fix imports
```

### Type Checking
```bash
# Check types with mypy
mypy src/

# Check specific file
mypy src/services/intelligence/analyzer.py

# Generate report
mypy src/ --html=mypy-report
```

### Complete Quality Check
```bash
# Run everything
pnpm run quality  # or: make quality

# Or manually:
black --check src/ tests/
pylint src/ tests/
mypy src/
pytest tests/ --cov=src --cov-fail-under=95
```

---

## CI/CD & GitHub Workflows

### Workflow Location
```
.github/workflows/
├── ci-cd.yml                  # Main CI/CD pipeline
├── security-scan.yml          # Security scanning
├── performance-test.yml       # Load testing
├── deploy-staging.yml         # Staging deployment
└── deploy-production.yml      # Production deployment
```

### Running Workflows Locally
```bash
# Install act (run workflows locally)
brew install act

# List available workflows
act -l

# Run specific workflow
act -j test

# Run with specific event
act push -e event.json

# Run in dry-run mode (don't actually run)
act --dry-run
```

### Manual Workflow Triggers
```bash
# Via GitHub CLI
gh workflow run ci-cd.yml

# View workflow status
gh run list

# View specific run logs
gh run view <run-id> --log

# Cancel a run
gh run cancel <run-id>
```

---

## Git Workflow & PR Guidelines

### Branch Naming Convention
```
feature/<feature-name>         # New feature
bugfix/<bug-description>       # Bug fix
hotfix/<issue-name>            # Critical fix
refactor/<component>           # Code refactoring
docs/<documentation>           # Documentation
```

### Local Development Branch
```bash
# Create feature branch
git checkout -b feature/defense-intelligence-v2

# Make changes and commit
git add src/services/intelligence/
git commit -m "feat: Add advanced conflict resolution

- Implement 5 conflict detection types
- Add resolution strategies
- Add comprehensive tests"

# Push to remote
git push origin feature/defense-intelligence-v2
```

### Pre-Commit Checklist
```bash
# 1. Format code
black src/ tests/
isort src/ tests/

# 2. Check types
mypy src/

# 3. Lint
pylint src/ tests/

# 4. Run tests
pytest tests/ -v

# 5. Check coverage
pytest tests/ --cov=src --cov-fail-under=95

# 6. Commit only if all pass!
git add .
git commit -m "[feature] Description"
```

### PR Title Format
```
[module-name] Brief description

Examples:
[intelligence] Add conflict resolution engine
[api] Implement rate limiting middleware
[security] Add prompt injection detection
[devops] Update Kubernetes deployment
[tests] Add performance benchmarks
```

### PR Description Template
```markdown
## Description
What does this PR do?

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Enhancement
- [ ] Documentation
- [ ] Breaking change

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Performance tests (if applicable)
- [ ] All tests passing

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Coverage maintained >95%
- [ ] Documentation updated
- [ ] No new warnings
- [ ] No breaking changes (unless noted)

## Related Issues
Closes #123
```

### Creating a PR
```bash
# Push your branch
git push origin feature/my-feature

# Create PR (via GitHub CLI)
gh pr create --title "[module] Description" --body "PR details"

# Or create via web UI
# https://github.com/Unpapamericano/autonomous-scientific-agent/pull/new/feature/my-feature
```

### Code Review Checklist
- [ ] Code follows project standards
- [ ] Tests are comprehensive
- [ ] Documentation is clear
- [ ] No performance regressions
- [ ] Security implications reviewed
- [ ] Breaking changes documented

---

## Development Commands Quick Reference

```bash
# Setup
python -m venv venv
pip install -r requirements-dev.txt

# Development
pytest tests/unit/ -v              # Fast feedback
pytest tests/ -v                   # Full suite
black src/ && pylint src/          # Format & lint
mypy src/                          # Type check

# Before commit
pytest tests/ --cov=src --cov-fail-under=95
black --check src/
pylint src/

# Useful shortcuts
make install                       # Install deps
make test                          # Run tests
make lint                          # Lint code
make format                        # Format code
make quality                       # All quality checks
make docker-build                  # Build image
make deploy-dev                    # Deploy to dev
```

---

## Troubleshooting

### Tests Failing
```bash
# Run with verbose output
pytest tests/ -vv

# Run with traceback
pytest tests/ -vv --tb=long

# Run with debugging
pytest tests/ -vv --pdb

# Run only failed tests
pytest --lf -v

# Run in parallel to find threading issues
pytest -n auto -v
```

### Import Errors
```bash
# Reinstall from scratch
rm -rf venv
python -m venv venv
pip install -r requirements-dev.txt

# Check Python path
python -c "import sys; print(sys.path)"

# Verify package installed
python -c "from src.services import intelligence; print(intelligence)"
```

### Git Issues
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard uncommitted changes
git checkout -- src/

# Clean up
git gc
git prune
```

---

## Resources

- **Tests**: `tests/` directory (600+ tests)
- **CI/CD**: `.github/workflows/` directory
- **Documentation**: `docs/` directory
- **Code Style**: `.pylintrc`, `pyproject.toml`
- **Type Hints**: `py.typed` marker file
- **Pre-commit**: `.pre-commit-config.yaml`

---

**Last Updated**: September 2026  
**Status**: Production-Ready  
**Maintainer**: Doncho (@Unpapamericano)
