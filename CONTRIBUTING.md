# Contributing

## Setup

Use Python 3.11 or newer:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install ".[dev]"
```

## Tests and quality

Run the test suite with:

```bash
pytest -q
```

Use Black and isort for formatting, Ruff and Pylint for static checks, and
mypy where type coverage is relevant. Keep changes focused and add or update
tests for behavior changes.

## Commits and pull requests

Use imperative, concise commit subjects such as `fix: handle empty search
results`. Open a pull request against `main` with a clear description,
testing details, and any operational or documentation impact. Keep unrelated
refactors out of feature or bug-fix pull requests.
