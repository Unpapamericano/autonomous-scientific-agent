from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


@dataclass
class AnnotationTask:
    task_id: str
    task_type: str
    content: str
    expected_label: str
    difficulty: str
    language: str
    security_level: str = "standard"
    instructions: str = ""

    @classmethod
    def from_record(cls, record: Dict[str, Any]) -> "AnnotationTask":
        return cls(
            task_id=record["task_id"],
            task_type=record["task_type"],
            content=record["content"],
            expected_label=record["expected_label"],
            difficulty=record["difficulty"],
            language=record["language"],
            security_level=record.get("security_level", "standard"),
            instructions=record.get("instructions", ""),
        )


@dataclass
class SubmissionResult:
    task_id: str
    task_type: str
    submitted_label: str
    expected_label: str
    is_correct: bool
    confidence: float
    quality_score: float
    time_seconds: float


@dataclass
class AnnotatorProfile:
    name: str = "AI Annotator"
    english_level: str = "advanced"
    german_level: str = "advanced"
    attention_to_detail: float = 0.93
    reliability: float = 0.94
    typing_speed: float = 85.0


class QualityEvaluator:
    @staticmethod
    def score_submission(task: AnnotationTask, submitted_label: str, time_seconds: float) -> SubmissionResult:
        is_correct = submitted_label == task.expected_label
        base_score = 1.0 if is_correct else 0.0
        difficulty_weight = {"easy": 0.9, "medium": 1.0, "hard": 1.1}[task.difficulty]
        if task.task_type in {"audio", "video"}:
            difficulty_weight *= 1.05
        time_bonus = max(0.0, 1.0 - (time_seconds / 180.0)) * 0.1
        quality_score = round(min(1.0, max(0.0, base_score * difficulty_weight + time_bonus)), 4)
        confidence = 0.98 if is_correct else 0.62
        return SubmissionResult(
            task_id=task.task_id,
            task_type=task.task_type,
            submitted_label=submitted_label,
            expected_label=task.expected_label,
            is_correct=is_correct,
            confidence=confidence,
            quality_score=quality_score,
            time_seconds=time_seconds,
        )


class AnnotationSimulator:
    def __init__(self, task_file: Path):
        self.task_file = task_file
        self.profile = AnnotatorProfile()
        self.evaluator = QualityEvaluator()
        self.tasks: List[AnnotationTask] = self._load_tasks()

    def _load_tasks(self) -> List[AnnotationTask]:
        raw = json.loads(self.task_file.read_text(encoding="utf-8"))
        return [AnnotationTask.from_record(item) for item in raw["tasks"]]

    def _simulate_submission(self, task: AnnotationTask) -> SubmissionResult:
        submitted_label = task.expected_label
        time_seconds = {
            "text": 18,
            "image": 30,
            "audio": 52,
            "video": 75,
        }.get(task.task_type, 25)
        if task.difficulty == "hard":
            time_seconds *= 1.25
        return self.evaluator.score_submission(task, submitted_label, time_seconds)

    def _simulate_calibration_round(self) -> Dict[str, float]:
        calibration_tasks = self.tasks[:3]
        scores = [self._simulate_submission(task).quality_score for task in calibration_tasks]
        return {
            "calibration_score": round(sum(scores) / len(scores), 4),
            "pass_threshold": 0.85,
            "passed": sum(scores) / len(scores) >= 0.85,
        }

    def run(self) -> Dict[str, Any]:
        calibration = self._simulate_calibration_round()
        results = [self._simulate_submission(task) for task in self.tasks]
        quality_scores = [result.quality_score for result in results]
        accuracy = sum(1 for result in results if result.is_correct) / len(results)
        avg_quality = sum(quality_scores) / len(quality_scores)
        by_type = {}
        for result in results:
            by_type.setdefault(result.task_type, []).append(result)

        summary = {
            "project_name": "Generalist Data Annotator Simulation",
            "profile": asdict(self.profile),
            "requirements_match": {
                "remote_flexible_work": True,
                "global_datasets": True,
                "multilingual": self.profile.english_level == "advanced" and self.profile.german_level == "advanced",
                "data_types": sorted(by_type.keys()),
                "quality_control": True,
                "security_protocols": True,
                "contract_work": True,
            },
            "calibration": calibration,
            "metrics": {
                "total_tasks": len(results),
                "accuracy": round(accuracy, 4),
                "average_quality_score": round(avg_quality, 4),
                "text_accuracy": round(self._type_accuracy(by_type.get("text", [])), 4),
                "image_accuracy": round(self._type_accuracy(by_type.get("image", [])), 4),
                "audio_accuracy": round(self._type_accuracy(by_type.get("audio", [])), 4),
                "video_accuracy": round(self._type_accuracy(by_type.get("video", [])), 4),
                "estimated_earnings_usd": round(self._estimate_earnings(results), 2),
            },
            "tasks": [asdict(result) for result in results],
        }
        return summary

    @staticmethod
    def _type_accuracy(results: List[SubmissionResult]) -> float:
        if not results:
            return 0.0
        return sum(1 for item in results if item.is_correct) / len(results)

    @staticmethod
    def _estimate_earnings(results: List[SubmissionResult]) -> float:
        average_per_task = {"text": 0.55, "image": 0.95, "audio": 1.35, "video": 1.9}
        total = 0.0
        for result in results:
            total += average_per_task.get(result.task_type, 0.7) * (0.8 + result.quality_score)
        return total

    @staticmethod
    def save_json_report(data: Dict[str, Any], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def save_dashboard(summary: Dict[str, Any], output_path: Path) -> None:
        metrics = summary["metrics"]
        labels = ["Text", "Image", "Audio", "Video"]
        values = [metrics["text_accuracy"], metrics["image_accuracy"], metrics["audio_accuracy"], metrics["video_accuracy"]]

        plt.figure(figsize=(9, 6))
        plt.bar(labels, values, color=["#0ea5e9", "#22c55e", "#f59e0b", "#8b5cf6"])
        plt.axhline(0.9, color="#ef4444", linestyle="--", linewidth=1.5, label="Quality target")
        plt.ylabel("Accuracy")
        plt.title("Annotation quality by data type")
        plt.ylim(0, 1.1)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
