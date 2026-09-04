# PHASE 4: VECTOR SEARCH & RAG

## Overview

Phase 4 adds semantic retrieval on top of Phase 3's literature search: papers
and abstract chunks are embedded, stored (pgvector when available, JSON
fallback otherwise), and retrievable by semantic similarity for grounded,
citation-ready context.

**Status**: ✅ COMPLETE
**Tests**: 16 new tests (all passing), 30 total passing across the project

---

## What Was Built

### 1. Embeddings (`src/rag/embeddings.py`)
- `EmbeddingGenerator` — lazy-loads `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim) so importing this module doesn't require a model download.
- `embed_text`, `embed_batch`, `similarity`, `rank_by_similarity`.
- `chunk_text(text, chunk_size, overlap)` — word-based chunking with overlap for RAG-friendly splitting.

### 2. Vector Search (`src/rag/vector_search.py`)
- `VectorSearchEngine` — semantic search over `DocumentChunk` and `Paper.abstract_embedding`.
- Uses pgvector's `cosine_distance` operator when pgvector is installed; falls back to an in-memory numpy ranking otherwise (used automatically in tests/dev).
- `backfill_chunk_embeddings` / `backfill_paper_embeddings` for embedding records that predate Phase 4.

### 3. RAG Pipeline (`src/rag/pipeline.py`)
- `RAGPipeline.ingest_query()` — runs a Phase 3 literature search, stores papers, chunks the abstract, embeds chunks, and stores everything (dedupes on re-ingest).
- `RAGPipeline.retrieve()` — embeds a question and returns a `RAGContext` with ranked, cited chunks plus a ready-to-paste prompt context string.

### 4. Agent Tool (`src/rag/rag_tool.py`)
- New `retrieve_context` tool (`ToolType.RETRIEVE`) registered separately from the Phase 2 stateless tools (this one needs a DB session).
- Intended flow: agent calls `search_literature` → `retrieve_context` to answer with grounded citations instead of parametric memory.

### 5. Model Changes (`src/rag/models.py`)
- **Bug fix**: SQLAlchemy's Declarative API reserves the attribute name `metadata` — every model previously used `metadata = Column(...)`, which raised `InvalidRequestError` at import time. Renamed the Python attribute to `extra_metadata` (DB column name unchanged) across all 8 affected models.
- Added `abstract_embedding` + `embedding_model` to `Paper`.
- Added `embedding_model` to `DocumentChunk`.
- `embedding_column()` helper picks pgvector `Vector(384)` or falls back to `JSON`.

### 6. Tests (`tests/integration/test_rag_pipeline.py`)
- Chunking edge cases (empty, short, long, overlap).
- Embedding generator with a mocked backend (no GPU/model download needed).
- Cosine similarity + ranking correctness.
- RAGPipeline ingestion and retrieval with fully mocked DB/session/search client.
- In-memory vector search fallback ranking.

---

## Bugs Found & Fixed During Verification

1. **`ModuleNotFoundError: httpx`** — declared in `requirements.txt` but not installed in the active environment; installed it.
2. **`ModuleNotFoundError: pytest-asyncio`** — same; installed it.
3. **`sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved`** — real bug in Phase 3 models that would have broken every table at import time in any real run. Fixed by renaming to `extra_metadata` and updating `repositories.py` accordingly.
4. **`Evaluation.__repr__` f-string bug** — `f"{self.accuracy:.2f if self.accuracy else 'N/A'}"` is invalid (format spec can't contain a ternary); fixed with a precomputed `acc` string.

---

## Usage

```python
from src.rag.database import init_database, get_session
from src.rag.pipeline import RAGPipeline

db = init_database()
session = get_session()
pipeline = RAGPipeline(session)

# 1. Search + ingest
await pipeline.ingest_query("CRISPR inherited blindness", limit=10)

# 2. Ask a grounded question
context = pipeline.retrieve("What is the success rate of RPE65 gene therapy?")
print(context.to_prompt_context())
```

Or via the agent tool registry:

```python
from src.core.tools import ToolRegistry
from src.rag.rag_tool import register_rag_tools

registry = ToolRegistry()
register_rag_tools(registry)
result = await registry.execute("retrieve_context", {"question": "..."})
```

---

## Next: Phase 5 — Evidence Graph & Contradiction Detection

Builds on the `Claim` and `Evidence` models already scaffolded in Phase 3, using Phase 4's retrieval to link claims to supporting/contradicting chunks.
