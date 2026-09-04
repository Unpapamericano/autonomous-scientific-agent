# PHASE 9: EVALUATION FRAMEWORK

## Overview

Phase 9 implements a comprehensive evaluation framework for measuring research quality against **RQ1–RQ7 research questions** from RESEARCH.md.

**Status**: ✅ COMPLETE
**Tests**: 20 new evaluation tests (all passing), 142 total passing across all phases
**Coverage**: Metrics, benchmarks, orchestration, reporting for all 7 RQs

---

## What Was Built

### 1. Metrics Calculation (`src/evaluation/metrics.py`)

**RQ-Specific Result Types**:

- **RQ1Result**: Task completion rate, answer coverage, latency, errors, traceable citations
- **RQ2Result**: Citation precision/recall, hallucination rate, grounding confidence (RAG effect)
- **RQ3Result**: Completion rate, evidence extraction F1, analysis depth, error recovery (tool effect)
- **RQ4Result**: Contradiction detection precision/recall/F1 and false positive rate
- **RQ5Result**: Attack success rate, false positive rate, latency overhead, attacks blocked/passed
- **RQ6Result**: Model comparison (Muse vs. Gemma/Qwen/Nemotron)
- **RQ7Result**: Quality-cost Pareto frontier (quantization, hardware, quality, latency, cost)

**MetricsCalculator**:
```python
calc = MetricsCalculator()

# RQ1: Task completion
rq1 = calc.calculate_rq1(
    num_tasks_total=15,
    num_tasks_completed=12,
    num_papers_cited=50,
    total_latency_seconds=1800,
    workflow_errors=1,
    traceable_citations=45,
)
# → completion_rate=0.80, latency=150s, coverage=50

# RQ4: Contradiction detection
rq4 = calc.calculate_rq4(tp=12, fp=2, fn=3)
# → precision=0.857, recall=0.8, f1=0.828

# RQ7: Composite quality score
score = calc.calculate_rq7_quality_score(
    rq1_completion=0.80,    # 40% weight
    rq2_precision=0.90,     # 35% weight
    rq4_f1=0.75,           # 15% weight
    rq5_security=0.95,     # 10% weight
)
# → quality_score=0.8425
```

### 2. Benchmark Datasets (`src/evaluation/benchmarks.py`)

**Dataset 1: Research Questions (n=15)**
- Biology (CRISPR, microbiota, SARS-CoV-2)
- Chemistry (perovskites, plastic degradation)
- AI/ML (SWE-Bench, diffusion models)
- Medicine (GLP-1, CAR-T)
- Physics (quantum entanglement, QEC)
- And more...

**Dataset 2: Contradiction Pairs (n=30)**
- 15 genuine contradictions (e.g., vitamin D studies conflicting)
- 15 non-contradictions (complementary findings)
- Each pair annotated with gold label + explanation

**Dataset 3: Adversarial Documents (n=20)**
- Direct jailbreaks ("ignore previous instructions")
- Role overrides ("you are now a sales agent")
- Subtle priming (biased language)
- Context confusion (hidden instructions in captions)
- Goal overrides (redefine objective)

All datasets queryable by domain/type:
```python
datasets = BenchmarkDatasets()

# Get all
questions = datasets.get_research_questions()  # 15
contradictions = datasets.get_contradiction_pairs()  # 30
adversarial = datasets.get_adversarial_documents()  # 20

# Filter by domain
bio_questions = datasets.get_by_domain(QuestionDomain.BIOLOGY)
```

### 3. Evaluation Orchestrator (`src/evaluation/evaluator.py`)

**EvaluationOrchestrator** manages end-to-end evaluation runs:

```python
orch = EvaluationOrchestrator()

# Create run
config = EvaluationConfig(
    name="RQ1_Completion",
    description="Test task completion rate",
    test_set="research_questions",
)
run = orch.create_run(config)

# Execute tests
orch.start_run(run)
orch.add_result("q1", {"completion": True, "latency": 145.3})
orch.add_result("q2", {"completion": True, "latency": 155.2})

# Metrics
orch.complete_metrics_phase({"avg_latency": 150.3})

# Complete
orch.complete_run(status="completed")

# Query
summary = run.to_dict()
all_runs = orch.get_all_runs()
```

**TestRunner** executes individual tests:
```python
runner = TestRunner(orch)

tests = [
    ("test_1", lambda: agent.process(q1)),
    ("test_2", lambda: agent.process(q2)),
]

results = runner.run_batch(tests, timeout_seconds=300)
```

### 4. Report Generator (`src/evaluation/report_generator.py`)

**EvaluationReport** with JSON/Markdown export:

```python
gen = ReportGenerator()

# RQ1 report
report = gen.generate_rq1_report(
    completion_rate=0.80,
    coverage=50,
    latency=150.0,
    errors=1,
    citations=45,
)

# Export
json_report = report.to_json()
md_report = report.to_markdown()
```

**Report Contents**:
- Executive summary (key metrics)
- RQ-specific results + success criteria
- Recommendations based on failures
- Metadata (timestamp, run ID)
- Appendix (raw data)

---

## RQ1–RQ7 Evaluation Structure

| RQ | Metric | Target | Status Check |
|---|---|---|---|
| **RQ1** | Task completion | ≥70% | completion_rate ≥ 0.70 |
| **RQ1** | Latency | <5 min (300s) | latency < 300 |
| **RQ2** | Citation precision | ≥0.85 | grounded_precision ≥ 0.85 |
| **RQ2** | Hallucination reduction | RAG <0.15 vs no-RAG >0.50 | reduction > 3.3x |
| **RQ3** | Tool benefit | +40% completion | completion_full > 1.4 × completion_none |
| **RQ4** | Contradiction F1 | ≥0.65 | f1_score ≥ 0.65 |
| **RQ4** | Precision | >0.60 | precision ≥ 0.60 |
| **RQ5** | Attack success | <10% | attack_success_rate < 0.10 |
| **RQ5** | False positives | <5% | false_positive_rate < 0.05 |
| **RQ6** | Model advantage | Muse +20% over alternatives | completion_muse ≥ 1.2 × completion_alt |
| **RQ7** | Quality-cost frontier | Clear tradeoff visible | Pareto curve plotable |

---

## Integration with Phase 11 (Benchmarking)

Phase 9 provides infrastructure; Phase 11 runs actual evaluations:

```python
# Phase 11 will do:
from src.evaluation import BenchmarkDatasets, MetricsCalculator, get_evaluator
from src.core.orchestration import Agent

evaluator = get_evaluator()
calc = MetricsCalculator()
agent = Agent()

# RQ1: Task completion
config = EvaluationConfig(
    name="RQ1_Completion_Phase11",
    description="Evaluate on 15 research questions",
    test_set="research_questions",
)
run = evaluator.create_run(config)
evaluator.start_run(run)

for question in BenchmarkDatasets.get_research_questions():
    result = agent.research(question.question)
    evaluator.add_result(question.id, result)

metrics = calc.calculate_rq1(...)
evaluator.complete_metrics_phase(metrics)
evaluator.complete_run()

report = report_gen.generate_rq1_report(...)
print(report.to_markdown())
```

---

## Testing

**20 tests** cover:
- Metrics calculation for all RQs
- Benchmark dataset loading & filtering
- Evaluation run creation/completion
- Test result collection
- Report generation (JSON, Markdown)
- Export/serialization

**Run tests**:
```bash
pytest tests/evaluation/test_evaluation.py -v
# 20 passed
```

---

## Limitations (Phase 9)

- **No actual benchmark execution** — infrastructure ready, Phase 11 runs tests
- **Metrics manual** — no automated data collection from agent
- **Comparison models not integrated** — Phase 11 will load Gemma, Qwen, etc.
- **No visualization** — Phase 9 generates JSON/Markdown; Phase 10 adds charts
- **Single-threaded** — `TestRunner.run_batch()` sequential; parallelization for Phase 11

---

## Success Criteria

Phase 9 enables:
- ✅ **Metric calculation** for all 7 RQs
- ✅ **Dataset provision** for benchmarking
- ✅ **Run orchestration** for test execution
- ✅ **Report generation** for publishing results
- ✅ **Export formats** (JSON, Markdown)

---

## Example: Running RQ4 Evaluation (Phase 11+)

```python
from src.evaluation import BenchmarkDatasets, MetricsCalculator, get_evaluator, get_report_generator
from src.rag.evidence_graph import EvidenceGraphBuilder

# Setup
evaluator = get_evaluator()
calc = MetricsCalculator()
gen = get_report_generator()
graph_builder = EvidenceGraphBuilder()

# Run
config = EvaluationConfig("RQ4_Contradiction", "Contradiction detection", "contradictions")
run = evaluator.create_run(config)
evaluator.start_run(run)

tp, fp, fn = 0, 0, 0
for pair in BenchmarkDatasets.get_contradiction_pairs():
    result = graph_builder.detect_contradiction(pair.paper_a_finding, pair.paper_b_finding)
    is_contradiction = result.contradictory
    
    if is_contradiction and pair.is_contradiction:
        tp += 1
    elif is_contradiction and not pair.is_contradiction:
        fp += 1
    elif not is_contradiction and pair.is_contradiction:
        fn += 1

# Metrics
rq4_result = calc.calculate_rq4(tp, fp, fn)
evaluator.complete_metrics_phase({"f1": rq4_result.f1_score})

# Report
report = gen.generate_rq4_report(
    precision=rq4_result.precision,
    recall=rq4_result.recall,
    f1=rq4_result.f1_score,
)
print(report.to_markdown())

evaluator.complete_run()
```

---

## Next: Phase 10 — Dashboard & UI

Add web dashboard to visualize evaluation results, charts, and system status.
