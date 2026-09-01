from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = ROOT / "docs" / "multiple_sclerosis_summary.md"
DATA_PATH = ROOT / "data" / "ms_evidence_summary.json"


def quick_summary() -> dict:
    if not DATA_PATH.exists():
        raise FileNotFoundError("Run scripts/generate_ms_evidence_visuals.py first.")
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def print_summary() -> None:
    data = quick_summary()
    print("MS EVIDENCE SUMMARY")
    print("=" * 24)
    print(f"Core mechanism: {data['cause_model']['core_mechanism']}")
    print("Major triggers:", ", ".join(data['cause_model']['environmental_triggers']))
    print()
    print("Risk factor evidence (qualitative):")
    for item in data["risk_factors"]:
        print(f"- {item['name']}: {item['score']}/10 ({item['note']})")
    print()
    print("Therapy maturity vs benefit:")
    for item in data["therapies"]:
        print(f"- {item['name']}: evidence={item['evidence_maturity']}/10, benefit={item['potential_benefit']}/10")
    print()
    print("Interpretation: there is no universal cure yet; DMTs are established, HSCT is cure-like for selected severe cases, and CAR T / MSC remain experimental.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Short tool for summarizing current evidence on multiple sclerosis causes and treatments.")
    parser.add_argument("--print", action="store_true", help="Print the evidence summary to the terminal")
    parser.add_argument("--generate-visuals", action="store_true", help="Generate the visuals with matplotlib")
    args = parser.parse_args()

    if args.generate_visuals:
        import subprocess
        subprocess.run(["python", str(ROOT / "scripts" / "generate_ms_evidence_visuals.py")], check=True)

    if args.print or not args.generate_visuals:
        print_summary()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
