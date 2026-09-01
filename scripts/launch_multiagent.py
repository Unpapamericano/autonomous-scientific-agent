from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.research.multiagent import ResearchWorkflowRunner


def main() -> int:
    parser = argparse.ArgumentParser(description="Freephdlabor-inspired multi-agent research workflow")
    parser.add_argument("--task", type=str, required=True, help="Research task or hypothesis to execute")
    parser.add_argument("--workspace", type=str, default="results/multiagent_run", help="Where to save workflow artifacts")
    args = parser.parse_args()

    runner = ResearchWorkflowRunner(args.workspace)
    result = runner.run(args.task)

    print(json.dumps({
        "task": result["task"],
        "plan_title": result["plan"]["title"],
        "status": result["review"]["verdict"],
    }, ensure_ascii=False, indent=2))
    print(f"\nResearch report saved to: {Path(args.workspace) / 'research_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
