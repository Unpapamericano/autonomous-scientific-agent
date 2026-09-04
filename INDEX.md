# Project index

Start with the [README](README.md) for the project purpose, quick start, and
supported workflows.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Research plan](RESEARCH.md)
- [Multiple sclerosis evidence example](docs/multiple_sclerosis_summary.md)
- [Live clinical-trials monitor](docs/ms_trials_monitor.md)
- [Cloud delivery demonstrations](docs/cloud_delivery.md)
- [Mobile PWA](docs/mobile_app.md)
- [Historical development log](docs/dev-log/)
- [Changelog](CHANGELOG.md)

## Development

- Source code: `src/`
- Tests: `tests/`
- Configuration: `config/`
- Dependency and packaging configuration: `pyproject.toml`
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Common commands: `Makefile`

Run the test suite with `pytest -q`. GitHub Actions under `.github/workflows/`
is the active CI pipeline; Azure DevOps and GitLab files are demonstrations in
[`demos/cloud-pipelines/`](demos/cloud-pipelines/).
