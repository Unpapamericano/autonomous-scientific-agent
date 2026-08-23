# PHASE 10: DASHBOARD & UI

## Overview

Phase 10 provides a **web-based dashboard** for visualizing evaluation results, system metrics, and agent performance. Built with lightweight Python backend components ready for Flask/Streamlit deployment.

**Status**: ✅ COMPLETE
**Tests**: 26 new dashboard tests (all passing), 168 total passing across all phases
**Components**: Dashboard app, metrics visualization, system monitoring

---

## What Was Built

### 1. Dashboard Application (`src/dashboard/app.py`)

**DashboardApp** — In-memory dashboard backend:

```python
dashboard = DashboardApp(title="Autonomous Scientific Agent")

# Add evaluation reports
dashboard.add_report({
    "report_id": "rq1_001",
    "title": "RQ1 Task Completion",
    "summary": {"completion_rate": 0.80, "latency": 150},
})

# System status
dashboard.update_system_status({"status": "healthy", "cpu": 45.2})

# Query reports
latest = dashboard.get_latest_report()
by_id = dashboard.get_report_by_id("rq1_001")
summary = dashboard.get_dashboard_summary()

# Export
export_dict = dashboard.export_dashboard()  # Full state as dict
```

**DashboardRenderer** — Renders views in multiple formats:

```python
renderer = DashboardRenderer()

# HTML homepage
html = renderer.render_html_homepage(dashboard)
# → HTML page with metrics, status, recent reports

# JSON metrics
json_metrics = renderer.render_json_metrics(dashboard)
# → JSON for API consumption

# Individual report
json_report = renderer.render_json_report(report)
```

**Features**:
- Report CRUD (add, query, export)
- System status tracking
- Caching with TTL
- Metrics aggregation
- HTML homepage rendering
- JSON export for APIs

### 2. Metrics Visualization (`src/dashboard/metrics_view.py`)

**MetricsView** — Chart builders for each RQ:

```python
view = MetricsView()

# RQ1 chart
chart_rq1 = view.build_rq1_chart(
    completion_rate=0.80,
    latency=150.0,
    coverage=50,
)
# → ChartData with title, type="bar", labels, datasets

# RQ4 contradiction detection
chart_rq4 = view.build_rq4_chart(precision=0.85, recall=0.80, f1=0.82)

# RQ5 security
chart_rq5 = view.build_rq5_chart(attack_success=0.05, false_positive=0.03)

# RQ7 quality-cost Pareto frontier
chart_rq7 = view.build_rq7_pareto_chart(configurations=[
    {"quantization": "4-bit", "hardware": "RTX4090", "quality_score": 0.85, "cost": 0.50},
    {"quantization": "8-bit", "hardware": "A100", "quality_score": 0.92, "cost": 2.00},
])

# RQ6 model comparison
chart_rq6 = view.build_model_comparison_chart(models=[
    {"model_name": "Muse", "task_completion_rate": 0.80, ...},
    {"model_name": "Gemma", "task_completion_rate": 0.65, ...},
])

# Convert to Chart.js JSON format
json_chart = MetricsView.chart_to_json(chart_rq1)
```

**ChartData** — Reusable chart format:
- title, chart_type (bar/line/pie/scatter)
- labels, datasets
- options (Chart.js format)

**MetricsTable** — Tabular display:

```python
table = MetricsTable()

# RQ results table
rq_table = table.build_rq_summary_table(rq_results)
# → List of dicts with RQ, Status, Target, Actual, Pass

# Runs table
runs_table = table.build_runs_table(runs)
# → List of dicts with Run ID, Test Set, Status, Results, Errors
```

### 3. System Monitoring (`src/dashboard/system_status.py`)

**SystemMonitor** — Resource tracking:

```python
monitor = SystemMonitor(cpu_threshold=80.0, memory_threshold=85.0)

# Get current metrics
metrics = monitor.get_system_metrics()
# → SystemMetrics: cpu%, memory%, disk%, status, timestamp

# Summary of recent metrics
summary = monitor.get_metrics_summary()
# → {"average_cpu": 45.2, "average_memory": 62.1, "current_status": "healthy"}

# Export
metrics_dict = monitor.to_dict()
```

**SystemMetrics** — Resource snapshot:
- cpu_percent, memory_percent, disk_percent (0-100)
- memory_used_gb, memory_available_gb
- disk_used_gb, disk_available_gb
- status: "healthy" | "warning" | "critical"
- timestamp: ISO 8601

**HealthCheck** — Custom health checks:

```python
hc = HealthCheck()

# Register checks
def check_database():
    return {"status": "healthy", "details": "DB connected"}

def check_cache():
    return {"status": "warning", "details": "Cache hit rate low"}

hc.add_check("database", check_database)
hc.add_check("cache", check_cache)

# Run all checks
results = hc.run_checks()
# → {"system": {...}, "database": {...}, "cache": {...}}

# Overall status
status = hc.get_health_status()  # "warning" (highest severity)
```

---

## Dashboard Features

### Views

1. **Homepage** (`/`)
   - System status badge (healthy/warning/critical)
   - Total reports count
   - Key metrics summary (avg values across runs)
   - Latest report card
   - HTML rendering

2. **Metrics** (`/metrics`)
   - Charts for each RQ (RQ1-RQ7)
   - Model comparison chart (RQ6)
   - Quality-cost Pareto frontier (RQ7)
   - Time-series trend charts
   - Chart.js JSON format for front-end

3. **Reports** (`/reports`)
   - List of all evaluation reports
   - Filter by status, date, test set
   - Detailed report view with full metrics

4. **System Status** (`/health`)
   - CPU, memory, disk usage
   - Health check results
   - System load history
   - Alert thresholds

5. **Export** (`/export`)
   - Full dashboard state as JSON
   - Individual report JSON
   - CSV metrics summary

---

## Integration with Phase 9 & Phase 11

**Phase 9** generates:
- EvaluationReport with RQ results
- Metrics data (precision, F1, etc.)

**Dashboard (Phase 10)** displays:
- Reports via DashboardApp.add_report()
- Metrics via MetricsView charts
- System status via SystemMonitor

**Phase 11** will:
1. Run evaluations using Phase 9 framework
2. Generate reports
3. Add to dashboard: `dashboard.add_report(report)`
4. Serve via Flask: `render_html_homepage(dashboard)`

### Example Integration

```python
# Phase 11 evaluation run
from src.evaluation import get_evaluator, BenchmarkDatasets, MetricsCalculator
from src.evaluation.report_generator import ReportGenerator
from src.dashboard.app import DashboardApp

# Setup
evaluator = get_evaluator()
report_gen = ReportGenerator()
dashboard = DashboardApp()

# Run RQ1 evaluation
config = EvaluationConfig("RQ1_Completion", "Test task completion", "research_questions")
run = evaluator.create_run(config)
# ... run tests ...
metrics = calc.calculate_rq1(...)
report = report_gen.generate_rq1_report(...)

# Add to dashboard
dashboard.add_report(report.to_dict())
dashboard.update_system_status({"status": "healthy"})

# Export or serve
print(dashboard.export_dashboard())
```

---

## Testing

**26 tests** cover:
- Dashboard CRUD operations
- Report management
- Metrics chart building
- Tables formatting
- System monitoring
- Health checks
- HTML/JSON rendering
- Export/serialization

**Run tests**:
```bash
pytest tests/dashboard/test_dashboard.py -v
# 26 passed
```

---

## Deployment Ready

### Flask Deployment

```python
from flask import Flask, jsonify
from src.dashboard.app import DashboardApp, DashboardRenderer

app = Flask(__name__)
dashboard = DashboardApp()

@app.route("/")
def homepage():
    html = DashboardRenderer.render_html_homepage(dashboard)
    return html

@app.route("/api/metrics")
def metrics():
    return jsonify(dashboard.get_metrics_summary())

@app.route("/api/health")
def health():
    return jsonify(dashboard.get_system_status())

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
```

### Streamlit Deployment

```python
import streamlit as st
from src.dashboard.app import DashboardApp, DashboardRenderer
from src.dashboard.metrics_view import MetricsView

dashboard = DashboardApp()

st.title(dashboard.title)
summary = dashboard.get_dashboard_summary()

col1, col2, col3 = st.columns(3)
col1.metric("Reports", summary["reports_count"])
col2.metric("Status", summary["system_status"]["status"])
col3.metric("Created", summary["created_at"][:10])

# Charts
metrics_view = MetricsView()
rq1_chart = metrics_view.build_rq1_chart(...)
st.json(MetricsView.chart_to_json(rq1_chart))
```

---

## Limitations (Phase 10)

- **Backend only** — no actual Flask/Streamlit app (Phase 11+ deployment)
- **In-memory storage** — no persistent database (add later)
- **No authentication** — add before production deployment
- **No real-time updates** — polling or WebSocket for live metrics
- **Chart.js format only** — add support for Plotly/D3 later

---

## Next: Phase 11 — Benchmarking & Experiments

Run actual evaluations on 15 research questions, benchmark models, generate reports via dashboard.
