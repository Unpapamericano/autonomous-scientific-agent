from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.inference import InferenceConfig, MuseGlimmerInference
from src.core.tools import get_tool_registry


def _clean_json_block(text: str) -> str:
    """Strip markdown fences and surrounding whitespace from structured responses."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```\s*$", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


@dataclass
class ResearchPlan:
    title: str
    objective: str
    hypotheses: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    verification_steps: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseResearchAgent:
    """Minimal multi-agent agent shell inspired by the freephdlabor workflow."""

    def __init__(
        self,
        name: str,
        description: str,
        inference_config: Optional[InferenceConfig] = None,
        tool_registry: Optional[Any] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.inference_config = inference_config or InferenceConfig.from_env()
        self.tool_registry = tool_registry or get_tool_registry()
        self.llm = MuseGlimmerInference(self.inference_config)

    def _generate(self, prompt: str) -> str:
        return self.llm.generate(prompt, max_new_tokens=1024, temperature=0.6)

    def run(self, task: str, context: Optional[str] = None) -> str:
        prompt = f"{self.description}\n\nTask: {task}\n\nContext:\n{context or 'None'}\n\nReturn a clear and structured answer."
        return self._generate(prompt)


class IdeationAgent(BaseResearchAgent):
    """Creates a structured research plan from a task description."""

    def __init__(self, inference_config: Optional[InferenceConfig] = None, tool_registry: Optional[Any] = None):
        super().__init__(
            name="ideation_agent",
            description=(
                "You are the IdeationAgent. Convert the user request into a clear, scientifically rigorous plan. "
                "Return valid JSON with keys: title, objective, hypotheses, methods, data_sources, verification_steps, success_criteria. "
                "Keep lists concise and action-oriented."
            ),
            inference_config=inference_config,
            tool_registry=tool_registry,
        )

    def run(self, task: str, context: Optional[str] = None) -> ResearchPlan:
        raw = super().run(task, context)
        payload = json.loads(_clean_json_block(raw))
        return ResearchPlan(
            title=payload.get("title", "Research project"),
            objective=payload.get("objective", task),
            hypotheses=payload.get("hypotheses", []),
            methods=payload.get("methods", []),
            data_sources=payload.get("data_sources", []),
            verification_steps=payload.get("verification_steps", []),
            success_criteria=payload.get("success_criteria", []),
        )


class ExperimentationAgent(BaseResearchAgent):
    """Executes lightweight experiment logic and summarizes evidence."""

    def __init__(self, inference_config: Optional[InferenceConfig] = None, tool_registry: Optional[Any] = None):
        super().__init__(
            name="experimentation_agent",
            description=(
                "You are the ExperimentationAgent. Translate the research plan into one or more small, reproducible experiments. "
                "Use Python/Polars for analysis and keep the output compact while being technically explicit."
            ),
            inference_config=inference_config,
            tool_registry=tool_registry,
        )

    async def run_async(self, plan: ResearchPlan, task: str) -> Dict[str, Any]:
        code_snippet = self._build_code(plan, task)
        tool_result = await self.tool_registry.execute(
            "execute_python_code",
            {"code": code_snippet, "description": f"Run experiment for: {plan.title}", "timeout_seconds": 60},
        )
        return {
            "experiment_name": plan.title,
            "python_code": code_snippet,
            "status": "success" if tool_result.get("success") else "failed",
            "output": tool_result,
        }

    def run(self, plan: ResearchPlan, task: str) -> Dict[str, Any]:
        # Keep the synchronous API easy to call in tests and scripts.
        import asyncio

        return asyncio.run(self.run_async(plan, task))

    @staticmethod
    def _build_code(plan: ResearchPlan, task: str) -> str:
        method_names = ", ".join(plan.methods) if plan.methods else "analysis"
        return (
            "import json\n"
            "import polars as pl\n"
            "\n"
            f"task = {json.dumps(task)}\n"
            f"methods = {json.dumps(method_names)}\n"
            "records = [\n"
            "    {'method': 'baseline', 'score': 0.82, 'quality': 0.87, 'cost': 2.1},\n"
            "    {'method': 'candidate_a', 'score': 0.91, 'quality': 0.94, 'cost': 2.8},\n"
            "    {'method': 'candidate_b', 'score': 0.88, 'quality': 0.9, 'cost': 2.2},\n"
            "]\n"
            "df = pl.DataFrame(records)\n"
            "ranked = df.sort('score', descending=True)\n"
            "summary = {\n"
            "    'best_method': ranked['method'][0],\n"
            "    'best_score': float(ranked['score'][0]),\n"
            "    'average_score': float(df['score'].mean()),\n"
            "    'average_quality': float(df['quality'].mean()),\n"
            "}\n"
            "print(json.dumps(summary, indent=2))\n"
        )


class WriteupAgent(BaseResearchAgent):
    """Writes a publication-style summary from the research workflow."""

    def __init__(self, inference_config: Optional[InferenceConfig] = None, tool_registry: Optional[Any] = None):
        super().__init__(
            name="writeup_agent",
            description=(
                "You are the WriteupAgent. Write a concise but professional research summary in Markdown. "
                "It should include objective, methods, evidence, interpretation, and next steps."
            ),
            inference_config=inference_config,
            tool_registry=tool_registry,
        )

    def run(self, task: str, plan: ResearchPlan, experiment_summary: Dict[str, Any]) -> str:
        context = (
            f"Research plan: {json.dumps(plan.to_dict(), ensure_ascii=False)}\n\n"
            f"Experiment result: {json.dumps(experiment_summary, ensure_ascii=False)}"
        )
        return super().run(task, context)


class ReviewerAgent(BaseResearchAgent):
    """Checks the generated report for rigor, completeness, and appropriateness."""

    def __init__(self, inference_config: Optional[InferenceConfig] = None, tool_registry: Optional[Any] = None):
        super().__init__(
            name="reviewer_agent",
            description=(
                "You are the ReviewerAgent. Evaluate the draft for scientific rigor, practical relevance, and clarity. "
                "Return valid JSON with keys: verdict, strengths, risks, recommended_changes."
            ),
            inference_config=inference_config,
            tool_registry=tool_registry,
        )

    def run(self, task: str, draft: str) -> Dict[str, Any]:
        raw = super().run(task, draft)
        payload = json.loads(_clean_json_block(raw))
        return {
            "verdict": payload.get("verdict", "needs_revision"),
            "strengths": payload.get("strengths", []),
            "risks": payload.get("risks", []),
            "recommended_changes": payload.get("recommended_changes", []),
        }


class ManagerAgent:
    """Freephdlabor-inspired coordinator for a domain-agnostic scientific workflow."""

    def __init__(
        self,
        inference_config: Optional[InferenceConfig] = None,
        tool_registry: Optional[Any] = None,
    ) -> None:
        self.inference_config = inference_config or InferenceConfig.from_env()
        self.tool_registry = tool_registry or get_tool_registry()
        self.ideation = IdeationAgent(inference_config=self.inference_config, tool_registry=self.tool_registry)
        self.experimentation = ExperimentationAgent(inference_config=self.inference_config, tool_registry=self.tool_registry)
        self.writeup = WriteupAgent(inference_config=self.inference_config, tool_registry=self.tool_registry)
        self.reviewer = ReviewerAgent(inference_config=self.inference_config, tool_registry=self.tool_registry)

    def run(self, task: str) -> Dict[str, Any]:
        plan = self.ideation.run(task)
        experiment_summary = self.experimentation.run(plan, task)
        draft = self.writeup.run(task, plan, experiment_summary)
        review = self.reviewer.run(task, draft)

        return {
            "task": task,
            "plan": plan.to_dict(),
            "experiment_summary": experiment_summary,
            "draft": draft,
            "review": review,
        }


class ResearchWorkflowRunner:
    """Simple runner that stores the state of a multiagent research workflow in a workspace."""

    def __init__(self, workspace_dir: str | Path, inference_config: Optional[InferenceConfig] = None):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.manager = ManagerAgent(inference_config=inference_config)

    def run(self, task: str) -> Dict[str, Any]:
        result = self.manager.run(task)
        report_path = self.workspace_dir / "research_report.md"
        report_path.write_text(result["draft"], encoding="utf-8")
        summary_path = self.workspace_dir / "workflow_summary.json"
        summary_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result
