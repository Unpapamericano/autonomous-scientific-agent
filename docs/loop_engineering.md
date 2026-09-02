# Loop engineering

## Status

This is a work-in-progress engineering pattern applied to the scientific
research platform. It is an operational method for improving software and
research workflows, not a claim that generated scientific outputs are final,
causal, or clinically validated.

## The loop

```text
DEFINE → BUILD → MEASURE → REVIEW → ITERATE
   ↑                                  ↓
   └────────────── improvement ──────┘
```

- **Define**: state the question, constraints, success criteria, and risks.
- **Build**: produce the smallest reproducible artifact or experiment.
- **Measure**: record quality, evidence coverage, latency, cost, and failures.
- **Review**: inspect evidence, uncertainty, safety, and reproducibility.
- **Iterate**: stop when criteria are met or revise the objective and repeat.

`src/research/loop_engineering.py` provides a bounded, callback-based
implementation that can wrap local inference, Polars analysis, tool calls, and
human review.

## Why it benefits this project

Loop engineering makes the adaptive-analysis roadmap operational. Instead of
asking an agent for one opaque answer, each pass leaves an auditable record:
what was intended, what was built, what was measured, and why the next pass
continued or stopped.

Expected benefits:

- less wasted model and tool computation
- earlier detection of weak evidence or broken assumptions
- measurable quality improvement across iterations
- clearer provenance for scientific visuals and reports
- safer separation of evidence, association, hypothesis, and speculation
- reproducible handoff between agents and engineers

The diagram and PDF are generated with:

```bash
python scripts/generate_loop_engineering_visual.py
```

Outputs:

- `visuals/loop_engineering_workflow.png`
- `visuals/loop_engineering_benefits.pdf`

These materials explain an engineering process. They do not validate any
medical conclusion or provide treatment guidance.
