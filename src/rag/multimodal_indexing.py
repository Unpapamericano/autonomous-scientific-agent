"""
Phase 7: Multimodal Indexing

Links extracted PDF content (text, tables, figures) into the evidence graph:
  - Each extracted element becomes a document chunk
  - Tables are indexed separately for easier querying
  - Figures are marked with captions/descriptions
  - All elements are embedded and searchable via RAG
"""

import logging
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from src.rag.models import DocumentChunk, Paper
from src.rag.document_extraction import ExtractedElement, DocumentElementType
from src.rag.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class MultimodalIndexer:
    """
    Index extracted PDF content into the database and evidence graph.
    """

    def __init__(self, session: Session, embedder: Optional[EmbeddingGenerator] = None):
        self.session = session
        self.embedder = embedder

    def index_extracted_elements(
        self,
        paper_id: str,
        elements: List[ExtractedElement],
    ) -> int:
        """
        Index a batch of extracted elements as document chunks.

        Args:
            paper_id: ID of the paper they came from
            elements: List of ExtractedElement

        Returns:
            Number of chunks created
        """
        if not elements:
            return 0

        texts = [e.content for e in elements]
        embeddings = None

        if self.embedder:
            embeddings = self.embedder.embed_batch(texts)

        chunks_created = 0

        for idx, element in enumerate(elements):
            # Generate section name based on element type
            section = f"{element.type.value}_p{element.page_number}"

            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                paper_id=paper_id,
                chunk_index=idx,
                content=element.content,
                section=section,
                page_number=element.page_number,
                embedding=embeddings[idx] if embeddings else None,
                embedding_model=self.embedder.model_name if self.embedder else None,
            )

            # Store element type in metadata
            chunk.extra_metadata = {
                "element_type": element.type.value,
                "source_file": element.source_file,
                "bounding_box": element.bounding_box,
                "extraction_metadata": element.metadata,
            }

            self.session.add(chunk)
            chunks_created += 1

        logger.info(f"Indexed {chunks_created} multimodal elements for paper {paper_id}")
        return chunks_created

    def index_table_specially(
        self,
        paper_id: str,
        table_element: ExtractedElement,
        chunk_index: int,
    ) -> Optional[DocumentChunk]:
        """
        Create a special table chunk with additional indexing.

        Args:
            paper_id: Paper ID
            table_element: ExtractedElement of type TABLE
            chunk_index: Chunk sequence number

        Returns:
            Created DocumentChunk or None
        """
        if table_element.type != DocumentElementType.TABLE:
            logger.warning("table_element is not a TABLE type")
            return None

        embedding = None
        if self.embedder:
            embedding = self.embedder.embed_text(table_element.content)

        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            paper_id=paper_id,
            chunk_index=chunk_index,
            content=table_element.content,
            section=f"table_p{table_element.page_number}",
            page_number=table_element.page_number,
            embedding=embedding,
            embedding_model=self.embedder.model_name if self.embedder else None,
        )

        chunk.extra_metadata = {
            "element_type": "table",
            "table_index": table_element.metadata.get("table_index"),
            "rows": table_element.metadata.get("rows"),
            "cols": table_element.metadata.get("cols"),
            "source_file": table_element.source_file,
        }

        self.session.add(chunk)
        logger.info(f"Indexed table from page {table_element.page_number} of paper {paper_id}")

        return chunk

    def get_elements_by_type(
        self,
        paper_id: str,
        element_type: DocumentElementType,
    ) -> List[DocumentChunk]:
        """Retrieve chunks of a specific element type from a paper."""
        return (
            self.session.query(DocumentChunk)
            .filter(
                DocumentChunk.paper_id == paper_id,
                DocumentChunk.section.like(f"{element_type.value}%"),
            )
            .all()
        )

    def get_tables_by_paper(self, paper_id: str) -> List[DocumentChunk]:
        """Get all table chunks from a paper."""
        return self.get_elements_by_type(paper_id, DocumentElementType.TABLE)

    def get_figures_by_paper(self, paper_id: str) -> List[DocumentChunk]:
        """Get all figure chunks from a paper."""
        return self.get_elements_by_type(paper_id, DocumentElementType.FIGURE)
