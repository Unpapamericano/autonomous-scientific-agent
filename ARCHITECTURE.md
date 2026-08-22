# ARCHITECTURE

## System Overview

```
User Query (Research Question)
    ↓
┌─────────────────────────────────────────────┐
│ Research Planner Agent                      │
│ - Parse & decompose question                │
│ - Generate search strategy                  │
│ - Plan analysis workflow                    │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Literature Search Agent                     │
│ - Query PubMed, arXiv, OpenAlex             │
│ - Rank results by relevance                 │
│ - Retrieve paper metadata                   │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Document Retrieval & Processing             │
│ - Fetch full PDFs or abstracts              │
│ - Extract text, figures, tables             │
│ - Parse citations & metadata                │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Scientific RAG Pipeline                     │
│ - Chunk documents                           │
│ - Generate embeddings (sentence-trans)      │
│ - Store in pgvector (PostgreSQL)            │
│ - Retrieve top-k relevant chunks            │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Muse Glimmer 30B Inference (Core)           │
│ - Tool-calling with structured schemas      │
│ - Multimodal analysis (text + charts)       │
│ - Long-context reasoning (131K tokens)      │
│ - Failure recovery & retries                │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Evidence Extraction & Verification          │
│ - Extract claims from LLM response          │
│ - Map claims → source documents             │
│ - Verify citations exist                    │
│ - Calculate grounding confidence            │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Python Data Analysis Sandbox                │
│ - Generate safe analysis code               │
│ - Execute in isolated Docker container      │
│ - Capture results, plots, statistics        │
│ - Detect invalid/malicious code             │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Critical Evaluation Agent                   │
│ - Assess study quality & bias               │
│ - Identify contradictions                   │
│ - Flag unsupported claims                   │
│ - Score evidence grounding                  │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Evidence Graph & Knowledge Base             │
│ - Build RDF/property graph structure        │
│ - Connect claims ↔ evidence ↔ papers        │
│ - Enable traceable lineage queries          │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Report Generation & Formatting              │
│ - Synthesize findings                       │
│ - Generate citations (BibTeX, RIS)          │
│ - Create human-readable markdown            │
│ - Include agent trajectory logs             │
└─────────────────────────────────────────────┘
    ↓
Final Scientific Report (Reproducible, Traceable)
```

## Core Components

### 1. **Inference Engine** (`src/core/inference.py`)

**Purpose**: Wrapper around Muse Glimmer 30B for local inference.

**Capabilities**:
- Quantized inference (4-bit, 8-bit, BF16)
- Simple generation
- Chat interface (single-turn)
- Structured JSON output (tool calling)
- Health checks

**Hardware Options**:
- Consumer GPU: RTX 4090 (4-bit, ~17GB VRAM)
- Mac: 32GB unified memory (4-bit)
- CPU: Fallback (slow)

### 2. **Literature Search** (`src/research/`)

**Purpose**: Retrieve scientific papers from multiple sources.

**Sources** (Phase 3):
- PubMed (biomedical)
- arXiv (preprints)
- OpenAlex (comprehensive)
- Semantic Scholar (if API access available)

**Outputs**:
- Paper metadata (title, authors, abstract, DOI)
- PDF URLs or full text
- Citation networks

### 3. **RAG Pipeline** (`src/rag/`)

**Purpose**: Embed, store, and retrieve relevant context for LLM.

**Components**:
- **Chunking**: Fixed size + sliding window
- **Embedding**: `sentence-transformers/all-mpnet-base-v2`
- **Storage**: PostgreSQL + pgvector
- **Retrieval**: Top-k similarity search

**Optimization**:
- Hybrid search (BM25 + semantic)
- Re-ranking via cross-encoder

### 4. **Security Layer** (`src/security/`)

**Purpose**: Defend against adversarial inputs and code injection.

**Threat Model**:
- Prompt injection via scientific papers
- Malicious code execution
- Data exfiltration
- Unauthorized tool calls

**Defenses**:
- Input sanitization & validation
- Sandboxed code execution (Docker)
- Rate limiting & quota enforcement
- Audit logging

### 5. **Analysis Sandbox** (`src/analysis/`)

**Purpose**: Execute data analysis code safely.

**Execution Environment**:
- Isolated Docker container per request
- Resource limits (CPU, memory, time)
- Restricted filesystem (read-only source, writable /tmp)
- No network access

**Supported Operations**:
- Python data manipulation (pandas, numpy)
- Statistics (scipy, scikit-learn)
- Visualization (matplotlib, seaborn)
- Scientific computing

### 6. **REST API** (`src/api/`)

**Purpose**: Expose system as HTTP endpoints.

**Endpoints** (Phase 2+):
- `POST /research` — Submit research question
- `GET /research/{id}` — Retrieve result
- `GET /research/{id}/trajectory` — Agent execution trace
- `GET /research/{id}/evidence` — Extracted evidence
- `GET /research/{id}/sources` — Retrieved papers
- `POST /evaluation/run` — Start benchmark

### 7. **Database** (`configs/`)

**Purpose**: Persistent storage for structured data.

**Schema** (PostgreSQL + pgvector):
- `papers` — Metadata, URLs, full text
- `chunks` — Text segments with embeddings
- `claims` — Extracted assertions
- `evidence` — Supporting passages
- `citations` — Paper-to-paper references
- `experiments` — Benchmark runs
- `trajectories` — Agent execution logs

## Data Flow

### Example: CRISPR Research Question

**User Input**:
```
"What are the latest advances in CRISPR-based therapeutics for inherited blindness?"
```

**Phase 1: Planning**
```json
{
  "research_question": "What are the latest advances in CRISPR-based therapeutics for inherited blindness?",
  "sub_questions": [
    "What are the main inherited blindness diseases targeted by CRISPR?",
    "What delivery mechanisms are used?",
    "What are clinical trial results?"
  ],
  "search_terms": [
    "CRISPR blindness",
    "RPE65 gene therapy",
    "inherited retinal disease CRISPR"
  ]
}
```

**Phase 2: Literature Search**
- Query PubMed for papers from 2022–2026
- Results: 150 papers, rank by relevance

**Phase 3: Document Processing**
- Retrieve abstracts & full PDFs
- Extract key claims, figures, methods

**Phase 4: RAG**
- Embed 5,000 document chunks
- Store in pgvector
- Retrieve top-10 for each sub-question

**Phase 5: Agent Reasoning**
- Muse Glimmer analyzes retrieved context
- Generates claims with confidence scores
- Tools: search, execute analysis, read tables

**Phase 6: Evidence Grounding**
- Verify each claim is cited in source documents
- Calculate citation precision/recall

**Phase 7: Data Analysis**
- Extract clinical trial success rates
- Generate comparison table
- Sandbox execution of Python analysis

**Phase 8: Evaluation**
- Critical review of evidence
- Detect contradictions between studies
- Identify gaps & limitations

**Phase 9: Report**
- Generate markdown report
- Include citations, figures, evidence links
- Agent trajectory for reproducibility

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM Inference** | Unsloth + llama.cpp | Quantized Muse Glimmer |
| **Orchestration** | LangChain / LLaMA-Index | Agentic workflows |
| **Vector Search** | PostgreSQL + pgvector | Semantic retrieval |
| **Embeddings** | Sentence-Transformers | Text representation |
| **REST API** | FastAPI | HTTP endpoints |
| **Code Sandbox** | Docker + resource limits | Safe execution |
| **Database** | PostgreSQL | Structured storage |
| **Observability** | Structlog + JSON logging | Audit trail |
| **Testing** | pytest | Unit/integration tests |
| **Containerization** | Docker + docker-compose | Reproducible deployment |

## Phases & Milestones

- ✓ **Phase 1**: Minimal inference (current)
- **Phase 2**: Tool calling & orchestration
- **Phase 3**: Literature retrieval APIs
- **Phase 4**: RAG pipeline
- **Phase 5**: Evidence graph
- **Phase 6**: Python sandbox
- **Phase 7**: Multimodal analysis
- **Phase 8**: Security layer
- **Phase 9**: Evaluation framework
- **Phase 10**: Dashboard
- **Phase 11**: Benchmarks
- **Phase 12**: Research report

---

## Design Decisions

### Why Muse Glimmer 30B?
- Optimized for local agentic workflows (no API dependency)
- Strong on tool-calling & long-context
- Multimodal (text + image)
- Apache 2.0 license (no restrictions)

### Why PostgreSQL + pgvector?
- Native vector search (pgvector extension)
- Structured metadata (papers, claims, evidence)
- Transaction support for consistency
- Rich query language (SQL)

### Why Sandbox for Code Execution?
- **Security**: Arbitrary code execution is dangerous
- **Isolation**: Prevents accidental state corruption
- **Resource limits**: Prevents DoS
- **Auditability**: Every execution is logged

### Why Multiple Retrieval Sources?
- **PubMed**: Biomedical domain expertise
- **arXiv**: Preprints & frontier research
- **OpenAlex**: Cross-disciplinary coverage
- **Diversification**: Reduces bias from single source

---

## Error Handling & Failure Recovery

### Graceful Degradation

| Failure | Recovery |
|---|---|
| Model loading fails | Fallback to smaller model or CPU |
| Paper retrieval times out | Continue with cached results |
| Code execution crashes | Return error + sandbox logs |
| API rate limit exceeded | Retry with exponential backoff |
| Evidence grounding fails | Flag as "unverified" in report |

### Observability

Every action is logged with:
```json
{
  "timestamp": "2026-01-15T10:30:45.123Z",
  "agent": "research_planner",
  "action": "decompose_question",
  "input": "...",
  "output": "...",
  "latency_ms": 234,
  "status": "success"
}
```

User can query: `GET /research/{id}/trajectory` to see full execution.

---

## Security Model

### Threat Model

1. **Prompt Injection** — Malicious text in retrieved papers
   - **Defense**: Input sanitization, format validation
   
2. **Code Injection** — Malicious Python in generated analysis
   - **Defense**: AST analysis, sandboxed execution
   
3. **Data Exfiltration** — Agent exfiltrates sensitive data
   - **Defense**: No network access in sandbox, audit logging
   
4. **Unauthorized Tool Calls** — Agent calls tools it shouldn't
   - **Defense**: Schema validation, rate limiting

### Principle of Least Privilege

- API has read-only access to most data
- Code execution sandbox has no network
- Database user has minimal permissions
- Models are loaded read-only

---

## Future Enhancements

- Multi-turn conversation with context window management
- Fine-tuning on domain-specific scientific tasks
- Distributed inference (multi-GPU)
- Real-time streaming output
- Integration with scientific software (R, Julia)
- Blockchain-based evidence provenance
