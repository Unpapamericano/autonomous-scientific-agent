# System Architecture

## Overview

Autonomous Scientific Research Agent is a modular, production-ready system for autonomous literature research. It combines:

- **Local LLM** (Muse Glimmer 30B, 4-bit quantized)
- **Multi-source retrieval** (PubMed, arXiv, OpenAlex)
- **Vector search** (pgvector + semantic embeddings)
- **Evidence graphs** (claims, contradictions, support links)
- **Safe execution** (Docker sandbox with resource limits)
- **Security layer** (injection detection + sanitization)
- **Comprehensive evaluation** (RQ1–RQ7 benchmarks)

---

## Component Stack

```
┌──────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                           │
│  ├─ Dashboard (HTML/JSON)                                    │
│  ├─ CLI (scripts/run_agent.py)                               │
│  └─ Python API (orchestration.py)                            │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│          AGENT ORCHESTRATION (Phase 2)                       │
│  ├─ Multi-turn conversation                                  │
│  ├─ Tool calling & JSON parsing                              │
│  ├─ State management                                         │
│  └─ Error recovery                                           │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼──┐  ┌─────────▼──────┐  ┌──────▼──┐
    │Tools │  │ LLM Inference  │  │ Database │
    └───┬──┘  │ (Phase 1)      │  │(Phase 3) │
        │     └────────────────┘  └──────────┘
    ┌───▼────────────────────────────────────┐
    │   TOOL IMPLEMENTATIONS                 │
    ├─ search_literature (Phase 3)           │
    ├─ retrieve_context (Phase 4)            │
    ├─ extract_claims (Phase 5)              │
    ├─ check_contradictions (Phase 5)        │
    ├─ execute_code (Phase 6)                │
    ├─ extract_pdf (Phase 7)                 │
    └─ detect_injection (Phase 8)            │
    │                                        │
    └────────────────┬───────────────────────┘
                     │
    ┌────────────────┼───────────────────────┐
    │                │                       │
┌───▼──────┐  ┌──────▼────────┐  ┌──────────▼──┐
│Retrieval │  │ RAG Pipeline   │  │  Evidence   │
│(Phase 3) │  │   (Phase 4)    │  │   Graph     │
└──────────┘  └────────────────┘  │  (Phase 5)  │
                    │              └─────────────┘
    ┌───────────────▼──────────────┐
    │  VECTOR SEARCH & EMBEDDINGS  │
    │  ├─ Sentence Transformers    │
    │  ├─ pgvector (PostgreSQL)    │
    │  └─ FAISS (fallback)         │
    └──────────────────────────────┘
                    │
    ┌───────────────▼──────────────┐
    │   DOCUMENT PROCESSING        │
    │  ├─ PDF extraction (Phase 7) │
    │  ├─ Table parsing            │
    │  ├─ OCR (fallback)           │
    │  └─ Metadata extraction      │
    └──────────────────────────────┘
                    │
    ┌───────────────▼──────────────┐
    │   SECURITY LAYER (Phase 8)   │
    │  ├─ Injection detection      │
    │  ├─ Input sanitization       │
    │  ├─ Audit logging            │
    │  └─ Code validation          │
    └──────────────────────────────┘
```

---

## Data Flow

### Research Query Workflow

```
1. USER INPUT
   └─> Injection Detection (Phase 8)
       ├─ Block if CRITICAL
       └─ Sanitize input

2. AGENT ORCHESTRATION (Phase 2)
   └─> Forward to LLM with context

3. LLM DECISION (Phase 1)
   └─> Call appropriate tool

4. TOOL EXECUTION
   
   a) SEARCH_LITERATURE (Phase 3)
      ├─ Query PubMed, arXiv, OpenAlex
      ├─ Retrieve papers & metadata
      ├─ Store in PostgreSQL
      └─> Send to RAG Pipeline

   b) RETRIEVE_CONTEXT (Phase 4)
      ├─ Query vector search (pgvector)
      ├─ Rank by relevance
      ├─> Return chunks & scores

   c) EXTRACT_CLAIMS (Phase 5)
      ├─ Parse paper abstracts/text
      ├─ Extract structured claims
      ├─> Link to evidence graph

   d) CHECK_CONTRADICTIONS (Phase 5)
      ├─ Compare claim pairs
      ├─ Semantic similarity check
      ├─-> Flag contradictions

   e) EXECUTE_CODE (Phase 6)
      ├─ Sanitize code
      ├─ Run in Docker sandbox
      ├─ Resource limits (512MB RAM)
      ├─-> Return results

   f) EXTRACT_PDF (Phase 7)
      ├─ Parse PDF (pdfplumber)
      ├─ Extract text/tables/figures
      ├─ OCR fallback
      ├─-> Index to vector store

5. EVIDENCE AGGREGATION (Phase 5)
   ├─ Collect claims & contradictions
   ├─ Build evidence graph
   └─-> Generate summary

6. LLM SYNTHESIS (Phase 1)
   └─> Generate final answer

7. EVALUATION & LOGGING (Phase 8-9)
   ├─ Record metrics
   ├─ Update dashboard
   └─> Audit trail
```

---

## Phase Responsibilities

### Phase 1: LLM Inference
**Responsibility**: Language understanding & generation
- Load Muse Glimmer 30B (4-bit quantized)
- Parse user queries
- Understand tool descriptions
- Generate JSON tool calls
- Synthesize answers from context

**Dependencies**: `torch`, `transformers`
**Files**: `src/core/inference.py`

### Phase 2: Orchestration
**Responsibility**: Multi-turn conversation management
- Maintain conversation history
- Parse tool calls from LLM output
- Execute tools with error handling
- Format tool results for LLM
- Implement reasoning loops

**Dependencies**: Phase 1, `pydantic`
**Files**: `src/core/orchestration.py`, `src/core/tools.py`

### Phase 3: Literature Search
**Responsibility**: Retrieve scientific papers
- Query PubMed, arXiv, OpenAlex in parallel
- Deduplicate results
- Rank by relevance
- Store in PostgreSQL
- Cache results

**Dependencies**: `biopython`, `arxiv`, `requests`, `sqlalchemy`
**Files**: `src/research/apis.py`, `src/rag/database.py`

### Phase 4: RAG Pipeline
**Responsibility**: Semantic retrieval & ranking
- Generate embeddings (Sentence Transformers)
- Store vectors in pgvector
- Search by semantic similarity
- Re-rank results
- FAISS fallback for in-memory

**Dependencies**: `sentence-transformers`, `pgvector`, `faiss-cpu`
**Files**: `src/rag/embeddings.py`, `src/rag/vector_search.py`

### Phase 5: Evidence Graph
**Responsibility**: Claim extraction & contradiction detection
- Extract claims from papers
- Link claims to source documents
- Detect contradictions between claims
- Build evidence support/dispute graphs
- Aggregate evidence strength

**Dependencies**: Phase 4, `networkx`
**Files**: `src/rag/claim_extraction.py`, `src/rag/evidence_graph.py`

### Phase 6: Code Sandbox
**Responsibility**: Safe code execution
- Validate Python code (block dangerous imports)
- Execute in Docker container (512MB RAM, no network)
- Capture output & errors
- Fallback to local execution
- Enforce timeout limits

**Dependencies**: `docker`, `subprocess`
**Files**: `src/analysis/sandbox.py`, `Sandbox.dockerfile`

### Phase 7: PDF Processing
**Responsibility**: Multimodal document extraction
- Extract text from PDFs (pdfplumber)
- Detect & parse tables
- Identify figures & captions
- OCR fallback (pytesseract)
- Index extracted content

**Dependencies**: `pdfplumber`, `pytesseract`, `Pillow`
**Files**: `src/rag/document_extraction.py`, `src/rag/multimodal_indexing.py`

### Phase 8: Security
**Responsibility**: Attack detection & input validation
- Detect prompt injection (7 attack types)
- Sanitize inputs (XSS, length, control chars)
- Block dangerous patterns
- Audit logging (injection, code execution, tool access)
- Confidence scoring

**Dependencies**: `regex`
**Files**: `src/security/prompt_injection_detector.py`, `src/security/input_sanitizer.py`

### Phase 9: Evaluation
**Responsibility**: Benchmarking framework
- Define RQ1–RQ7 metrics
- Manage benchmark datasets
- Orchestrate evaluation runs
- Generate reports (JSON/Markdown)
- Collect system metrics

**Dependencies**: `dataclasses`, `datetime`
**Files**: `src/evaluation/metrics.py`, `src/evaluation/benchmarks.py`

### Phase 10: Dashboard
**Responsibility**: Visualization & monitoring
- Store evaluation reports
- Visualize metrics (Chart.js)
- Monitor system health (CPU, memory)
- Export results (HTML, JSON)
- Health checks

**Dependencies**: `flask` (optional), `psutil`
**Files**: `src/dashboard/app.py`, `src/dashboard/metrics_view.py`

---

## Database Schema

### Core Tables (PostgreSQL)

```sql
-- Papers
CREATE TABLE papers (
    id UUID PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    authors TEXT[],
    published_date DATE,
    source VARCHAR(50),  -- pubmed, arxiv, openalex
    url TEXT,
    doi TEXT UNIQUE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Document Chunks (for RAG)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    paper_id UUID REFERENCES papers(id),
    content TEXT,
    chunk_index INTEGER,
    start_char INTEGER,
    end_char INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector Embeddings (pgvector)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    chunk_id UUID REFERENCES document_chunks(id),
    embedding vector(384),  -- Sentence Transformers dimension
    similarity_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);

-- Claims (Evidence Graph)
CREATE TABLE claims (
    id UUID PRIMARY KEY,
    paper_id UUID REFERENCES papers(id),
    claim_text TEXT,
    confidence FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Contradictions
CREATE TABLE contradictions (
    id UUID PRIMARY KEY,
    claim_a_id UUID REFERENCES claims(id),
    claim_b_id UUID REFERENCES claims(id),
    contradiction_score FLOAT,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Evaluation Results
CREATE TABLE evaluation_results (
    id UUID PRIMARY KEY,
    run_id VARCHAR(255),
    test_id VARCHAR(255),
    metric_name VARCHAR(255),
    metric_value FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Configuration Flow

```
config/config.yaml (YAML)
         │
         ▼
src/config/__init__.py (Loader)
         │
         ▼
Pydantic Config Models
         │
    ┌────┴────┬────────┬──────────┐
    │          │        │          │
    ▼          ▼        ▼          ▼
 Phase 1     Phase 3  Phase 4   Phase 6
 (LLM)     (Database)(Search) (Sandbox)
```

---

## Error Handling

### Resilience Pattern

```python
try:
    primary_approach()
except Exception as e:
    log_error(e)
    fallback_approach()
```

### Examples

| Component | Primary | Fallback |
|-----------|---------|----------|
| Vector Search | pgvector | FAISS (in-memory) |
| PDF Extraction | pdfplumber | pytesseract (OCR) |
| Code Execution | Docker | Local (safe mode) |
| Database | PostgreSQL | SQLite |
| Embeddings | Sentence Transformers | TF-IDF (last resort) |

---

## Performance Characteristics

### Latency by Component

```
┌─ Search Literature ─────────── 1-5 seconds ┐
├─ Vector Search (10 results) ── 100-500 ms   │
├─ PDF Extraction ───────────── 500 ms-2 s    │
├─ LLM Inference ────────────── 2-10 seconds  │
├─ Contradiction Detection ───── 100-200 ms   │
└─ Dashboard Rendering ────────── 50-200 ms   ┘
  
Total end-to-end: 5-30 seconds per query
```

### Memory Usage

```
┌─ LLM (4-bit, 70B) ─────────── ~14 GB ─┐
├─ Vector Store (pgvector) ────── 1-5 GB │
├─ Sandbox Docker Image ──────── 500 MB │
├─ Cache (embeddings) ──────────── <2 GB │
└─ Database (PostgreSQL) ──────── 5-10 GB┘

Total: 20-30 GB (can be reduced with smaller models)
```

---

## Scalability Considerations

### Current (Phase 10)
- Single-threaded test execution
- In-process evaluation
- Local caching

### Phase 11+
- Distributed evaluation (multi-worker)
- Batch processing
- Result aggregation
- Horizontal scaling (multiple agents)

### Future Improvements
- Multi-GPU inference
- Sharded vector store
- Message queues (for tool calls)
- Microservices architecture

---

## Security Architecture

```
┌──────────────────────────────┐
│    User Input / PDF Content  │
└────────────┬─────────────────┘
             │
     ┌───────▼────────┐
     │ Injection Check │ ─────> Block if CRITICAL
     │                │ ─────> Warn if HIGH/MEDIUM
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │  Sanitization  │ ─────> Remove XSS, control chars
     │                │ ─────> Enforce length limits
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │ Code Validation│ ─────> Block dangerous imports
     │                │ ─────> Validate syntax
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │ Safe Execution │ ─────> Docker sandbox
     │                │ ─────> Resource limits
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │ Audit Logging  │ ─────> Record all events
     │                │ ─────> Compliance trail
     └────────────────┘
```

---

## Testing Strategy

```
Unit Tests (fast, isolated)
├─ Phase 1: LLM inference mocking
├─ Phase 2: Tool calling logic
├─ Phase 3: API response parsing
├─ Phase 4: Embeddings computation
├─ Phase 5: Claim extraction
├─ Phase 6: Code validation
├─ Phase 7: PDF parsing
├─ Phase 8: Security detection
├─ Phase 9: Metrics calculation
└─ Phase 10: Dashboard rendering

Integration Tests (slower, real components)
├─ Database operations
├─ Literature search (with mocks)
├─ RAG pipeline end-to-end
├─ Evidence graph building
├─ Sandbox execution
└─ Dashboard queries

Evaluation Tests (benchmarks)
├─ RQ1–RQ7 metrics
├─ Benchmark datasets
├─ Report generation
└─ Dashboard export
```

---

## Deployment

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Staging
```bash
docker-compose -f docker-compose.staging.yml up
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up
# or Kubernetes
kubectl apply -f k8s/
```

---

## Future Enhancements

1. **Multi-modal LLMs** (GPT-4V, Claude 3.5 Vision)
2. **Distributed inference** (vLLM, Ray)
3. **Fine-tuned models** (domain-specific)
4. **Real-time updates** (WebSocket dashboard)
5. **Automated remediation** (self-healing)
6. **Advanced UI** (React/Vue dashboard)
7. **Export formats** (PDF reports, LaTeX)
8. **Multi-language support**

---

**Last Updated**: Phase 10 Complete  
**Architecture Version**: 1.0
