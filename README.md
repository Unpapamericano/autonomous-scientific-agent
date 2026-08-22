# Autonomous Scientific Research Agent

A production-grade, research-oriented autonomous AI agent powered by **Meta Muse Glimmer 30B**. This system combines multimodal inference, agentic tool use, scientific RAG, evidence verification, Python-based data analysis, and security evaluation to perform complex scientific literature research workflows.

**Status**: Phase 3 (Literature Search APIs) ✅ COMPLETE  
**Total Code**: 4,900+ LOC  
**Ready for**: Phase 4 (Vector Search & RAG)

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 15+ (optional, for Phase 3+)
- CUDA 12.1+ (RTX 4090, A100) OR CPU (for Phase 1 inference)
- 24–32 GB VRAM (for Phase 1 with 4-bit quantization)

### Installation

```bash
# Clone & setup
git clone https://github.com/[your-repo]/autonomous-scientific-agent.git
cd autonomous-scientific-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify Muse Glimmer loads
python src/core/inference.py
```

### Run Tests (No GPU Required)

```bash
make test                  # All tests
make test-integration      # Integration tests only
make demo-phase2           # Phase 2 tool demo (no GPU)
```

### Search Literature (Phase 3)

```python
from src.research.apis import AggregatedSearchClient

client = AggregatedSearchClient()
papers = await client.search(
    "CRISPR inherited blindness",
    limit=20,
    year_from=2020,
)
for paper in papers:
    print(f"{paper.title} ({paper.year})")
```

### Run Agent with LLM (Phase 1, GPU Required)

```python
from src.core.orchestration import ResearchAgent, AgentState

agent = ResearchAgent()
state = AgentState()

answer, state = await agent.query(
    "What are the latest CRISPR advances for inherited blindness?",
    session_state=state
)
print(answer)
```

## Architecture

```
User Query
    ↓
Research Planner (Parse question → decompose)
    ↓
Literature Search Agent (PubMed, arXiv, OpenAlex APIs)
    ↓
Document Retrieval (Fetch & validate papers)
    ↓
Scientific RAG (Chunk, embed, retrieve relevant context)
    ↓
Evidence Extraction (Structured claim ← source mapping)
    ↓
Python Sandbox (Execute analysis code safely)
    ↓
Evidence Grounding (Verify claims ← citations)
    ↓
Critical Evaluation (Quality, bias, limitations)
    ↓
Final Scientific Report (Traceable, reproducible)
```

## Phases

| Phase | Name | Status | LOC | Deliverables |
|---|---|---|---|---|
| 1 | Minimal Inference | ✅ | 1,200 | Muse Glimmer loading, inference |
| 2 | Tool Calling & Orchestration | ✅ | 1,200 | Tool registry, agent orchestration |
| 3 | Literature Search APIs | ✅ | 1,200 | PubMed, arXiv, OpenAlex, PostgreSQL |
| 4 | Vector Search & RAG | 🔜 | 800 | Embeddings, pgvector, semantic search |
| 5 | Evidence Graph | 🔜 | 600 | Claims, evidence linking |
| 6 | Python Sandbox | 🔜 | 400 | Docker sandbox, safe execution |
| 7 | Multimodal Documents | 🔜 | 400 | PDF parsing, figure extraction |
| 8 | Security Hardening | 🔜 | 400 | Prompt injection defense |
| 9 | Evaluation Framework | 🔜 | 300 | Benchmarks, metrics |
| 10 | Dashboard & UI | 🔜 | 500 | Web interface, visualization |
| 11 | Deployment | 🔜 | 300 | Docker, cloud, scaling |
| 12 | Final Integration | 🔜 | 200 | Testing, documentation |

## Documentation

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** — Complete project overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design & components
- **[RESEARCH.md](RESEARCH.md)** — Research questions & methodology
- **[PHASE1_SUMMARY.md](PHASE1_SUMMARY.md)** — Phase 1 report
- **[PHASE2_SUMMARY.md](PHASE2_SUMMARY.md)** — Phase 2 report
- **[PHASE3_SUMMARY.md](PHASE3_SUMMARY.md)** — Phase 3 report

## Research Questions (Phase 11+)

Evaluates Muse Glimmer 30B on:

- **RQ1**: Can local models do useful research? (Target: ≥70% task completion)
- **RQ2**: Does RAG reduce hallucination? (Target: precision >0.85)
- **RQ3**: Does tool use improve quality? (Target: +40% completion)
- **RQ4**: Can agents detect contradictions? (Target: F1 ≥0.65)
- **RQ5**: Resistant to prompt injection? (Target: <10% success)
- **RQ6**: Muse vs. Gemma 4 / Qwen 3.6? (Target: Muse +20%)
- **RQ7**: Quality-cost-latency tradeoff? (Target: Clear Pareto frontier)

See `RESEARCH.md` for methodology.

## Hardware Requirements

| Mode | VRAM | Hardware |
|---|---|---|
| 4-bit (recommended) | 17 GB | RTX 4090, Mac 32GB |
| 8-bit | 34 GB | A100 80GB, DGX |
| Full BF16 | 58 GB | Professional GPU |

## Model Details

- **Model**: Meta Muse Glimmer-30B
- **Context**: 131,072 tokens
- **Multimodal**: Text + Image → Text
- **License**: Apache 2.0
- **Knowledge Cutoff**: January 4, 2026

## Important Limitations

⚠️ **Do NOT use this system for**:
- Medical advice, diagnosis, or treatment recommendations
- Making clinical decisions without human review
- High-stakes scientific claims without expert validation

This is a **research tool for literature analysis**, not a clinical decision-making system.

## Contributing

See `CONTRIBUTING.md` for development guidelines.

## License

Apache 2.0 — See `LICENSE` file.

## Citation

If you use this project, cite as:

```bibtex
@software{scientific_agent_2026,
  title={Autonomous Scientific Research Agent with Muse Glimmer 30B},
  author={Your Name},
  year={2026},
  url={https://github.com/[your-repo]/autonomous-scientific-agent}
}
```

## Contact

Questions? Open an issue on GitHub or contact [your-email].

---

**Last updated**: Phase 1, [Date]  
**Maintainer**: [Your Name]
