# Generalist Data Annotator Simulator

This project simulates the work profile described in the "Generalist Data Annotator" remote job description and turns it into a realistic, production-oriented portfolio project.

## What it demonstrates

- text, image, audio, and video labeling
- data quality validation and calibration
- error detection and correction workflows
- multilingual annotation workflow (English + German)
- productivity and quality scoring
- secure handling of client data and annotation protocols
- contract gig / remote work operations model

## Business value

This project demonstrates the ability to design and manage annotation pipelines that are accurate, scalable, and audit-friendly, which is directly relevant for data annotation, QA, AI training, and digital operations roles.

## Quick start

```bash
python data_annotation_simulator/run.py
```

This generates:
- `data_annotation_simulator/output/annotation_report.json`
- `data_annotation_simulator/output/quality_dashboard.png`

## Project structure

```text
data_annotation_simulator/
├── README.md
├── data/
│   └── tasks.json
├── output/
├── run.py
├── src/
│   ├── __init__.py
│   └── simulator.py
└── __init__.py
```
