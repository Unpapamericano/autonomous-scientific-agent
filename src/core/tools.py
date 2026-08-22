"""
Phase 2: Tool Definitions & Registry

Structured tool definitions for Muse Glimmer tool calling.
Each tool is defined as a Pydantic model with:
  - Name & description
  - Input schema (parameters)
  - Output type
  - Execution function

Tools can be called by the agent and orchestrated by LangChain/LLaMA-Index.
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class ToolType(str, Enum):
    """Categories of tools available to the agent."""
    SEARCH = "search"           # Search scientific literature
    RETRIEVE = "retrieve"       # Fetch full documents
    EXECUTE = "execute"         # Run Python code
    PARSE = "parse"             # Parse tables, figures, text
    ANALYZE = "analyze"         # Statistical analysis
    EXTRACT = "extract"         # Extract structured data
    VALIDATE = "validate"       # Verify claims against sources


class ToolStatus(str, Enum):
    """Tool availability status."""
    AVAILABLE = "available"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    DISABLED = "disabled"


# ============================================================================
# TOOL INPUT/OUTPUT SCHEMAS
# ============================================================================

class SearchQuery(BaseModel):
    """Input schema for literature search tool."""
    query: str = Field(
        ...,
        description="Search query (e.g., 'CRISPR gene editing blindness')",
        min_length=3,
        max_length=500,
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results",
        ge=1,
        le=100,
    )
    source: str = Field(
        default="all",
        description="Search source: 'pubmed', 'arxiv', 'openalex', or 'all'",
    )
    year_from: Optional[int] = Field(
        default=None,
        description="Filter results from year (inclusive)",
        ge=1900,
        le=2026,
    )
    year_to: Optional[int] = Field(
        default=None,
        description="Filter results to year (inclusive)",
        ge=1900,
        le=2026,
    )

    @validator("source")
    def validate_source(cls, v):
        valid = {"pubmed", "arxiv", "openalex", "all"}
        if v not in valid:
            raise ValueError(f"source must be one of {valid}")
        return v

    @validator("year_to")
    def validate_year_range(cls, v, values):
        if v is not None and "year_from" in values:
            year_from = values["year_from"]
            if year_from is not None and v < year_from:
                raise ValueError("year_to must be >= year_from")
        return v


class SearchResult(BaseModel):
    """Output schema for search results."""
    paper_id: str
    title: str
    authors: List[str]
    year: int
    abstract: str
    relevance_score: float  # 0-1
    source: str  # "pubmed", "arxiv", etc.
    url: Optional[str] = None
    doi: Optional[str] = None


class ExecuteCode(BaseModel):
    """Input schema for code execution tool."""
    code: str = Field(
        ...,
        description="Python code to execute (no imports of dangerous modules)",
        min_length=1,
        max_length=10000,
    )
    timeout_seconds: int = Field(
        default=30,
        description="Execution timeout",
        ge=1,
        le=300,
    )
    description: Optional[str] = Field(
        default=None,
        description="What this code does (for audit log)",
    )


class CodeExecutionResult(BaseModel):
    """Output schema for code execution."""
    success: bool
    stdout: str
    stderr: str
    return_value: Optional[Any] = None
    execution_time_ms: float
    error: Optional[str] = None


class ParseTable(BaseModel):
    """Input schema for table parsing tool."""
    content: str = Field(
        ...,
        description="Table content (markdown, CSV, or raw text)",
    )
    table_format: str = Field(
        default="auto",
        description="Format: 'markdown', 'csv', 'html', or 'auto' (detect)",
    )
    extraction_goal: Optional[str] = Field(
        default=None,
        description="What specific data to extract (e.g., 'treatment vs. control success rates')",
    )


class ExtractedTable(BaseModel):
    """Output schema for parsed tables."""
    rows: List[Dict[str, str]]
    columns: List[str]
    summary: str
    structured_data: Dict[str, Any]  # Interpreted data


class VerifyClaim(BaseModel):
    """Input schema for claim verification."""
    claim: str = Field(
        ...,
        description="The claim to verify",
    )
    source_documents: List[str] = Field(
        ...,
        description="List of document IDs or texts to verify against",
        min_items=1,
        max_items=20,
    )
    confidence_threshold: float = Field(
        default=0.7,
        description="Minimum confidence score to consider verified",
        ge=0.0,
        le=1.0,
    )


class VerificationResult(BaseModel):
    """Output schema for verification."""
    claim: str
    verified: bool
    confidence_score: float
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    reasoning: str


class RetrieveContext(BaseModel):
    """Input schema for RAG context retrieval tool (Phase 4)."""
    question: str = Field(
        ...,
        description="Natural language question to retrieve grounded context for",
        min_length=3,
        max_length=500,
    )
    top_k: int = Field(
        default=5,
        description="Number of relevant chunks to retrieve",
        ge=1,
        le=20,
    )
    paper_id: Optional[str] = Field(
        default=None,
        description="Optionally restrict retrieval to a single paper ID",
    )


class RetrievedChunk(BaseModel):
    """A single retrieved chunk with provenance."""
    chunk_id: str
    paper_id: str
    content: str
    section: Optional[str] = None
    score: float


class RetrieveContextResult(BaseModel):
    """Output schema for RAG context retrieval (Phase 4)."""
    question: str
    chunks: List[RetrievedChunk]
    context_text: str  # formatted, citation-ready context block


# ============================================================================
# TOOL DEFINITION BASE CLASS
# ============================================================================

@dataclass
class ToolDefinition:
    """
    Standard tool definition for structured calling.
    
    Attributes:
        name: Unique tool identifier (e.g., 'search_literature')
        type: Tool category (ToolType enum)
        description: Human-readable description for LLM
        input_schema: Pydantic model for input validation
        output_schema: Pydantic model for output
        execution_fn: Actual function to call
        status: Tool availability status
        requires_approval: Whether tool needs human approval
        rate_limit_per_minute: Rate limiting (calls/min)
        tags: Search tags for tool discovery
    """
    name: str
    type: ToolType
    description: str
    input_schema: type  # Pydantic BaseModel class
    output_schema: type  # Pydantic BaseModel class
    execution_fn: Callable
    status: ToolStatus = ToolStatus.AVAILABLE
    requires_approval: bool = False
    rate_limit_per_minute: int = 60
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert tool definition to JSON schema for LLM calling."""
        input_schema = self.input_schema.schema()
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "const": self.name},
                "description": {"type": "string", "const": self.description},
                "parameters": input_schema,
            },
            "required": ["name", "parameters"],
        }

    def to_openai_format(self) -> Dict[str, Any]:
        """Format for OpenAI function calling (compatible with LLMs)."""
        input_schema = self.input_schema.schema()
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": input_schema.get("properties", {}),
                "required": input_schema.get("required", []),
            },
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with input validation and error handling.
        
        Args:
            **kwargs: Tool-specific parameters matching input_schema
            
        Returns:
            Validated output matching output_schema
        """
        try:
            # Validate input
            input_obj = self.input_schema(**kwargs)
            logger.info(f"Tool '{self.name}' called with: {input_obj}")

            # Execute
            result = await self.execution_fn(**input_obj.dict())

            # Validate output
            if isinstance(result, self.output_schema):
                output_obj = result
            else:
                output_obj = self.output_schema(**result)

            logger.info(f"Tool '{self.name}' completed successfully")
            return output_obj.dict()

        except ValueError as e:
            logger.error(f"Tool '{self.name}' validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Tool '{self.name}' execution error: {e}")
            raise


# ============================================================================
# TOOL REGISTRY
# ============================================================================

class ToolRegistry:
    """
    Central registry for all available tools.
    
    Provides:
      - Tool discovery by name, type, or tag
      - Availability checking
      - Schema export for LLM prompting
      - Execution orchestration
      - Rate limiting
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._call_counts: Dict[str, int] = {}
        logger.info("ToolRegistry initialized")

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool."""
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered; overwriting")
        
        self._tools[tool.name] = tool
        self._call_counts[tool.name] = 0
        logger.info(f"Registered tool: {tool.name} (type: {tool.type})")

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Retrieve a tool by name."""
        return self._tools.get(name)

    def list_by_type(self, tool_type: ToolType) -> List[ToolDefinition]:
        """List all tools of a specific type."""
        return [t for t in self._tools.values() if t.type == tool_type]

    def list_by_tag(self, tag: str) -> List[ToolDefinition]:
        """List all tools with a specific tag."""
        return [t for t in self._tools.values() if tag in t.tags]

    def list_available(self) -> List[ToolDefinition]:
        """List only available tools."""
        return [t for t in self._tools.values() if t.status == ToolStatus.AVAILABLE]

    def export_json_schema(self, available_only: bool = True) -> List[Dict[str, Any]]:
        """
        Export all tools as JSON schema for LLM prompting.
        
        Args:
            available_only: If True, exclude disabled/deprecated tools
            
        Returns:
            List of tool definitions in JSON schema format
        """
        tools = self.list_available() if available_only else list(self._tools.values())
        return [t.to_json_schema() for t in tools]

    def export_openai_format(self, available_only: bool = True) -> List[Dict[str, Any]]:
        """Export in OpenAI function calling format."""
        tools = self.list_available() if available_only else list(self._tools.values())
        return [t.to_openai_format() for t in tools]

    async def execute(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        check_rate_limit: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute a tool with rate limiting and error handling.
        
        Args:
            tool_name: Name of tool to execute
            tool_input: Input parameters
            check_rate_limit: If True, enforce rate limits
            
        Returns:
            Tool output
            
        Raises:
            KeyError: Tool not found
            ValueError: Rate limit exceeded or validation error
        """
        tool = self.get(tool_name)
        if not tool:
            raise KeyError(f"Tool '{tool_name}' not found")

        if tool.status != ToolStatus.AVAILABLE:
            raise ValueError(f"Tool '{tool_name}' is not available (status: {tool.status})")

        # Check rate limit
        if check_rate_limit:
            call_count = self._call_counts.get(tool_name, 0)
            if call_count >= tool.rate_limit_per_minute:
                raise ValueError(
                    f"Tool '{tool_name}' rate limit exceeded "
                    f"({tool.rate_limit_per_minute} calls/min)"
                )

        # Execute
        result = await tool.execute(**tool_input)

        # Update call count
        self._call_counts[tool_name] = self._call_counts.get(tool_name, 0) + 1

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_tools": len(self._tools),
            "available_tools": len(self.list_available()),
            "call_counts": self._call_counts.copy(),
            "tools_by_type": {
                tool_type.value: len(self.list_by_type(tool_type))
                for tool_type in ToolType
            },
        }


# ============================================================================
# SINGLETON REGISTRY INSTANCE
# ============================================================================

_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create global tool registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
