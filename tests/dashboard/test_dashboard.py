"""
Phase 10: Dashboard Tests

Tests for dashboard app, metrics views, and system monitoring.
"""

import pytest
from src.dashboard.app import DashboardApp, DashboardRenderer
from src.dashboard.metrics_view import MetricsView, MetricsTable, ChartData
from src.dashboard.system_status import SystemMonitor, HealthCheck


class TestDashboardApp:
    """Test dashboard application."""

    def test_dashboard_init(self):
        dashboard = DashboardApp(title="Test Dashboard")
        assert dashboard.title == "Test Dashboard"
        assert len(dashboard.reports) == 0

    def test_add_report(self):
        dashboard = DashboardApp()
        report = {
            "report_id": "test_1",
            "title": "Test Report",
            "timestamp": "2026-01-01T00:00:00",
        }
        dashboard.add_report(report)

        assert len(dashboard.reports) == 1
        assert dashboard.reports[0]["report_id"] == "test_1"

    def test_get_reports(self):
        dashboard = DashboardApp()
        for i in range(5):
            dashboard.add_report({"report_id": f"test_{i}", "title": f"Report {i}"})

        reports = dashboard.get_reports()
        assert len(reports) == 5

        reports_limit = dashboard.get_reports(limit=2)
        assert len(reports_limit) == 2

    def test_get_latest_report(self):
        dashboard = DashboardApp()
        dashboard.add_report({"report_id": "test_1"})
        dashboard.add_report({"report_id": "test_2"})

        latest = dashboard.get_latest_report()
        assert latest["report_id"] == "test_2"

    def test_get_report_by_id(self):
        dashboard = DashboardApp()
        dashboard.add_report({"report_id": "test_1", "title": "Report 1"})
        dashboard.add_report({"report_id": "test_2", "title": "Report 2"})

        report = dashboard.get_report_by_id("test_1")
        assert report["title"] == "Report 1"

    def test_update_system_status(self):
        dashboard = DashboardApp()
        status = {"status": "healthy", "cpu": 45.2}
        dashboard.update_system_status(status)

        retrieved = dashboard.get_system_status()
        assert retrieved["status"] == "healthy"
        assert "updated_at" in retrieved

    def test_get_dashboard_summary(self):
        dashboard = DashboardApp()
        dashboard.add_report({"report_id": "test_1", "title": "Report 1"})
        dashboard.update_system_status({"status": "healthy"})

        summary = dashboard.get_dashboard_summary()
        assert summary["total_reports"] == 1
        assert summary["system_status"]["status"] == "healthy"

    def test_cache_operations(self):
        dashboard = DashboardApp()
        dashboard.cache_set("key1", "value1", ttl_seconds=10)

        assert dashboard.cache_get("key1") == "value1"
        assert dashboard.cache_get("nonexistent") is None

    def test_export_dashboard(self):
        dashboard = DashboardApp()
        dashboard.add_report({"report_id": "test_1"})

        export = dashboard.export_dashboard()
        assert export["title"] == dashboard.title
        assert export["total_reports"] == 1
        assert "summary" in export


class TestDashboardRenderer:
    """Test dashboard rendering."""

    def test_render_html_homepage(self):
        dashboard = DashboardApp(title="Test Dashboard")
        dashboard.add_report({"report_id": "test_1", "title": "Report 1"})
        dashboard.update_system_status({"status": "healthy"})

        html = DashboardRenderer.render_html_homepage(dashboard)

        assert "Test Dashboard" in html
        assert "<!DOCTYPE html>" in html
        assert "Total Reports" in html

    def test_render_json_metrics(self):
        dashboard = DashboardApp()
        dashboard.add_report({"summary": {"metric1": 0.85}})

        json_str = DashboardRenderer.render_json_metrics(dashboard)
        assert "metric1" in json_str
        assert "0.85" in json_str


class TestMetricsView:
    """Test metrics visualization."""

    def test_build_rq1_chart(self):
        chart = MetricsView.build_rq1_chart(
            completion_rate=0.80,
            latency=150.0,
            coverage=50,
        )

        assert chart.title == "RQ1: Task Completion & Latency"
        assert chart.chart_type == "bar"
        assert len(chart.datasets) == 1

    def test_build_rq4_chart(self):
        chart = MetricsView.build_rq4_chart(
            precision=0.85,
            recall=0.80,
            f1=0.82,
        )

        assert chart.title == "RQ4: Contradiction Detection"
        assert len(chart.labels) == 3

    def test_build_model_comparison_chart(self):
        models = [
            {
                "model_name": "Muse",
                "task_completion_rate": 0.80,
                "evidence_accuracy_f1": 0.85,
                "contradiction_detection_f1": 0.75,
            },
            {
                "model_name": "Gemma",
                "task_completion_rate": 0.65,
                "evidence_accuracy_f1": 0.70,
                "contradiction_detection_f1": 0.60,
            },
        ]

        chart = MetricsView.build_model_comparison_chart(models)

        assert chart.title == "RQ6: Model Performance Comparison"
        assert len(chart.labels) == 2

    def test_chart_to_json(self):
        chart = MetricsView.build_rq1_chart(0.80, 150.0, 50)
        json_data = MetricsView.chart_to_json(chart)

        assert "type" in json_data
        assert json_data["type"] == "bar"
        assert "data" in json_data
        assert "labels" in json_data["data"]


class TestMetricsTable:
    """Test metrics table rendering."""

    def test_build_rq_summary_table(self):
        rq_results = {
            "RQ1": {"status": "PASS", "target": "≥70%", "actual": "80%"},
            "RQ2": {"status": "FAIL", "target": "≥85%", "actual": "75%"},
        }

        rows = MetricsTable.build_rq_summary_table(rq_results)

        assert len(rows) == 2
        assert rows[0]["RQ"] == "RQ1"
        assert rows[0]["Pass"] is True
        assert rows[1]["Pass"] is False

    def test_build_runs_table(self):
        runs = [
            {
                "run_id": "run_1",
                "config": {"test_set": "research_questions"},
                "status": "completed",
                "results_count": 15,
                "errors_count": 0,
                "start_time": "2026-01-01T00:00:00",
            },
            {
                "run_id": "run_2",
                "config": {"test_set": "contradictions"},
                "status": "running",
                "results_count": 10,
                "errors_count": 1,
                "start_time": "2026-01-02T00:00:00",
            },
        ]

        rows = MetricsTable.build_runs_table(runs)

        assert len(rows) == 2
        assert rows[0]["Run ID"] == "run_1"
        assert rows[0]["Results"] == 15


class TestSystemMonitor:
    """Test system monitoring."""

    def test_monitor_init(self):
        monitor = SystemMonitor(cpu_threshold=80.0, memory_threshold=85.0)
        assert monitor.cpu_threshold == 80.0
        assert monitor.memory_threshold == 85.0

    def test_get_system_metrics(self):
        monitor = SystemMonitor()
        metrics = monitor.get_system_metrics()

        assert 0 <= metrics.cpu_percent <= 100
        assert 0 <= metrics.memory_percent <= 100
        assert metrics.memory_used_gb >= 0
        assert metrics.status in ["healthy", "warning", "critical", "unknown"]

    def test_metrics_history(self):
        monitor = SystemMonitor()
        monitor.get_system_metrics()
        monitor.get_system_metrics()

        assert len(monitor.metrics_history) == 2

    def test_get_metrics_summary(self):
        monitor = SystemMonitor()
        monitor.get_system_metrics()

        summary = monitor.get_metrics_summary()
        assert summary["total_samples"] > 0
        assert "average_cpu" in summary
        assert "average_memory" in summary

    def test_to_dict(self):
        monitor = SystemMonitor()
        metrics_dict = monitor.to_dict()

        assert "cpu_percent" in metrics_dict
        assert "memory_percent" in metrics_dict
        assert "status" in metrics_dict


class TestHealthCheck:
    """Test health checks."""

    def test_health_check_init(self):
        hc = HealthCheck()
        assert len(hc.checks) == 0

    def test_add_check(self):
        hc = HealthCheck()

        def dummy_check():
            return {"status": "healthy", "details": "All good"}

        hc.add_check("dummy", dummy_check)
        assert "dummy" in hc.checks

    def test_run_checks(self):
        hc = HealthCheck()

        def dummy_check():
            return {"status": "healthy"}

        hc.add_check("dummy", dummy_check)
        results = hc.run_checks()

        assert "system" in results
        assert "dummy" in results
        assert results["dummy"]["status"] == "healthy"

    def test_get_health_status(self):
        hc = HealthCheck()

        def check_healthy():
            return {"status": "healthy"}

        hc.add_check("test", check_healthy)
        status = hc.get_health_status()

        assert status in ["healthy", "warning", "critical", "error"]
