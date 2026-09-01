import json
from pathlib import Path
from unittest.mock import patch

from src.research.multiagent import ManagerAgent, ResearchWorkflowRunner


class DummyRegistry:
    async def execute(self, name, params):
        return {
            "success": True,
            "stdout": "{\"best_method\": \"candidate_a\", \"average_score\": 0.87}",
            "stderr": "",
            "return_value": None,
            "execution_time_ms": 5.0,
            "error": None,
        }


class DummyLLM:
    def generate(self, prompt, max_new_tokens=None, temperature=None):
        if "IdeationAgent" in prompt:
            return json.dumps({
                "title": "Benchmark Optimization Study",
                "objective": "Improve evaluation quality.",
                "hypotheses": ["Stronger feature engineering matters"],
                "methods": ["feature engineering", "AB testing"],
                "data_sources": ["internal benchmark set"],
                "verification_steps": ["repeat on holdout set"],
                "success_criteria": ["improve quality by 5%"],
            })
        if "ReviewerAgent" in prompt:
            return json.dumps({
                "verdict": "approved",
                "strengths": ["clear logic"],
                "risks": ["limited data"],
                "recommended_changes": ["add ablation"],
            })
        return "# Research Summary\n\nThis study shows the expected gains."


def test_manager_agent_workflow():
    registry = DummyRegistry()
    with patch("src.research.multiagent.MuseGlimmerInference", return_value=DummyLLM()):
        manager = ManagerAgent(tool_registry=registry)
        result = manager.run("Improve a benchmark for scientific evaluation")

    assert result["task"] == "Improve a benchmark for scientific evaluation"
    assert result["plan"]["title"] == "Benchmark Optimization Study"
    assert result["review"]["verdict"] == "approved"
    assert "draft" in result


def test_workflow_runner_writes_artifacts(tmp_path):
    registry = DummyRegistry()
    with patch("src.research.multiagent.MuseGlimmerInference", return_value=DummyLLM()):
        runner = ResearchWorkflowRunner(tmp_path, inference_config=None)
        runner.manager = ManagerAgent(tool_registry=registry)
        result = runner.run("Use an active learning workflow for model selection")

    assert (tmp_path / "research_report.md").exists()
    assert (tmp_path / "workflow_summary.json").exists()
    assert result["plan"]["objective"] == "Improve evaluation quality."
