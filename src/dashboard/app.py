"""
Phase 10: Dashboard Application

Web-based dashboard for viewing evaluation results, system status, and metrics.
Built with Flask for lightweight deployment.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import uuid

import polars as pl

logger = logging.getLogger(__name__)


class DashboardApp:
    """
    Dashboard application for displaying agent results and metrics.
    """

    def __init__(self, title: str = "Autonomous Scientific Agent Dashboard"):
        self.title = title
        self.reports = []
        self.studies = {}
        self.results = []
        self.system_status = {}
        self.cache = {}
        self.created_at = datetime.utcnow().isoformat()

    def add_report(self, report_data: Dict[str, Any]) -> None:
        """Add an evaluation report to the dashboard."""
        report_data["added_at"] = datetime.utcnow().isoformat()
        self.reports.append(report_data)
        logger.info(f"Added report: {report_data.get('title', 'untitled')}")

    def get_reports(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get reports, optionally limited."""
        if limit:
            return self.reports[-limit:]
        return self.reports

    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """Get the most recent report."""
        return self.reports[-1] if self.reports else None

    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report by ID."""
        for report in self.reports:
            if report.get("report_id") == report_id:
                return report
        return None

    def register_study(
        self,
        title: str,
        description: str = "",
        study_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Register a study that can receive observations and result records."""
        if not title.strip():
            raise ValueError("Study title must not be empty")
        resolved_id = study_id or str(uuid.uuid4())[:8]
        if resolved_id in self.studies:
            raise ValueError(f"Study '{resolved_id}' already exists")
        study = {
            "study_id": resolved_id,
            "title": title,
            "description": description,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
        }
        self.studies[resolved_id] = study
        return study.copy()

    def get_studies(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List registered studies, optionally filtered by status."""
        studies = list(self.studies.values())
        if status is not None:
            studies = [study for study in studies if study["status"] == status]
        return [study.copy() for study in studies]

    def add_result(self, study_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Add an observation or analysis result to a registered study."""
        if study_id not in self.studies:
            raise KeyError(f"Study '{study_id}' not found")
        if not result:
            raise ValueError("Result must contain at least one field")
        record = {
            "result_id": str(uuid.uuid4())[:8],
            "study_id": study_id,
            "recorded_at": datetime.utcnow().isoformat(),
            **result,
        }
        self.results.append(record)
        return record.copy()

    def get_study_results(self, study_id: str) -> List[Dict[str, Any]]:
        """Return all observations recorded for a study."""
        if study_id not in self.studies:
            raise KeyError(f"Study '{study_id}' not found")
        return [result.copy() for result in self.results if result["study_id"] == study_id]

    def get_study_summary(self, study_id: str) -> Dict[str, Any]:
        """Summarize numeric study results using Polars."""
        if study_id not in self.studies:
            raise KeyError(f"Study '{study_id}' not found")
        results = self.get_study_results(study_id)
        numeric_columns = {}
        for result in results:
            for key, value in result.items():
                if key not in {"result_id", "study_id", "recorded_at"}:
                    numeric_columns.setdefault(key, []).append(value)

        metrics = {}
        for column, values in numeric_columns.items():
            frame = pl.DataFrame({"value": values}).with_columns(
                pl.col("value").cast(pl.Float64, strict=False)
            ).drop_nulls()
            if not frame.is_empty():
                metrics[column] = {
                    "average": round(frame["value"].mean(), 12),
                    "minimum": frame["value"].min(),
                    "maximum": frame["value"].max(),
                    "observations": frame.height,
                }
        return {
            "study": self.studies[study_id].copy(),
            "result_count": len(results),
            "metrics": metrics,
        }

    def update_system_status(self, status: Dict[str, Any]) -> None:
        """Update system status information."""
        status["updated_at"] = datetime.utcnow().isoformat()
        self.system_status = status
        logger.info(f"Updated system status: {status.get('status', 'unknown')}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        if not self.system_status:
            return {
                "status": "unknown",
                "updated_at": datetime.utcnow().isoformat(),
            }
        return self.system_status

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary for homepage."""
        latest_report = self.get_latest_report()
        system_status = self.get_system_status()

        return {
            "title": self.title,
            "created_at": self.created_at,
            "total_reports": len(self.reports),
            "total_studies": len(self.studies),
            "total_results": len(self.results),
            "latest_report": latest_report,
            "system_status": system_status,
            "reports_count": len(self.reports),
            "studies_count": len(self.studies),
            "results_count": len(self.results),
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics across reports."""
        if not self.reports:
            return {"total_reports": 0, "metrics": {}}

        # Aggregate metrics
        all_metrics = {}
        for report in self.reports:
            summary = report.get("summary", {})
            for key, value in summary.items():
                if key not in all_metrics:
                    all_metrics[key] = []
                if isinstance(value, (int, float)):
                    all_metrics[key].append(value)

        # Calculate averages
        metric_stats = {}
        for key, values in all_metrics.items():
            if values:
                metric_stats[key] = {
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }

        return {
            "total_reports": len(self.reports),
            "metrics": metric_stats,
        }

    def cache_set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Cache a value with TTL."""
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow().timestamp() + ttl_seconds,
        }

    def cache_get(self, key: str) -> Optional[Any]:
        """Get a cached value if not expired."""
        if key not in self.cache:
            return None

        cached = self.cache[key]
        if datetime.utcnow().timestamp() > cached["expires_at"]:
            del self.cache[key]
            return None

        return cached["value"]

    def export_dashboard(self) -> Dict[str, Any]:
        """Export entire dashboard state as JSON."""
        return {
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": datetime.utcnow().isoformat(),
            "total_reports": len(self.reports),
            "reports": self.reports,
            "studies": list(self.studies.values()),
            "results": self.results,
            "system_status": self.system_status,
            "summary": self.get_dashboard_summary(),
            "metrics_summary": self.get_metrics_summary(),
        }


class DashboardRenderer:
    """
    Renders dashboard views (HTML/JSON).
    """

    @staticmethod
    def render_html_homepage(dashboard: DashboardApp) -> str:
        """Render homepage HTML."""
        summary = dashboard.get_dashboard_summary()
        metrics = dashboard.get_metrics_summary()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{dashboard.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        .status-good {{ color: #28a745; font-weight: bold; }}
        .status-warning {{ color: #ffc107; font-weight: bold; }}
        .status-bad {{ color: #dc3545; font-weight: bold; }}
        .metric {{ margin: 15px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #007bff; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .recent-reports {{ margin-top: 30px; }}
        .report-card {{ margin: 10px 0; padding: 15px; background: #f0f8ff; border: 1px solid #007bff; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{dashboard.title}</h1>
        
        <div class="metric">
            <strong>System Status:</strong>
            <span class="{('status-good' if summary['system_status'].get('status') == 'healthy' else 'status-warning')}">{summary['system_status'].get('status', 'unknown').upper()}</span>
        </div>
        
        <div class="metric">
            <strong>Total Reports:</strong>
            <div class="metric-value">{summary['reports_count']}</div>
        </div>
        
        <div class="metric">
            <strong>Key Metrics:</strong>
"""

        for metric_name, stats in metrics.get("metrics", {}).items():
            avg = stats["average"]
            if isinstance(avg, float):
                avg = f"{avg:.2%}" if 0 <= avg <= 1 else f"{avg:.2f}"
            html += f"<div>- {metric_name}: {avg} (avg of {stats['count']} runs)</div>"

        html += """
        </div>

        <div class="recent-reports">
            <h2>Studies and Research Results</h2>
"""

        if dashboard.studies:
            for study in dashboard.get_studies():
                result_count = len(dashboard.get_study_results(study["study_id"]))
                html += f"""
            <div class="report-card">
                <strong>{study['title']}</strong>
                <p>ID: {study['study_id']} | Status: {study['status']} | Results: {result_count}</p>
                <p>{study['description']}</p>
            </div>
"""
        else:
            html += "<p>No studies registered.</p>"

        html += """
        </div>
        
        <div class="recent-reports">
            <h2>Recent Reports</h2>
"""

        latest = dashboard.get_latest_report()
        if latest:
            html += f"""
            <div class="report-card">
                <strong>{latest.get('title', 'Untitled')}</strong>
                <p>ID: {latest.get('report_id', 'N/A')}</p>
                <p>Generated: {latest.get('timestamp', 'N/A')}</p>
            </div>
"""

        html += """
        </div>
    </div>
</body>
</html>
"""
        return html

    @staticmethod
    def render_json_metrics(dashboard: DashboardApp) -> str:
        """Render metrics as JSON."""
        return json.dumps(dashboard.get_metrics_summary(), indent=2)

    @staticmethod
    def render_json_report(report: Dict[str, Any]) -> str:
        """Render a report as JSON."""
        return json.dumps(report, indent=2)


def get_dashboard() -> DashboardApp:
    """Get a dashboard instance."""
    return DashboardApp()


def get_renderer() -> DashboardRenderer:
    """Get a dashboard renderer instance."""
    return DashboardRenderer()
