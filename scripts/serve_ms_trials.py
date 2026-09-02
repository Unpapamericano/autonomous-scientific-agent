"""Serve a live-refreshing MS trials page from ClinicalTrials.gov."""

import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.research.clinical_trials import ClinicalTrialsClient, render_ms_trials_page


class TrialsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if urlparse(self.path).path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        client = ClinicalTrialsClient()
        try:
            page = render_ms_trials_page(client.search_ms_trials())
        finally:
            client.close()
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8765), TrialsHandler)
    print("MS trials monitor: http://127.0.0.1:8765")
    server.serve_forever()


if __name__ == "__main__":
    main()
