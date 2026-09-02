# Adaptive analysis roadmap

## Status

This is an active work-in-progress implementation roadmap. It applies the
general design principles behind Google's agentic video understanding to this
local-first scientific research platform. It does not add Gemini as a required
runtime dependency and does not claim Google's benchmark results apply here.

## Implemented foundation

- Explicit `fast`, `balanced`, and `deep` processing modes
- Cheap global scan followed by bounded relevance-based inspection
- Evidence localization for pages, figures, tables, transcript segments, and timestamps
- Structured telemetry for scanned units, inspected units, tool calls, tokens, latency,
  evidence coverage, confidence, and inspection ratio
- Backend-neutral interfaces compatible with Ollama, local extraction, and future providers

Implementation: `src/research/adaptive_analysis.py`.

## Next increments

1. Add adapters for PDF pages, literature records, transcript segments, and Polars
   partitions.
2. Connect the plan to orchestration so tools are called only for selected evidence.
3. Persist telemetry beside workflow artifacts for static-vs-adaptive evaluation.
4. Add citation validation and missed-evidence checks.
5. Benchmark quality, latency, token use, and cost on a fixed local test corpus.
6. Add optional provider adapters only behind explicit configuration flags.

## Guardrails

- Adaptive ranking is a routing heuristic, not proof of relevance or causation.
- A low inspection ratio must not be presented as complete evidence coverage.
- Scientific outputs must distinguish established evidence, association, hypothesis,
  experimental intervention, and speculation.
- The multiple sclerosis visuals remain exploratory information artifacts, not
  clinical advice, definitive solutions, or cure claims.
