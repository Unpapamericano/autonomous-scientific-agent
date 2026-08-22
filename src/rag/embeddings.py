"""
Phase 4: Embeddings Generation

Generates vector embeddings for papers and document chunks using
sentence-transformers. Embeddings enable semantic similarity search
(as opposed to Phase 3's keyword-based search).

Model: all-MiniLM-L6-v2 (default) — fast, 384-dim, good quality.
Alternative: all-mpnet-base-v2 (768-dim, higher quality, slower).
"""

import logging
from typing import List, Optional, Union
from functools import lru_cache

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # dimension for all-MiniLM-L6-v2


class EmbeddingGenerator:
    """
    Generates embeddings for text using sentence-transformers.

    Lazily loads the model on first use to avoid slowing down
    imports/tests that don't need embeddings.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL, device: Optional[str] = None):
        """
        Initialize embedding generator.

        Args:
            model_name: HuggingFace sentence-transformers model name
            device: "cuda", "cpu", or None (auto-detect)
        """
        self.model_name = model_name
        self.device = device
        self._model = None  # Lazy-loaded

        logger.info(f"EmbeddingGenerator configured with model={model_name}")

    @property
    def model(self):
        """Lazily load the sentence-transformers model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"✓ Embedding model loaded (dim={self._model.get_sentence_embedding_dimension()})")

        return self._model

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector as a list of floats
        """
        if not text or not text.strip():
            logger.warning("Empty text passed to embed_text, returning zero vector")
            return [0.0] * EMBEDDING_DIM

        embedding = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (efficient batching).

        Args:
            texts: List of input texts
            batch_size: Batch size for encoding

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Replace empty strings to avoid errors
        safe_texts = [t if t and t.strip() else " " for t in texts]

        embeddings = self.model.encode(
            safe_texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 50,
        )

        logger.info(f"Generated {len(embeddings)} embeddings (dim={embeddings.shape[1]})")
        return embeddings.tolist()

    def similarity(self, embedding_a: List[float], embedding_b: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.

        Since embeddings are normalized, this is a simple dot product.

        Args:
            embedding_a: First embedding vector
            embedding_b: Second embedding vector

        Returns:
            Cosine similarity score (-1.0 to 1.0)
        """
        a = np.array(embedding_a)
        b = np.array(embedding_b)
        return float(np.dot(a, b))

    def rank_by_similarity(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: Optional[int] = None,
    ) -> List[int]:
        """
        Rank candidate embeddings by similarity to query embedding.

        Args:
            query_embedding: Query vector
            candidate_embeddings: List of candidate vectors
            top_k: Return only top K results (None = all)

        Returns:
            List of indices into candidate_embeddings, sorted by similarity (desc)
        """
        query = np.array(query_embedding)
        candidates = np.array(candidate_embeddings)

        # Cosine similarity via dot product (embeddings are normalized)
        scores = candidates @ query

        # Sort descending
        ranked_indices = np.argsort(-scores)

        if top_k is not None:
            ranked_indices = ranked_indices[:top_k]

        return ranked_indices.tolist()


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
) -> List[str]:
    """
    Split text into overlapping chunks for embedding.

    Args:
        text: Full text to chunk
        chunk_size: Target chunk size in words
        overlap: Overlap between chunks in words

    Returns:
        List of text chunks
    """
    if not text:
        return []

    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    logger.info(f"Chunked text ({len(words)} words) into {len(chunks)} chunks")
    return chunks


# Global singleton instance
_embedding_generator: Optional[EmbeddingGenerator] = None


def get_embedding_generator(model_name: str = DEFAULT_MODEL) -> EmbeddingGenerator:
    """Get or create the global embedding generator singleton."""
    global _embedding_generator

    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator(model_name=model_name)

    return _embedding_generator
