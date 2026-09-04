# PHASE 5: EVIDENCE GRAPH & CONTRADICTION DETECTION

## Overview

Phase 5 turns raw papers/chunks into checkable claims and builds a graph
connecting Claim → DocumentChunk (evidence) and Claim → Claim
(support/contradiction). This directly targets **RQ4** in RESEARCH.md
("Can agents detect contradictions?").

**Status**: ✅ COMPLETE
**Tests**: 32 new tests (all passing), 62 total passing across the project (13 intentionally skipped)

---

## What Was Built

### 1. Claim Extraction (`src/rag/claim_extraction.py`)
- `extract_claims_heuristic(text)` — sentence-splits text and classifies each
  sentence as `finding` / `hypothesis` / `limitation` using cue-phrase
  heuristics (no GPU/LLM required, works everywhere).
- Filters out background/citation sentences (`et al.`, questions, short
  sentences) so extraction stays precision-oriented.
- `llm_extract_claims(text, agent)` — optional extension point that
  delegates to a Phase 2 `ResearchAgent` for higher-quality extraction,
  with automatic fallback to the heuristic extractor if no agent/model
  is available or the LLM call fails.

### 2. Evidence Graph (`src/rag/evidence_graph.py`)
- `compare_claims(text_a, text_b)` — classifies two claim texts as
  `supports` / `contradicts` / `neutral`:
  1. Embed both claims (Phase 4 embedder) and compute cosine similarity.
  2. Below `TOPICAL_SIMILARITY_THRESHOLD` (0.55) → `neutral` (not about the same thing).
  3. Above threshold: check for polarity conflict (opposite-direction word
     pairs like increase/decrease, effective/ineffective, or a negation
     mismatch) → `contradicts`; otherwise → `supports`.
- Every result carries `similarity_score`, `confidence`, and a
  human-readable `explanation` — nothing is a black box (per RESEARCH.md's
  emphasis on reproducibility).
- `EvidenceGraphBuilder`:
  - `extract_and_store_claims()` — extracts + embeds + persists `Claim` rows.
  - `link_claim_to_chunk()` — creates an `Evidence` row when a claim and a
    chunk are semantically close enough (`direct` if similarity ≥0.75, else `indirect`).
  - `detect_contradiction()` / `build_relations_for_claim()` — compares a
    claim against others and persists `ClaimRelation` rows.
  - `get_contradictions_for_paper()` — query helper for surfacing conflicts.

### 3. Agent Tools (`src/rag/evidence_tool.py`)
- `extract_claims` tool — pulls claims out of an already-ingested paper's
  chunks (falls back to the abstract if no chunks exist).
- `check_contradictions` tool — compares a paper's claims against claims
  from other ingested papers, returning `relations` with counts of
  supports/contradictions.
- Both registered via `register_evidence_tools(registry)`, following the
  same DB-session pattern as Phase 4's `rag_tool.py`.

### 4. Model Changes (`src/rag/models.py`)
- `Claim` gained `source_chunk_id` (FK to `DocumentChunk`), `claim_embedding`,
  and `embedding_model` columns.
- New `ClaimRelation` table: `claim_id_a`, `claim_id_b`, `relation_type`,
  `similarity_score`, `confidence`, `explanation`, unique on the claim pair.
- Verified all 11 tables (including the new `claim_relations`) register
  cleanly with SQLAlchemy's declarative Base.

### 5. Tests (`tests/integration/test_evidence_graph.py`)
- Sentence splitting (handles `et al.` correctly).
- Cue-phrase classification for all three claim types + negative cases
  (too short, citation-heavy, purely background).
- Full heuristic extraction pipeline on a realistic abstract.
- Polarity-conflict detection (opposite pairs, negation mismatches).
- `compare_claims()` classification with mocked embedders (neutral /
  contradicts / supports).
- `EvidenceGraphBuilder` end-to-end with mocked session + embedder:
  claim storage, evidence linking (above/below threshold, missing
  embeddings), contradiction detection, self-comparison skip,
  neutral-storage toggle, similarity ranking.

---

## Bug Found & Fixed During Verification

**Cue-phrase priority bug**: the sentence *"We hypothesize that this
approach may lead to broader applications... improved outcomes"* matched
both the `finding` cue `"improved"` and the `hypothesis` cue
`"we hypothesize"`, but since `finding` was checked before `hypothesis` in
`_classify_sentence`, it was misclassified as a finding. Fixed by
reordering the checks so `limitation` → `hypothesis` → `finding` (explicit
epistemic-stance cues like "we hypothesize" now win over incidental
overlapping words). Caught by a test (`test_classify_hypothesis`) and
verified fixed with the full suite passing afterward.

---

## Usage

```python
from src.rag.database import get_session
from src.rag.evidence_graph import EvidenceGraphBuilder

session = get_session()
builder = EvidenceGraphBuilder(session)

# Extract + store claims from an ingested paper's abstract
claims_a = builder.extract_and_store_claims(paper_id="p1", text=paper_a.abstract)
claims_b = builder.extract_and_store_claims(paper_id="p2", text=paper_b.abstract)
session.commit()

# Check paper A's claims against paper B's for contradictions
for claim in claims_a:
    relations = builder.build_relations_for_claim(claim, claims_b)
    for r in relations:
        print(r.relation_type, r.confidence, r.explanation)
session.commit()
```

Or via the agent tool registry:

```python
from src.core.tools import ToolRegistry
from src.rag.evidence_tool import register_evidence_tools

registry = ToolRegistry()
register_evidence_tools(registry)

await registry.execute("extract_claims", {"paper_id": "p1"})
result = await registry.execute("check_contradictions", {"paper_id": "p1"})
print(result["contradiction_count"], result["support_count"])
```

---

## Known Limitations (Phase 5)

- Heuristic extraction is cue-phrase based, not a real NLP claim parser —
  it will miss claims phrased unusually and occasionally over/under-fire.
  The `llm_extract_claims` extension point exists for exactly this reason.
- `compare_claims` polarity detection uses a fixed opposite-word list; it
  won't catch semantically opposite claims phrased without those cue words.
- No deduplication of near-identical claims yet (e.g. same finding restated
  across two chunks of the same paper) — worth revisiting once evaluated
  against RQ4's F1 ≥0.65 target in Phase 9.

---

## Next: Phase 6 — Python Sandbox

Move `execute_python_code` from Phase 2's basic import-blocking to a real
Docker-based sandbox with resource limits, building on the security
groundwork already flagged in PHASE2_SUMMARY.md.
