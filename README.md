# Autonomous Scientific Research Agent

![Portfolio banner](visuals/portfolio_banner.png)

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Docker CI](https://github.com/Unpapamericano/autonomous-scientific-agent/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Unpapamericano/autonomous-scientific-agent/actions/workflows/docker-image.yml)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Work in progress:** this project is an experimental, local-first research
> platform. Its analyses and visualizations are information and hypotheses,
> not final scientific conclusions, medical advice, or treatment recommendations.

## What this project does

The Autonomous Scientific Research Agent helps turn a research question into a
traceable workflow:

```text
Question → Search → Extract → Analyze → Verify → Explain
```

It combines local AI, scientific literature search, reproducible data analysis,
evidence tracking, safe tool execution, and professional visual reporting.

## Why it is useful

- **Local-first:** run supported workflows with Ollama and open-source models.
- **Evidence-aware:** connect claims to recognized sources and label uncertainty.
- **Reproducible:** use Python, Polars, tests, Docker, and structured artifacts.
- **Adaptive:** inspect the most relevant evidence instead of processing everything equally.
- **Production-minded:** use quality gates, telemetry, security checks, and CI.
- **Understandable:** generate reports, dashboards, diagrams, and PDFs for technical
  and non-technical audiences.

## Core capabilities

| Capability | What it provides |
|---|---|
| Literature search | PubMed, arXiv, and OpenAlex integrations |
| Evidence synthesis | Claims, source links, contradiction-aware review |
| Adaptive analysis | Fast, balanced, and deep evidence inspection modes |
| Model routing | Budget- and task-aware selection with high-risk confirmation signals |
| AI workflows | Ideation, experimentation, write-up, and review agents |
| Data analysis | Polars-based scientific summaries and visualizations |
| Context continuity | Searchable notes for decisions and open questions across sessions |
| Safe execution | Sandboxed Python tooling and security checks |
| Delivery governance | Discover → Design → Build → Validate → Release → Operate → Evolve |
| Reporting | Dashboards, images, Markdown summaries, and PDFs |

## Quick start

### 1. Install

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install ".[dev]"
```

### 2. Run a local research workflow

Start Ollama separately, then configure the local model:

```powershell
$env:MUSE_BACKEND="ollama"
$env:MUSE_MODEL_ID="qwen3:8b"
$env:OLLAMA_HOST="http://127.0.0.1:11434"
python scripts/launch_multiagent.py --task "Compare evidence for two scientific methods."
```

The workflow writes a report and structured summary under the configured results
workspace.

### 3. Generate visuals

```bash
python scripts/generate_scientific_visuals.py
python scripts/generate_ms_evidence_visuals.py
python scripts/generate_loop_engineering_visual.py
python scripts/generate_enterprise_workflow_visual.py
```

### 4. Run tests

```bash
pytest -q
```

## Engineering workflow

The project uses three connected loops:

```text
Enterprise delivery:
DISCOVER → DESIGN → BUILD → VALIDATE → RELEASE → OPERATE → EVOLVE

Loop engineering:
DEFINE → BUILD → MEASURE → REVIEW → ITERATE

Research:
PLAN → SEARCH → INSPECT → ANALYZE → CITE → REVIEW
```

Each loop is designed to make assumptions, evidence, quality, cost, and
uncertainty visible before an artifact is released.

Key implementations:

- `src/research/adaptive_analysis.py`
- `src/research/loop_engineering.py`
- `src/research/enterprise_delivery.py`
- `src/research/source_governance.py`

## Multiple sclerosis example

The repository includes an exploratory MS evidence project demonstrating how
the workflow can organize:

- multifactorial disease mechanisms
- genetic and environmental risk factors
- standard disease-modifying therapies
- HSCT, CAR T-cell, and MSC research
- possible solution paths and evidence maturity

This example is deliberately conservative. Correlation is not causation;
experimental research is not established treatment; and no visual in this
repository is a diagnosis, cure claim, or clinical recommendation.

Recognized sources are registered in `data/ms_source_registry.json`, including
WHO, NINDS/NIH, PubMed/MEDLINE, Cochrane, ECTRIMS, ClinicalTrials.gov, FDA, and
EMA. Claims should be tied to sources and labeled as established evidence,
association, hypothesis, experimental, or speculation.

## Project map

```text
src/
  core/       inference, orchestration, tools
  research/   literature APIs, adaptive analysis, delivery governance
  rag/        retrieval, documents, evidence graphs
  security/   injection detection and input sanitization
  evaluation/ metrics, benchmarks, reports
  dashboard/  metrics and monitoring views

data/         source registries and analysis data
docs/         architecture, methods, and project explanations
scripts/      runnable workflows and visual generators
tests/        unit, integration, security, and dashboard tests
visuals/      generated charts, diagrams, and PDFs
```

## Documentation

- [Final release summary](docs/final_release_summary.md)
- [Adaptive analysis roadmap](docs/adaptive_analysis_roadmap.md)
- [Loop engineering](docs/loop_engineering.md)
- [Enterprise AI delivery workflow](docs/enterprise_ai_delivery_workflow.md)
- [Multiple sclerosis evidence summary](docs/multiple_sclerosis_summary.md)
- [Live MS trials monitor](docs/ms_trials_monitor.md)
- [Android and iOS mobile app](docs/mobile_app.md)
- [Contributor guide](CONTRIBUTING.md)
- [Architecture](ARCHITECTURE.md)
- [Research methodology](RESEARCH.md)

## Docker

The Docker image is built automatically for pushes and pull requests to
`main`. To build locally:

```bash
docker build --target app --tag autonomous-scientific-agent:ci .
```

The repository uses `config/` consistently for configuration files. Docker CI
is defined in `.github/workflows/docker-image.yml`.

## Cloud delivery skills demonstration

The repository includes a validation-focused enterprise cloud track:

- Cloud pipeline demonstrations: [`demos/cloud-pipelines/`](demos/cloud-pipelines/)
- PowerShell delivery checks: `ops/Validate-Delivery.ps1`
- Entra ID authentication guidance and least-privilege notes:
  `docs/cloud_delivery.md`

These templates validate code and infrastructure without provisioning cloud
resources or storing credentials. See [cloud delivery documentation](docs/cloud_delivery.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, style, commit,
and pull-request guidance.

## License

MIT. See [LICENSE](LICENSE).
