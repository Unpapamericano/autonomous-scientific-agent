"""Generate a trombone practice plan from the command line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow the documented direct invocation from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.music.trombone import build_practice_plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a structured trombone practice session")
    parser.add_argument("--minutes", type=int, default=45)
    parser.add_argument("--focus", default="fundamentals")
    args = parser.parse_args()
    print(json.dumps(build_practice_plan(args.minutes, focus=args.focus).to_dict(), indent=2))


if __name__ == "__main__":
    main()
