"""Fetch and render the live multiple-sclerosis trials monitor."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.research.clinical_trials import ClinicalTrialsClient, render_ms_trials_page


OUTPUT = ROOT / "visuals" / "ms_clinical_trials.html"


def main() -> None:
    client = ClinicalTrialsClient()
    try:
        trials = client.search_ms_trials()
    finally:
        client.close()
    OUTPUT.write_text(render_ms_trials_page(trials), encoding="utf-8")
    print(f"Rendered {len(trials)} studies to {OUTPUT}")


if __name__ == "__main__":
    main()
