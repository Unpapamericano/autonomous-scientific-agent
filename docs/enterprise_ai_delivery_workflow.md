# Enterprise-inspired software and AI delivery workflow

## Scope and attribution

This is an original adaptation of publicly observable enterprise delivery
practices associated with large software, consulting, and AI organizations,
including companies such as Accenture. It is not an official Accenture
framework and does not reproduce proprietary methods.

The workflow is designed for this repository's local-first scientific platform.
It complements loop engineering and adaptive analysis by adding explicit
delivery stages, evidence-based gates, and production ownership.

## Lifecycle

```text
DISCOVER → DESIGN → BUILD → VALIDATE → RELEASE → OPERATE → EVOLVE
    ↑                                                        ↓
    └────────────── measured feedback and new experiments ───┘
```

| Stage | Main outcome | Gate examples |
|---|---|---|
| Discover | Problem brief and measurable value | success metrics, risk register |
| Design | Architecture and data boundaries | data contract, threat model |
| Build | Reproducible implementation | tests, observability |
| Validate | Quality and evidence decision | evaluation, human review |
| Release | Controlled production handoff | approval, rollback plan |
| Operate | Reliable and economical service | drift, incidents, cost |
| Evolve | Prioritized improvements | feedback, next experiment |

## Applying it here

- **Software engineering** owns modular code, APIs, tests, security, release
  automation, and operational reliability.
- **AI engineering** owns model routing, prompt/tool contracts, evaluation,
  grounding, uncertainty, safety, and cost-quality trade-offs.
- **Domain review** protects against overclaiming, especially in the MS
  evidence work: exploratory correlations are not causation or treatment advice.
- **Product and stakeholder review** keeps the project aligned to user value,
  accessibility, and understandable visual communication.

The executable gate model is in `src/research/enterprise_delivery.py`.
Generate the visual and PDF with:

```bash
python scripts/generate_enterprise_workflow_visual.py
```

Outputs:

- `visuals/enterprise_ai_delivery_workflow.png`
- `visuals/enterprise_ai_delivery_benefits.pdf`

## Expected benefits

- clearer ownership between software, AI, data, and domain work
- fewer unsafe or unreviewed releases
- repeatable quality gates instead of one-shot demos
- explicit rollback, monitoring, and incident readiness
- measurable cost, latency, evidence coverage, and model quality
- a durable path from experiment to maintainable product

This remains a work in progress. Passing a software gate does not validate a
scientific or medical conclusion; scientific claims still require appropriate
literature, expert review, and clinical validation.
