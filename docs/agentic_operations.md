# Agentic operations

The project uses conservative patterns for longer-running agent work:

- **Adaptive routing:** `src/core/model_routing.py` selects a model profile
  according to task type, quality, latency, and budget. Bulk extraction can
  use a lower-cost profile while synthesis and tool use can select a stronger
  eligible profile.
- **Explicit safety gates:** cybersecurity tasks are marked as requiring
  confirmation and only tool-capable profiles are eligible. This is a policy
  signal for the caller, not permission to create exploits or bypass controls.
- **Searchable context:** `ContextNoteStore` persists decisions, observations,
  and unresolved questions as JSONL. Search results are deterministic and
  bounded so prior context can be recovered without relying on a lossy summary.
- **Evidence localization:** adaptive analysis keeps source IDs, locators,
  excerpts, and telemetry so synthesis claims can be inspected against the
  underlying artifact.

Model benchmark scores and vendor announcements should be stored as dated,
independently verifiable evidence. A reported score is not automatically
comparable across harnesses, versions, prompts, or tool configurations.
