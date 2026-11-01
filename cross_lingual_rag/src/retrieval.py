"""
Retrieval coordinator for English and Multilingual Vector Stores.
Executes query vectorization, FAISS search, context formatting, and latency tracking.
"""

import time
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from .chunking import DocumentChunk
from .embeddings import BaseEmbedder
from .vector_store import FAISSVectorStore

class Retriever:
    """
    Coordinates semantic vector search against an underlying FAISS index.
    """
    def __init__(self, vector_store: FAISSVectorStore, embedder: BaseEmbedder, top_k: int = 5):
        self.vector_store = vector_store
        self.embedder = embedder
        self.top_k = top_k

    def retrieve(self, query: str, top_k: Optional[int] = None) -> Tuple[List[DocumentChunk], List[float], float]:
        """
        Encodes query string, searches vector store, and returns:
        (retrieved_chunks, similarity_scores, retrieval_latency_ms)
        """
        k = top_k if top_k is not None else self.top_k
        start_time = time.perf_counter()

        # Generate query embedding
        query_vec = self.embedder.embed_query(query)

        # Execute search in vector store
        search_results = self.vector_store.search(query_vec, top_k=k)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        chunks = [res[0] for res in search_results]
        scores = [res[1] for res in search_results]

        return chunks, scores, latency_ms

    @staticmethod
    def format_context(chunks: List[DocumentChunk]) -> str:
        """
        Formats retrieved chunks into a standardized academic context block for LLM prompts.
        """
        if not chunks:
            return "[No relevant context found in index]"

        context_blocks = []
        for rank, chunk in enumerate(chunks, 1):
            block = (
                f"--- [Document Passage {rank} | ID: {chunk.chunk_id} | Page: {chunk.page} | Subject: {chunk.subject}] ---\n"
                f"{chunk.text}\n"
            )
            context_blocks.append(block)

        return "\n".join(context_blocks)
