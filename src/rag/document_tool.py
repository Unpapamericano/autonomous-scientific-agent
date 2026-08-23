"""
Phase 7: Multimodal Document Extraction Agent Tool

Exposes PDF extraction as an agent tool:
  - extract_and_index_pdf: Takes a PDF file path, extracts content,
    and indexes it into the database for RAG.

Integrates with Phase 4 (RAG) and Phase 5 (evidence graph).
"""

import logging
from typing import Any, Dict

from src.core.tools import (
    ToolDefinition,
    ToolType,
    ToolStatus,
)
from src.rag.database import get_session
from src.rag.document_extraction import get_pdf_extractor
from src.rag.multimodal_indexing import MultimodalIndexer
from src.rag.embeddings import get_embedding_generator

logger = logging.getLogger(__name__)


# Tool schemas (define new ones if needed, or reuse existing)
class ExtractAndIndexPDF:
    """Input schema for PDF extraction tool."""

    def __init__(self, pdf_path: str, paper_id: str):
        self.pdf_path = pdf_path
        self.paper_id = paper_id


class PDFExtractionResult:
    """Output schema for PDF extraction."""

    def __init__(
        self,
        success: bool,
        paper_id: str,
        elements_extracted: int,
        chunks_created: int,
        error: str = None,
    ):
        self.success = success
        self.paper_id = paper_id
        self.elements_extracted = elements_extracted
        self.chunks_created = chunks_created
        self.error = error


async def extract_and_index_pdf(
    pdf_path: str,
    paper_id: str,
) -> Dict[str, Any]:
    """
    Extract content from a PDF and index it into the database.

    Args:
        pdf_path: Path to PDF file
        paper_id: ID of the paper (must exist in database)

    Returns:
        PDFExtractionResult dict
    """
    logger.info(f"Extracting and indexing PDF: {pdf_path} for paper {paper_id}")

    session = get_session()
    try:
        extractor = get_pdf_extractor()
        embedder = get_embedding_generator()
        indexer = MultimodalIndexer(session, embedder)

        # Extract
        elements = extractor.extract_from_file(pdf_path, extract_tables=True, extract_images=True)

        if not elements:
            logger.warning(f"No content extracted from {pdf_path}")
            return {
                "success": False,
                "paper_id": paper_id,
                "elements_extracted": 0,
                "chunks_created": 0,
                "error": "No content extracted from PDF",
            }

        # Index
        chunks_created = indexer.index_extracted_elements(paper_id, elements)
        session.commit()

        logger.info(f"Extracted {len(elements)} elements and created {chunks_created} chunks")

        return {
            "success": True,
            "paper_id": paper_id,
            "elements_extracted": len(elements),
            "chunks_created": chunks_created,
            "error": None,
        }

    except FileNotFoundError:
        error_msg = f"PDF file not found: {pdf_path}"
        logger.error(error_msg)
        return {
            "success": False,
            "paper_id": paper_id,
            "elements_extracted": 0,
            "chunks_created": 0,
            "error": error_msg,
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"PDF extraction error: {error_msg}")
        return {
            "success": False,
            "paper_id": paper_id,
            "elements_extracted": 0,
            "chunks_created": 0,
            "error": error_msg,
        }

    finally:
        session.close()


# Tool definition (using ToolDefinition from core/tools.py pattern)
EXTRACT_PDF_TOOL_DEFINITION = {
    "name": "extract_and_index_pdf",
    "type": ToolType.EXTRACT.value,
    "description": (
        "Extract text, tables, and figures from a PDF file and index them into the "
        "database for semantic search and evidence linking. Use after retrieving or "
        "downloading a paper's full PDF."
    ),
    "input_schema": "ExtractAndIndexPDF",
    "output_schema": "PDFExtractionResult",
    "execution_fn": "extract_and_index_pdf",
    "status": ToolStatus.EXPERIMENTAL.value,
    "tags": ["multimodal", "pdf", "extraction", "indexing"],
}


def register_multimodal_tools(registry) -> None:
    """
    Register Phase 7 multimodal document extraction tools.

    Note: This is a placeholder pattern. Real tool registration requires
    ToolDefinition objects. For now, tools are documented here for Phase 7.
    """
    logger.info("Multimodal document extraction tools ready (Phase 7)")
    # TODO: Create proper ToolDefinition and register in registry
