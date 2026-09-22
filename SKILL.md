# SKILL.md - AI-Powered Development Assistant Skills

## Overview
This document describes how AI assistants (like GitHub Copilot, Claude, or other AI tools) can effectively contribute to the Defense Intelligence Platform project.

---

## Core Capabilities

### 1. Code Generation
The assistant can help generate:
- ✅ FastAPI endpoint implementations
- ✅ Service layer business logic
- ✅ Domain model implementations
- ✅ Test cases (unit, integration, performance)
- ✅ Database migration scripts
- ✅ Docker configurations
- ✅ Kubernetes manifests
- ✅ GitHub Actions workflows

### 2. Code Analysis & Review
The assistant can:
- ✅ Identify performance bottlenecks
- ✅ Spot security vulnerabilities
- ✅ Find dead code and unused imports
- ✅ Suggest design pattern improvements
- ✅ Review PR changes for quality
- ✅ Recommend test coverage improvements

### 3. Documentation
The assistant can help create:
- ✅ API documentation
- ✅ Architecture diagrams (in Mermaid)
- ✅ Setup guides
- ✅ Troubleshooting guides
- ✅ Changelog entries
- ✅ Code comments and docstrings

### 4. Debugging & Troubleshooting
The assistant can help with:
- ✅ Analyzing error messages
- ✅ Identifying root causes
- ✅ Suggesting fixes
- ✅ Creating minimal reproductions
- ✅ Analyzing performance issues
- ✅ Memory leak detection

### 5. Refactoring
The assistant can help:
- ✅ Extract functions
- ✅ Reduce code duplication
- ✅ Improve naming
- ✅ Apply design patterns
- ✅ Modernize Python code
- ✅ Optimize hot paths

---

## Working with AI Assistants

### Best Practices for Prompts

#### 1. Provide Context
```
❌ BAD: "Write a function that analyzes intelligence"

✅ GOOD: """
I'm building an intelligence analysis function for a FastAPI service.

Requirements:
- Input: Query string, list of sources (with reliability scores)
- Output: AnalysisResult with synthesis, confidence, recommendations
- Must use Muse Glimmer 30B LLM for analysis
- Response time SLA: <50ms
- Should detect conflicts between sources
- Include comprehensive docstring and type hints

The function should follow this pattern:
```python
async def analyze_intelligence(
    query: str,
    sources: List[IntelligenceSource],
    confidence_threshold: float = 0.7
) -> AnalysisResult:
    '''Analyze multi-source intelligence with conflict detection'''
    pass
```
"""
```

#### 2. Show Examples
```
WHEN ASKING FOR CODE:
"Here's a similar function in our codebase. Use this as a template:
```python
async def detect_threats(data: dict) -> List[Threat]:
    '''Detect threats in intelligence data'''
    validated = await validate_data(data)
    threats = await model.predict(validated)
    return sorted(threats, key=lambda t: t.severity, reverse=True)
```
Now implement `analyze_contradictions()` with the same pattern"
```

#### 3. Specify Constraints
```
"Generate code that:
- Uses async/await throughout
- Includes comprehensive type hints
- Has detailed docstrings (Google style)
- Includes error handling
- Includes logging
- Has 100% test coverage
- Follows PEP-8 conventions
- Uses only packages in requirements.txt"
```

#### 4. Ask for Alternatives
```
"Give me 3 different approaches to solve this:
1. With pros/cons
2. For each approach

Then recommend which fits our architecture best."
```

---

## Task-Specific Guidance

### Writing Tests

**Request Template**:
```
"I need comprehensive tests for this function:
```python
async def resolve_conflicts(conflicts: List[Conflict]) -> ResolutionResult:
    # implementation
```

Requirements:
- Unit tests with mocks
- Integration tests with real data
- Edge cases (empty list, high confidence, low confidence)
- Performance tests (<50ms)
- Test both success and failure paths

Use pytest, async support, and our test fixtures from tests/fixtures/"
```

### Creating API Endpoints

**Request Template**:
```
"Create a FastAPI endpoint with:
- Path: POST /api/v1/intelligence/analyze
- Input: IntelligenceQuery (query, sources, confidence_threshold)
- Output: AnalysisResponse
- Features: OAuth2 auth, rate limiting, request validation, error handling
- Docs: Swagger-compatible docstring
- Follows our endpoint pattern in src/api/endpoints/

Include the full implementation + tests."
```

### Database Queries

**Request Template**:
```
"Write SQLAlchemy queries for:
1. Get all sources with reliability > 0.8
2. Count analyses by source (last 30 days)
3. Find conflicts between specific sources

Use our models in src/infrastructure/models.py
Include async support (AsyncSession)"
```

### Docker & Deployment

**Request Template**:
```
"Create a production Dockerfile with:
- Multi-stage build
- Non-root user
- Health check
- Security best practices
- Optimize for size and layer caching

Target: Python 3.11 base image
Include: All dependencies from requirements.txt"
```

---

## Code Generation Examples

### Example 1: FastAPI Endpoint with AI Help
```
PROMPT:
"Create a FastAPI endpoint for threat detection that:
- Accepts POST requests with intelligence data
- Uses our ThreatDetector service
- Returns confidence scores
- Includes proper error handling and logging"

AI RESPONSE:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog

router = APIRouter(prefix="/api/v1/security", tags=["Security"])
logger = structlog.get_logger()

class ThreatRequest(BaseModel):
    data: dict
    confidence_threshold: float = 0.7

class ThreatResponse(BaseModel):
    threats: List[dict]
    confidence: float
    timestamp: str

detector = ThreatDetector()

@router.post("/detect-threats", response_model=ThreatResponse)
async def detect_threats(request: ThreatRequest):
    '''Detect threats in intelligence data'''
    try:
        logger.info("threat_detection_started", threshold=request.confidence_threshold)
        threats = await detector.detect(request.data)
        confidence = await detector.calculate_confidence(threats)
        
        return ThreatResponse(
            threats=threats,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error("threat_detection_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Detection failed")
```
"""
```

### Example 2: Test Writing with AI Help
```
PROMPT:
"Write pytest tests for conflict detection. The function signature is:
def detect_contradictions(studies: List[Study]) -> List[Conflict]

Test scenarios needed:
- No conflicts (both agree)
- Direct contradiction
- Quantitative disagreement
- Edge case: empty list
- Edge case: single study

Use pytest fixtures."

AI RESPONSE:
```python
import pytest
from hypothesis import given, strategies as st

@pytest.fixture
def study_factory():
    def create(name, finding, confidence=0.9):
        return Study(name=name, finding=finding, confidence=confidence)
    return create

def test_no_conflicts(study_factory):
    """Test when studies agree"""
    study1 = study_factory("A", "X increases Y", 0.9)
    study2 = study_factory("B", "X increases Y", 0.8)
    
    conflicts = detect_contradictions([study1, study2])
    assert len(conflicts) == 0

def test_direct_contradiction(study_factory):
    """Test when studies contradict"""
    study1 = study_factory("A", "X increases Y", 0.9)
    study2 = study_factory("B", "X decreases Y", 0.85)
    
    conflicts = detect_contradictions([study1, study2])
    assert len(conflicts) == 1
    assert conflicts[0].type == ConflictType.DIRECT_CONTRADICTION

@given(st.lists(st.just(Study(name="test"))))
def test_property_empty_input(studies):
    """Property test: always returns list"""
    result = detect_contradictions(studies)
    assert isinstance(result, list)
```
"""
```

---

## Integration with Development Workflow

### 1. Feature Development
```
AI ASSISTS WITH:
1. Understanding requirements
2. Designing solution
3. Writing implementation
4. Generating tests
5. Creating documentation

HUMAN DECIDES:
- Architecture and design
- Which approach to take
- Code review and approval
- When to merge
```

### 2. Bug Fixing
```
AI ASSISTS WITH:
1. Analyzing error messages
2. Identifying root cause
3. Suggesting fixes
4. Generating test cases
5. Verification steps

HUMAN DECIDES:
- Whether fix is correct
- Whether to apply
- Related changes needed
```

### 3. Performance Optimization
```
AI ASSISTS WITH:
1. Profiling analysis
2. Bottleneck identification
3. Optimization strategies
4. Benchmark generation
5. Regression testing

HUMAN DECIDES:
- Trade-offs acceptable
- Which optimization to apply
- Performance targets
```

---

## Advanced Techniques

### Architectural Guidance
```
REQUEST:
"Review this architecture decision:
- Should we use FastAPI or Django?
- Why FastAPI is better for our <50ms SLA?
- What are trade-offs?"

AI RESPONSE:
- Compares approaches
- Considers project constraints
- Provides recommendations
- Lists pros/cons
```

### Complex Algorithm Help
```
REQUEST:
"Help me implement conflict resolution with 4 strategies:
1. Weight by quality
2. Average effects
3. Check replication
4. Flag unresolved

Each strategy should handle different conflict types.
Need to pick the best strategy automatically."

AI RESPONSE:
- Suggests design patterns (Strategy pattern)
- Generates base classes
- Implements each strategy
- Creates selector logic
```

### System Design
```
REQUEST:
"How should we architect the LLM inference layer for:
- Low latency (<50ms)
- High throughput (1000+ req/sec)
- Memory efficiency (<4GB)
- Easy model switching

Show deployment diagram and data flow."

AI RESPONSE:
- Proposes architecture
- Creates Mermaid diagrams
- Shows data flow
- Lists components
```

---

## What AI CANNOT Do

### ❌ Cannot Replace Human Judgment
- Architecture decisions
- Code review approval
- Security certification
- Performance tuning
- Team communication

### ❌ Cannot Guarantee Correctness
- Must verify generated code
- Run tests thoroughly
- Review logic carefully
- Test edge cases
- Performance benchmark

### ❌ Cannot Understand Business Context
- Customer needs
- Priority decisions
- Trade-offs
- Risk assessment
- Strategic direction

---

## Quality Standards for AI-Generated Code

### Acceptance Criteria
- [ ] Follows project conventions
- [ ] Includes type hints
- [ ] Has docstrings
- [ ] Passes linting (pylint, black)
- [ ] Type-checks pass (mypy)
- [ ] All tests pass
- [ ] >95% test coverage
- [ ] Performance SLAs met
- [ ] Security reviewed
- [ ] No duplicate code

### Before Merging AI-Generated Code
```bash
# 1. Run quality checks
make quality

# 2. Run all tests
pytest tests/ -v

# 3. Check coverage
pytest tests/ --cov=src --cov-fail-under=95

# 4. Manual review
# - Read all code line-by-line
# - Verify logic correctness
# - Check error handling
# - Review security implications

# 5. Test locally
# - Manual testing
# - Edge cases
# - Performance under load
```

---

## Examples of Good AI Prompts

### 1. Feature Request
```
"Implement the uncertainty quantification service that:
- Takes analysis results
- Applies GRADE methodology
- Returns confidence level (0-1)
- Evidence level (HIGH/MODERATE/LOW/VERY_LOW)
- Includes full docstring and type hints
- Has comprehensive tests
- Performance: <50ms"
```

### 2. Bug Fix
```
"Fix the API latency issue:
- Current: 200ms average
- Target: <50ms
- The bottleneck is in model.generate() calls
- We need to batch process when possible
- Cache results when appropriate
- Show before/after performance"
```

### 3. Optimization
```
"Optimize memory usage:
- Current: 8GB peak
- Target: <4GB
- Implement quantized inference (4-bit)
- Add caching layer
- Show memory profiling before/after"
```

### 4. Documentation
```
"Generate API documentation for our endpoints:
- List all /api/v1/* endpoints
- Include request/response examples
- Add error cases
- Include authentication info
- Format as Markdown for README"
```

---

## Troubleshooting AI-Generated Code

### Issue: Type Errors
```
PROBLEM: "error: Cannot assign value of type X to Y"

FIX REQUEST:
"Fix type errors in this code by:
- Adding proper type hints
- Fixing type mismatches
- Validating Pydantic models"
```

### Issue: Performance Problems
```
PROBLEM: "Function takes 500ms, needs to be <50ms"

FIX REQUEST:
"Optimize this function:
- Profile to find bottleneck
- Suggest caching strategy
- Consider batch processing
- Show performance improvement"
```

### Issue: Security Vulnerability
```
PROBLEM: "Security scan found injection vulnerability"

FIX REQUEST:
"Fix SQL injection vulnerability:
- Use parameterized queries
- Validate/sanitize inputs
- Add security tests
- Show before/after"
```

---

## Team Collaboration

### Using AI with Code Review
```
WORKFLOW:
1. AI generates code
2. Human reviews
3. If issues: "AI, fix these issues: [list]"
4. Human reviews again
5. Repeat until approved
6. Merge with confidence

AI ASSISTS: Generation, quick fixes
HUMAN DECIDES: Approval, quality gate
```

### Pair Programming with AI
```
WORKFLOW:
1. Human: "I need a function that..."
2. AI: Generates implementation
3. Human: Reviews and tests
4. Human: "Let's optimize the part that..."
5. AI: Suggests improvements
6. Human: Implements and verifies
```

---

## Performance Expectations

### Typical Generation Times
- Simple function: <10 seconds
- Complete service: <30 seconds
- Full feature: <2 minutes
- Tests: <1 minute
- Documentation: <1 minute

### Accuracy Rates
- Syntax correctness: 95%+
- Logic correctness: 80-90% (requires review)
- Performance optimization: 70-80% (needs tuning)
- Security: 80%+ (always review)

---

## Best Practices Summary

1. **Be Specific**: Provide context, constraints, examples
2. **Verify Output**: Always review and test generated code
3. **Iterate**: Request improvements, refine solutions
4. **Combine Skills**: AI for generation, humans for judgment
5. **Document Decisions**: Record why choices were made
6. **Test Thoroughly**: Generated code needs same rigor
7. **Review Security**: Always security-check AI code
8. **Optimize Performance**: Benchmark before/after

---

## Resources

- **FastAPI**: https://fastapi.tiangolo.com/docs/
- **PyTorch**: https://pytorch.org/docs/
- **Project Docs**: `docs/` directory
- **Code Examples**: `src/` and `tests/` directories

---

**Last Updated**: September 2026  
**Version**: 1.0  
**Status**: Production  
**Maintainer**: Doncho (@Unpapamericano)
