# Changelog

All notable project changes are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses semantic
versioning where releases are published.

## [Unreleased]

### Added
- Repository hygiene, contributor guidance, community templates, and a
  clearly separated cloud-pipeline demonstration area.
- A single `pyproject.toml` dependency and packaging configuration.

## Historical development phases

### Phase 1 - Local model inference
Established the local LLM inference foundation with device management,
quantization support, and caching.

### Phase 2 - Tool calling and orchestration
Added multi-turn orchestration, a tool registry, schemas, and safe tool
execution patterns for research tasks.

### Phase 3 - Literature APIs and database
Connected literature services including PubMed, arXiv, and OpenAlex with
parallel search, deduplication, and persistence.

### Phase 4 - Vector search and RAG
Built document embeddings, vector retrieval, and grounded retrieval-augmented
generation workflows.

### Phase 5 - Evidence graph
Added claim and evidence relationships, repository operations, and
contradiction detection support.

### Phase 6 - Code sandbox
Introduced bounded Python execution with resource and network controls for
reproducible scientific analysis.

### Phase 7 - Multimodal extraction
Added PDF extraction, OCR, multimodal indexing, and document processing
support for scientific sources.

### Phase 8 - Security hardening
Implemented prompt-injection detection, input sanitization, and security audit
logging around agent interactions.

### Phase 9 - Evaluation framework
Added benchmark datasets, RQ1-RQ7 metrics, evaluator orchestration, and report
generation for measuring research quality.

### Phase 10 - Dashboard and UI
Added dashboard report management, metrics views, health status, and the
responsive research-facing interface.

### Phase 11 - Live research synthesis
Added adaptive analysis, evidence governance, clinical-trial monitoring,
multiple-sclerosis research examples, and bounded delivery workflows.
