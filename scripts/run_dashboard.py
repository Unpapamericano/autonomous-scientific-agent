#!/usr/bin/env python3
"""Minimal dashboard entrypoint for local execution."""

import argparse
import json
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.app import DashboardApp, DashboardRenderer
from src.dashboard.system_status import SystemMonitor


DASHBOARD = DashboardApp()
DASHBOARD.update_system_status(
    {
        "status": "degraded",
        "backend": "compatibility-fallback",
        "message": "Model backend unavailable; dashboard is running in demo mode.",
    }
)
DASHBOARD.add_report(
    {
        "title": "Startup health report",
        "report_id": "startup-report",
        "summary": {"status": "degraded"},
        "timestamp": datetime.utcnow().isoformat(),
    }
)


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """Serve the dashboard HTML and basic API endpoints."""

    server_version = "AutonomousScientificAgent/0.10"

    def do_GET(self):
        if self.path == "/health":
            payload = json.dumps({"status": "ok", "dashboard": DASHBOARD.get_dashboard_summary()}).encode("utf-8")
            self._send_json(payload)
            return

        if self.path == "/api/dashboard":
            payload = json.dumps(DASHBOARD.export_dashboard(), indent=2).encode("utf-8")
            self._send_json(payload)
            return

        if self.path == "/api/system":
            payload = json.dumps({"system_status": DASHBOARD.get_system_status(), "metrics": SystemMonitor().to_dict()}).encode("utf-8")
            self._send_json(payload)
            return

        html = DashboardRenderer.render_html_homepage(DASHBOARD).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def _send_json(self, payload: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Autonomous Scientific Agent dashboard locally.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind to.")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on.")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), DashboardRequestHandler)
    print(f"Dashboard running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
