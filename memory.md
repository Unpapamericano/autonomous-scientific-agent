# memory.md - Development Context & Project Memory

## Project Essentials

### Quick Facts
- **Project**: Defense Intelligence Analysis Platform
- **Author**: Doncho Panayotov
- **GitHub**: https://github.com/Unpapamericano/autonomous-scientific-agent
- **Email**: doncho.ap@gmail.com
- **Language**: English (for code/docs), German (for culture/context)
- **Python Version**: 3.11+
- **Status**: Production-Ready

### Key Directories
```
C:\Users\49174\projects\autonomous-scientific-agent\
├── src/                    # 11,500+ LOC production code
├── tests/                  # 600+ tests
├── k8s/                    # Kubernetes
├── .github/workflows/      # CI/CD
├── config/                 # Configuration
├── scripts/                # Utilities
└── docs/                   # Documentation
```

---

## Technical Stack

### Core Technologies
- **Primary Language**: Python 3.11+
- **Web Framework**: FastAPI (async, high-performance)
- **ML Frameworks**: PyTorch, Transformers (HuggingFace)
- **Model**: Meta Muse Glimmer 30B (quantized 4-bit)
- **Databases**: PostgreSQL, Redis
- **Containerization**: Docker, Kubernetes
- **CI/CD**: GitHub Actions
- **Testing**: pytest (600+ tests)
- **API Docs**: OpenAPI/Swagger

### Supporting Languages
- **Go**: Performance-critical services (<50ms)
- **C++**: Quantum computing & mathematical optimization
- **JavaScript/React**: Frontend dashboards

### Key Packages
```
fastapi==0.109.0           # Web framework
pydantic==2.5.0            # Data validation
pytorch::pytorch           # Deep learning
transformers==4.35.0       # Language models
sqlalchemy==2.0.0          # ORM
redis==5.0.0               # Caching
pytest==7.4.0              # Testing
```

---

## Architecture Principles

### Design Philosophy
1. **Layered Architecture**
   - API Layer (FastAPI endpoints)
   - Service Layer (business logic)
   - Domain Layer (entities, models)
   - Infrastructure Layer (DB, cache, APIs)

2. **SOLID Principles**
   - Single Responsibility
   - Open/Closed
   - Liskov Substitution
   - Interface Segregation
   - Dependency Inversion

3. **Clean Code**
   - Type hints throughout
   - Comprehensive docstrings
   - Meaningful variable names
   - Small, focused functions
   - Modular design

4. **Testing Strategy**
   - Unit tests for business logic
   - Integration tests for workflows
   - Performance tests for SLAs
   - Security tests for vulnerabilities

### Performance Targets
- **API Latency**: <50ms (99th percentile)
- **Throughput**: 1000+ requests/second
- **Model Inference**: 100-500ms
- **Memory**: <4GB (with quantization)
- **Startup**: <30 seconds
- **Uptime**: 99.95% SLA

---

## Development Workflow

### Daily Development Loop
1. **Start Day**: `git pull origin main`
2. **Create Branch**: `git checkout -b feature/my-feature`
3. **Write Test**: Create test in `tests/unit/`
4. **Implement**: Write code in `src/`
5. **Test**: `pytest tests/` until green
6. **Quality**: `black src/` + `pylint src/` + `mypy src/`
7. **Commit**: `git commit -m "[module] Description"`
8. **Push**: `git push origin feature/my-feature`
9. **PR**: Create PR on GitHub

### Before Merge
- [ ] All tests passing (600+)
- [ ] Coverage >95%
- [ ] Code formatted (black)
- [ ] Linting passed (pylint)
- [ ] Types checked (mypy)
- [ ] Documentation updated
- [ ] No security issues
- [ ] No performance regressions

---

## Key Features & Modules

### Intelligence Services
| Module | Purpose | Status | Tests |
|--------|---------|--------|-------|
| conflict_resolver | Detects contradictions | ✅ | 25+ |
| uncertainty_quantifier | Confidence scoring | ✅ | 20+ |
| insight_generator | Recommendations | ✅ | 30+ |
| synthesizer | Multi-source synthesis | ✅ | 15+ |

### API Endpoints
| Endpoint | Method | Purpose | Latency |
|----------|--------|---------|---------|
| `/api/v1/analyze` | POST | Intelligence analysis | <50ms |
| `/api/v1/threats` | POST | Threat detection | <100ms |
| `/api/v1/sources` | GET | List sources | <20ms |
| `/health` | GET | Health check | <10ms |

### Security Features
- ✅ Prompt injection detection
- ✅ OAuth2 authentication
- ✅ RBAC (role-based access control)
- ✅ Encryption at rest/transit
- ✅ Audit logging
- ✅ Rate limiting

---

## Testing Philosophy

### Test Organization
```
tests/
├── unit/                   # Fast, isolated (200+ tests)
├── integration/            # Component interaction (250+ tests)
├── performance/            # Load/stress (50+ tests)
└── security/               # Vulnerabilities (100+ tests)
```

### Test Coverage Requirements
- **Critical paths**: 100% coverage
- **Business logic**: 95%+ coverage
- **Overall**: >95% coverage
- **Excluded**: Configuration, third-party integrations

### Writing Tests
```python
# Unit test example
def test_conflict_detection():
    resolver = ConflictResolver()
    result = resolver.detect_contradictions(study1, study2)
    assert result.conflict_type == ConflictType.QUANTITATIVE
    assert result.severity == "high"

# Integration test example
@pytest.mark.asyncio
async def test_end_to_end_analysis():
    result = await agent.analyze_intelligence(query)
    assert result.confidence >= 0.7
    assert len(result.recommendations) > 0

# Performance test example
def test_api_latency():
    with timer() as t:
        response = client.post("/api/v1/analyze", json=payload)
    assert t.elapsed < 0.050  # <50ms SLA
```

---

## Common Patterns & Conventions

### Naming Conventions
```python
# Functions/methods: snake_case
def analyze_intelligence(): pass

# Classes: PascalCase
class IntelligenceAnalyzer: pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private methods: leading underscore
def _prepare_context(): pass

# Type hints: always include
def analyze(query: str) -> AnalysisResult: pass
```

### File Organization
```
src/services/intelligence/
├── __init__.py
├── analyzer.py             # Main analysis logic
├── models.py               # Pydantic models
├── schemas.py              # Request/response schemas
├── exceptions.py           # Custom exceptions
└── tests/                  # Module-specific tests
    └── test_analyzer.py
```

### Error Handling
```python
# Define custom exceptions
class AnalysisError(Exception): pass

# Raise with context
if not sources:
    raise AnalysisError("No sources provided for analysis")

# Handle gracefully
try:
    result = await analyze(query)
except AnalysisError as e:
    logger.error("Analysis failed", error=str(e))
    return {"error": str(e), "status": "failed"}
```

---

## Performance Optimization Techniques

### Caching Strategy
```python
# Use Redis for frequent queries
@cache(ttl=3600)
async def get_source_data(source_id: str):
    return await db.sources.get(source_id)

# Cache model predictions
@cache(ttl=7200)
async def classify_threat(data: dict):
    return model.predict(data)
```

### Async/Await Pattern
```python
# Parallel execution
results = await asyncio.gather(
    fetch_source_a(),
    fetch_source_b(),
    fetch_source_c()
)

# Streaming responses
async def stream_analysis():
    for chunk in await model.generate_streaming(query):
        yield chunk
```

### Batch Processing
```python
# Process in batches for efficiency
def analyze_batch(sources: List[Source]):
    batches = chunk_list(sources, size=32)
    results = []
    for batch in batches:
        batch_results = model.batch_predict(batch)
        results.extend(batch_results)
    return results
```

---

## Debugging Techniques

### Local Development
```bash
# Run with debug logging
DEBUG=1 python -m src.api.main

# Attach debugger
python -m pdb -c continue src/api/main.py

# Profile performance
python -m cProfile -s cumulative src/api/main.py

# Memory profiling
python -m memory_profiler analyze_intelligence.py
```

### Test Debugging
```bash
# Run with print statements
pytest tests/unit/ -s -v

# Drop into debugger on failure
pytest tests/unit/ --pdb

# Show local variables
pytest tests/unit/ -l

# Detailed traceback
pytest tests/unit/ --tb=long
```

### Logging
```python
import structlog
logger = structlog.get_logger()

# Structured logging
logger.info("analysis_started", query=query, source_count=len(sources))
logger.error("analysis_failed", error=str(e), query=query)
logger.debug("cache_hit", key=cache_key)
```

---

## Deployment Checkpoints

### Pre-Deployment
- [ ] All tests passing (600+)
- [ ] Coverage >95%
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Database migrations ready
- [ ] Environment variables configured

### Post-Deployment
- [ ] Health checks passing
- [ ] Logs flowing correctly
- [ ] Metrics visible in dashboards
- [ ] Alerts configured
- [ ] Rollback plan ready
- [ ] Team notified
- [ ] Performance monitoring

---

## Knowledge Base

### Key Decisions
1. **FastAPI over Django**: Performance (<50ms), async support, auto-docs
2. **PostgreSQL over NoSQL**: Relational data, ACID compliance, queries
3. **Redis caching**: Fast key-value, <10ms access, good for LLM cache
4. **Quantized inference**: 4-bit reduces memory to <4GB, minimal accuracy loss
5. **Kubernetes**: Production scaling, zero-downtime deployments

### Known Challenges
1. **LLM Context Limits**: Muse has 131K tokens, need careful chunking
2. **Model Latency**: 100-500ms per inference, batch when possible
3. **Memory Constraints**: Quantization essential for edge deployment
4. **Cold Starts**: Docker builds take 5-10 min, use layer caching
5. **Token Costs**: LLM API calls expensive, implement caching aggressively

### Solutions Applied
1. ✅ Context windowing for large documents
2. ✅ Batch inference for throughput
3. ✅ 4-bit quantization for memory efficiency
4. ✅ Docker layer caching optimized
5. ✅ Redis cache for LLM responses

---

## Code Review Standards

### Before Submitting PR
- Run: `make quality` (lint, type-check, test)
- Check: Test coverage >95%
- Verify: No breaking changes
- Update: Documentation and CHANGELOG
- Add: Tests for new code paths

### Review Checklist
- [ ] Code style consistent
- [ ] Performance acceptable
- [ ] Security sound
- [ ] Tests comprehensive
- [ ] Documentation clear
- [ ] No duplication
- [ ] Error handling proper
- [ ] Logging appropriate

### Common Issues to Avoid
- ❌ Missing type hints
- ❌ No error handling
- ❌ Untested code paths
- ❌ Hardcoded values
- ❌ Missing docstrings
- ❌ Overly complex functions
- ❌ Performance regressions
- ❌ Security vulnerabilities

---

## Team Communication

### When Stuck
1. Check existing documentation in `docs/`
2. Review similar code patterns in codebase
3. Look at test examples in `tests/`
4. Check GitHub issues for similar problems
5. Ask in project discussions

### Reporting Issues
```markdown
**Title**: [module] Clear problem description

**Description**: What's happening, what should happen

**Steps to Reproduce**:
1. Run this command
2. Observe this error
3. Expected this behavior

**Context**: Python version, OS, error logs

**Suggested Fix**: Any ideas?
```

---

## Useful Links & Resources

### Internal
- GitHub: https://github.com/Unpapamericano/autonomous-scientific-agent
- Documentation: `docs/` directory
- Architecture: `ARCHITECTURE.md`
- Deployment: `docs/DEPLOYMENT.md`

### External
- FastAPI Docs: https://fastapi.tiangolo.com/
- PyTorch: https://pytorch.org/
- Pydantic: https://docs.pydantic.dev/
- Kubernetes: https://kubernetes.io/docs/

---

## Next Steps for New Contributors

1. **Read**: This file + AGENTS.md + SKILL.md
2. **Setup**: Follow dev environment setup
3. **Explore**: Look at 2-3 test examples
4. **Build**: Create a simple feature with test
5. **Review**: Get code reviewed by team
6. **Deploy**: Follow deployment checklist

---

**Last Updated**: September 2026  
**Version**: 1.0  
**Status**: Production  
**Maintainer**: Doncho (@Unpapamericano)
