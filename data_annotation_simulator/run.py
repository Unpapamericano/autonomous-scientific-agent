from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data_annotation_simulator.src.simulator import AnnotationSimulator


ROOT = Path(__file__).resolve().parent


def main() -> int:
    task_file = ROOT / "data" / "tasks.json"
    output_dir = ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    simulator = AnnotationSimulator(task_file)
    summary = simulator.run()

    report_path = output_dir / "annotation_report.json"
    dashboard_path = output_dir / "quality_dashboard.png"

    AnnotationSimulator.save_json_report(summary, report_path)
    AnnotationSimulator.save_dashboard(summary, dashboard_path)

    print(f"Generated annotation report: {report_path}")
    print(f"Generated quality dashboard: {dashboard_path}")
    print(f"Overall accuracy: {summary['metrics']['accuracy']:.2%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
