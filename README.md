# Autonomous Scientific Research Agent

A production-grade, research-oriented autonomous AI agent powered by **Meta Muse Glimmer 30B**. This system combines multimodal inference, agentic tool use, scientific RAG, evidence verification, Python-based data analysis, and security evaluation to perform complex scientific literature research workflows.

**Status**: Phase 1 (Minimal Inference) — In Progress

## Quick Start (Phase 1)

### Prerequisites
- Python 3.10+
- CUDA 12.1+ (RTX 4090, A100) OR CPU (slower)
- 24–32 GB VRAM (with 4-bit quantization)

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

### First Inference (Minimal)

```python
from src.core.inference import MuseGlimmerInference

model = MuseGlimmerInference(quantization="4-bit")
response = model.chat("What are the main mechanisms of CRISPR gene editing?")
print(response)
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

- **Phase 1**: Minimal Glimmer Inference ✓ (current)
- **Phase 2**: Tool-calling framework
- **Phase 3**: Literature retrieval (PubMed, arXiv)
- **Phase 4**: Scientific RAG
- **Phase 5**: Evidence graph & claim extraction
- **Phase 6**: Python sandbox & data analysis
- **Phase 7**: Multimodal document understanding
- **Phase 8**: Security layer (prompt injection detection)
- **Phase 9**: Evaluation framework
- **Phase 10**: Dashboard (Gradio/Streamlit)
- **Phase 11**: Benchmark experiments
- **Phase 12**: Research report & publication

## Documentation

- `ARCHITECTURE.md` — System design & components
- `RESEARCH.md` — Research questions & methodology
- `EVALUATION.md` — Benchmark definitions & metrics
- `SECURITY.md` — Threat model & defenses

## Evaluation & Benchmarks

This project evaluates Muse Glimmer 30B against:

- **SciCode** — Scientific problem-solving with code
- **Custom Scientific Dataset** — Literature analysis tasks
- **Comparative**: Gemma4-31B, Qwen3.6-27B

See `EVALUATION.md` for metrics & reproducibility.

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
