"""
Phase 9: Evaluation Framework Tests

Tests for metrics, benchmarks, evaluation orchestration, and reporting.
"""

import pytest
from src.evaluation.metrics import (
    MetricsCalculator,
    RQ1Result,
    RQ2Result,
    RQ4Result,
    RQ5Result,
    RQ7Result,
)
from src.evaluation.benchmarks import (
    BenchmarkDatasets,
    ResearchQuestion,
    ContradictionPair,
    QuestionDomain,
)
from src.evaluation.evaluator import EvaluationOrchestrator, EvaluationConfig
from src.evaluation.report_generator import ReportGenerator
import pytest


class TestMetricsCalculator:
    """Test metrics calculation."""

    def test_calculate_rq1(self):
        calc = MetricsCalculator()
        result = calc.calculate_rq1(
            num_tasks_total=10,
            num_tasks_completed=8,
            num_papers_cited=45,
            total_latency_seconds=1200,
            workflow_errors=1,
            traceable_citations=38,
        )

        assert result.task_completion_rate == 0.8
        assert result.answer_coverage == 45
        assert result.latency_seconds == 150.0
        assert result.workflow_errors == 1

    def test_calculate_rq2(self):
        calc = MetricsCalculator()
        result = calc.calculate_rq2(
            num_claims_total=100,
            num_claims_with_citations=90,
            num_extractable_facts=50,
            num_facts_cited=45,
            confidence_scores=[0.8, 0.9, 0.85],
            treatment="rag_grounded",
        )

        assert result.grounded_precision == 0.9
        assert result.grounded_recall == 0.9
        assert result.hallucination_rate == pytest.approx(0.1)
        assert result.treatment == "rag_grounded"

    def test_calculate_rq4(self):
        calc = MetricsCalculator()
        result = calc.calculate_rq4(
            tp=12,  # 12 real contradictions detected
            fp=2,  # 2 false positives
            fn=3,  # 3 contradictions missed
        )

        # Precision = 12 / (12+2) = 0.857
        # Recall = 12 / (12+3) = 0.8
        # F1 = 2 * (0.857 * 0.8) / (0.857 + 0.8) ≈ 0.828

        assert result.precision == pytest.approx(0.857, 0.01)
        assert result.recall == 0.8
        assert result.f1_score == pytest.approx(0.828, 0.01)

    def test_calculate_rq5(self):
        calc = MetricsCalculator()
        result = calc.calculate_rq5(
            attacks_blocked=18,
            attacks_passed=2,
            false_positives=1,
            benign_inputs=100,
            security_latency_overhead_ms=50,
        )

        assert result.attack_success_rate == 0.1  # 2/20
        assert result.false_positive_rate == 0.01  # 1/100
        assert result.latency_overhead_ms == 50

    def test_calculate_rq7_quality_score(self):
        calc = MetricsCalculator()
        score = calc.calculate_rq7_quality_score(
            rq1_completion=0.80,  # 40% weight
            rq2_precision=0.90,  # 35% weight
            rq4_f1=0.75,  # 15% weight
            rq5_security=0.95,  # 10% weight (1 - attack_success_rate)
        )

        # 0.40*0.80 + 0.35*0.90 + 0.15*0.75 + 0.10*0.95
        # = 0.32 + 0.315 + 0.1125 + 0.095 = 0.8425
        assert score == pytest.approx(0.8425, 0.001)


class TestBenchmarkDatasets:
    """Test benchmark datasets."""

    def test_get_research_questions(self):
        questions = BenchmarkDatasets.get_research_questions()

        assert len(questions) == 15
        assert all(isinstance(q, ResearchQuestion) for q in questions)
        assert questions[0].id == "rq1_q1"
        assert questions[0].domain == QuestionDomain.BIOLOGY

    def test_get_contradiction_pairs(self):
        pairs = BenchmarkDatasets.get_contradiction_pairs()

        assert len(pairs) > 0
        assert all(isinstance(p, ContradictionPair) for p in pairs)
        # Check for both contradictions and non-contradictions
        contradictions = [p for p in pairs if p.is_contradiction]
        non_contradictions = [p for p in pairs if not p.is_contradiction]
        assert len(contradictions) > 0
        assert len(non_contradictions) > 0

    def test_get_adversarial_documents(self):
        docs = BenchmarkDatasets.get_adversarial_documents()

        assert len(docs) > 0
        # Check all docs have injection payloads
        for doc in docs:
            assert doc.injection_payload is not None
            assert doc.expected_detection is True

    def test_get_by_domain(self):
        bio_questions = BenchmarkDatasets.get_by_domain(QuestionDomain.BIOLOGY)

        assert len(bio_questions) > 0
        assert all(q.domain == QuestionDomain.BIOLOGY for q in bio_questions)


class TestEvaluationOrchestrator:
    """Test evaluation orchestration."""

    def test_create_run(self):
        orch = EvaluationOrchestrator()
        config = EvaluationConfig(
            name="test_run",
            description="Test evaluation",
            test_set="research_questions",
        )

        run = orch.create_run(config)

        assert run.config.name == "test_run"
        assert run.status == "running"
        assert run.phase.value == "setup"

    def test_add_result(self):
        orch = EvaluationOrchestrator()
        config = EvaluationConfig(
            name="test_run",
            description="Test",
            test_set="research_questions",
        )
        run = orch.create_run(config)

        orch.add_result("test_1", {"status": "pass", "score": 0.95})

        assert len(run.results) == 1
        assert run.results["test_1"]["score"] == 0.95

    def test_add_error(self):
        orch = EvaluationOrchestrator()
        config = EvaluationConfig(
            name="test_run",
            description="Test",
            test_set="research_questions",
        )
        run = orch.create_run(config)

        orch.add_error("Test failed")

        assert len(run.errors) == 1

    def test_complete_run(self):
        orch = EvaluationOrchestrator()
        config = EvaluationConfig(
            name="test_run",
            description="Test",
            test_set="research_questions",
        )
        run = orch.create_run(config)
        orch.complete_run(status="completed")

        assert run.status == "completed"
        assert run.end_time is not None

    def test_get_run(self):
        orch = EvaluationOrchestrator()
        config = EvaluationConfig(
            name="test_run",
            description="Test",
            test_set="research_questions",
        )
        run1 = orch.create_run(config)
        run_id = run1.run_id

        retrieved = orch.get_run(run_id)

        assert retrieved is not None
        assert retrieved.run_id == run_id


class TestReportGenerator:
    """Test report generation."""

    def test_generate_report(self):
        gen = ReportGenerator()
        report = gen.generate_report(
            title="Test Report",
            summary={"metric1": 0.85, "metric2": 42},
            rq_results={"RQ1": {"status": "PASS", "score": 0.85}},
            recommendations=["Improve X", "Optimize Y"],
        )

        assert report.title == "Test Report"
        assert len(report.recommendations) == 2
        assert report.report_id is not None

    def test_generate_rq1_report(self):
        gen = ReportGenerator()
        report = gen.generate_rq1_report(
            completion_rate=0.75,
            coverage=45,
            latency=180.0,
            errors=0,
            citations=38,
        )

        assert "RQ1" in report.rq_results
        assert report.rq_results["RQ1"]["status"] == "PASS"

    def test_generate_rq4_report(self):
        gen = ReportGenerator()
        report = gen.generate_rq4_report(
            precision=0.80,
            recall=0.75,
            f1=0.77,
        )

        assert "RQ4" in report.rq_results
        assert report.rq_results["RQ4"]["status"] == "PASS"

    def test_generate_rq5_report(self):
        gen = ReportGenerator()
        report = gen.generate_rq5_report(
            attack_success_rate=0.05,
            false_positive_rate=0.03,
            latency_overhead_ms=50,
            attacks_blocked=19,
            attacks_passed=1,
        )

        assert "RQ5" in report.rq_results
        assert report.rq_results["RQ5"]["status"] == "PASS"

    def test_report_to_json(self):
        gen = ReportGenerator()
        report = gen.generate_report(
            title="Test",
            summary={"metric": 0.85},
            rq_results={"RQ1": {"status": "PASS"}},
        )

        json_str = report.to_json()
        assert "Test" in json_str
        assert "PASS" in json_str

    def test_report_to_markdown(self):
        gen = ReportGenerator()
        report = gen.generate_report(
            title="Test Report",
            summary={"metric": 0.85},
            rq_results={"RQ1": {"status": "PASS"}},
            recommendations=["Rec 1", "Rec 2"],
        )

        md = report.to_markdown()
        assert "# Autonomous Scientific Agent" in md
        assert "Test Report" in md
        assert "Rec 1" in md
        assert "85.00%" in md  # 0.85 formatted as 85.00%
