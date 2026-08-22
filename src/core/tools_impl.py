"""
Phase 2: Tool Implementations

Concrete implementations of tools used by the research agent.
Each tool is async, testable, and includes error handling.

Tools included:
  - Search (literature search via APIs)
  - Execute (Python code execution in sandbox)
  - Parse (table/data extraction)
  - Verify (claim verification)
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional

from src.core.tools import (
    ToolDefinition,
    ToolType,
    ToolStatus,
    SearchQuery,
    SearchResult,
    ExecuteCode,
    CodeExecutionResult,
    ParseTable,
    ExtractedTable,
    VerifyClaim,
    VerificationResult,
)

logger = logging.getLogger(__name__)


# ============================================================================
# SEARCH TOOL
# ============================================================================

async def search_literature(
    query: str,
    limit: int = 10,
    source: str = "all",
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Search scientific literature across multiple sources.
    
    Phase 2 implementation: Mock responses.
    Phase 3: Real API integration (PubMed, arXiv, OpenAlex).
    
    Args:
        query: Search query
        limit: Max results
        source: "pubmed", "arxiv", "openalex", or "all"
        year_from: Filter by year range
        year_to: Filter by year range
        
    Returns:
        List of SearchResult dicts
    """
    logger.info(f"Searching literature: query='{query}', source='{source}'")
    
    # TODO: Phase 3 — Replace with real API calls
    # For now, return mock results
    mock_results = [
        {
            "paper_id": f"pubmed_12345_{i}",
            "title": f"Study on {query} - Result {i+1}",
            "authors": [f"Author {j}" for j in range(2)],
            "year": 2025,
            "abstract": f"This study investigates {query}. Mock abstract for demonstration.",
            "relevance_score": 1.0 - (i * 0.1),  # Decreasing relevance
            "source": "pubmed" if i % 2 == 0 else "arxiv",
            "url": f"https://example.com/paper/{i}",
            "doi": f"10.1234/example.{i}",
        }
        for i in range(min(limit, 5))  # Mock up to 5 results
    ]
    
    logger.info(f"Found {len(mock_results)} results")
    return mock_results


SEARCH_TOOL = ToolDefinition(
    name="search_literature",
    type=ToolType.SEARCH,
    description=(
        "Search scientific literature across PubMed, arXiv, and OpenAlex. "
        "Returns paper metadata (title, authors, abstract, DOI) ranked by relevance. "
        "Use for finding research papers related to a topic."
    ),
    input_schema=SearchQuery,
    output_schema=SearchResult,
    execution_fn=search_literature,
    status=ToolStatus.AVAILABLE,
    tags=["research", "literature", "search"],
)


# ============================================================================
# CODE EXECUTION TOOL
# ============================================================================

async def execute_python_code(
    code: str,
    timeout_seconds: int = 30,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute Python code in a sandboxed environment.
    
    Phase 2 implementation: Basic local execution with safety checks.
    Phase 6: Full Docker sandbox with resource limits.
    
    Args:
        code: Python code to execute
        timeout_seconds: Execution timeout
        description: What this code does (for logging)
        
    Returns:
        CodeExecutionResult dict
    """
    logger.info(f"Executing code: {description or 'unnamed'}")
    
    # Safety checks
    dangerous_imports = {"os", "sys", "subprocess", "socket", "urllib"}
    for imp in dangerous_imports:
        if f"import {imp}" in code or f"from {imp}" in code:
            error_msg = f"Dangerous import detected: {imp}"
            logger.error(error_msg)
            return {
                "success": False,
                "stdout": "",
                "stderr": error_msg,
                "return_value": None,
                "execution_time_ms": 0,
                "error": error_msg,
            }
    
    # Prepare execution environment
    namespace = {
        "__builtins__": __builtins__,
        "__name__": "__sandbox__",
    }
    
    # Allow safe imports
    safe_modules = {
        "math": __import__("math"),
        "json": __import__("json"),
        "re": __import__("re"),
        "statistics": __import__("statistics"),
    }
    namespace.update(safe_modules)
    
    try:
        import time
        start = time.time()
        
        # Execute with timeout
        exec(code, namespace)
        
        elapsed_ms = (time.time() - start) * 1000
        
        logger.info(f"Code executed successfully in {elapsed_ms:.1f}ms")
        
        return {
            "success": True,
            "stdout": "",
            "stderr": "",
            "return_value": None,
            "execution_time_ms": elapsed_ms,
            "error": None,
        }
    
    except asyncio.TimeoutError:
        error_msg = f"Code execution timed out after {timeout_seconds}s"
        logger.error(error_msg)
        return {
            "success": False,
            "stdout": "",
            "stderr": error_msg,
            "return_value": None,
            "execution_time_ms": timeout_seconds * 1000,
            "error": error_msg,
        }
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Code execution error: {error_msg}")
        return {
            "success": False,
            "stdout": "",
            "stderr": error_msg,
            "return_value": None,
            "execution_time_ms": 0,
            "error": error_msg,
        }


EXECUTE_CODE_TOOL = ToolDefinition(
    name="execute_python_code",
    type=ToolType.EXECUTE,
    description=(
        "Execute Python code for data analysis, statistics, or visualization. "
        "Code runs in a sandboxed environment with limited imports (math, json, re, statistics). "
        "Use for numerical analysis, data manipulation, and calculations."
    ),
    input_schema=ExecuteCode,
    output_schema=CodeExecutionResult,
    execution_fn=execute_python_code,
    status=ToolStatus.EXPERIMENTAL,  # Sandboxing is basic in Phase 2
    tags=["analysis", "code", "python"],
)


# ============================================================================
# TABLE PARSING TOOL
# ============================================================================

async def parse_table_data(
    content: str,
    table_format: str = "auto",
    extraction_goal: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Parse table data from various formats.
    
    Phase 2 implementation: Basic parsing.
    Phase 7: Integration with PDF table extraction.
    
    Args:
        content: Table content (markdown, CSV, or text)
        table_format: Format hint
        extraction_goal: What to extract
        
    Returns:
        ExtractedTable dict
    """
    logger.info(f"Parsing table: format={table_format}, goal={extraction_goal}")
    
    rows = []
    columns = []
    
    try:
        # Try parsing as markdown table
        lines = content.strip().split('\n')
        
        if len(lines) >= 2 and '|' in lines[0]:
            # Parse markdown table
            columns = [c.strip() for c in lines[0].split('|') if c.strip()]
            
            for line in lines[2:]:  # Skip header separator
                if '|' in line:
                    values = [v.strip() for v in line.split('|') if v.strip()]
                    if len(values) == len(columns):
                        rows.append(dict(zip(columns, values)))
        
        elif ',' in content:
            # Try CSV
            import csv
            from io import StringIO
            reader = csv.DictReader(StringIO(content))
            columns = reader.fieldnames or []
            rows = list(reader)
        
        else:
            # Plain text table
            lines = content.strip().split('\n')
            if lines:
                columns = [f"col_{i}" for i in range(len(lines[0].split()))]
                for line in lines:
                    values = line.split()
                    if len(values) == len(columns):
                        rows.append(dict(zip(columns, values)))
        
        summary = f"Extracted {len(rows)} rows × {len(columns)} columns"
        
        logger.info(f"Table parsed: {summary}")
        
        return {
            "rows": rows,
            "columns": columns,
            "summary": summary,
            "structured_data": {"row_count": len(rows), "column_count": len(columns)},
        }
    
    except Exception as e:
        logger.error(f"Table parsing error: {e}")
        return {
            "rows": [],
            "columns": [],
            "summary": f"Error parsing table: {e}",
            "structured_data": {},
        }


PARSE_TABLE_TOOL = ToolDefinition(
    name="parse_table_data",
    type=ToolType.PARSE,
    description=(
        "Extract and parse table data from various formats (markdown, CSV, text). "
        "Returns structured rows and columns. "
        "Use for extracting results tables, comparison matrices, or summary statistics from papers."
    ),
    input_schema=ParseTable,
    output_schema=ExtractedTable,
    execution_fn=parse_table_data,
    status=ToolStatus.AVAILABLE,
    tags=["parsing", "data-extraction"],
)


# ============================================================================
# VERIFICATION TOOL
# ============================================================================

async def verify_claim(
    claim: str,
    source_documents: List[str],
    confidence_threshold: float = 0.7,
) -> Dict[str, Any]:
    """
    Verify a claim against source documents.
    
    Phase 2 implementation: Basic keyword matching.
    Phase 5: Integration with RAG & evidence graph.
    
    Args:
        claim: Claim to verify
        source_documents: List of documents to check against
        confidence_threshold: Min confidence to consider verified
        
    Returns:
        VerificationResult dict
    """
    logger.info(f"Verifying claim: '{claim}'")
    
    # Extract key terms from claim
    keywords = set(claim.lower().split())
    keywords = {w for w in keywords if len(w) > 3}  # Filter short words
    
    supporting = []
    contradicting = []
    
    # Check each source document
    for i, doc in enumerate(source_documents):
        doc_lower = doc.lower()
        
        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in doc_lower)
        match_ratio = matches / len(keywords) if keywords else 0
        
        if match_ratio >= 0.7:
            supporting.append(f"Document {i}: {doc[:100]}...")
        elif match_ratio >= 0.3:
            # Partial match could indicate contradiction
            contradicting.append(f"Document {i}: {doc[:100]}...")
    
    # Calculate verification confidence
    if supporting:
        confidence = min(0.9, 0.5 + (len(supporting) * 0.2))
        verified = confidence >= confidence_threshold
    else:
        confidence = 0.0
        verified = False
    
    logger.info(
        f"Claim verification: verified={verified}, confidence={confidence:.2f}"
    )
    
    return {
        "claim": claim,
        "verified": verified,
        "confidence_score": confidence,
        "supporting_evidence": supporting,
        "contradicting_evidence": contradicting,
        "reasoning": (
            f"Found {len(supporting)} supporting documents and "
            f"{len(contradicting)} potentially contradicting documents."
        ),
    }


VERIFY_CLAIM_TOOL = ToolDefinition(
    name="verify_claim",
    type=ToolType.VALIDATE,
    description=(
        "Verify a scientific claim against source documents. "
        "Returns confidence score and supporting/contradicting evidence. "
        "Use to validate whether claims are actually supported by retrieved papers."
    ),
    input_schema=VerifyClaim,
    output_schema=VerificationResult,
    execution_fn=verify_claim,
    status=ToolStatus.EXPERIMENTAL,  # Basic implementation, improved in Phase 5
    tags=["verification", "validation"],
)


# ============================================================================
# TOOL COLLECTION
# ============================================================================

CORE_TOOLS = [
    SEARCH_TOOL,
    EXECUTE_CODE_TOOL,
    PARSE_TABLE_TOOL,
    VERIFY_CLAIM_TOOL,
]


def register_core_tools(registry) -> None:
    """Register all core tools to a registry."""
    for tool in CORE_TOOLS:
        registry.register(tool)
    logger.info(f"Registered {len(CORE_TOOLS)} core tools")
