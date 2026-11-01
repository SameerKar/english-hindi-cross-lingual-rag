"""
Embedding models abstraction layer for monolingual English and cross-lingual multilingual encoders.
Enforces vector L2-normalization so that FAISS Inner Product matches Cosine Similarity.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

class BaseEmbedder(ABC):
    """
    Abstract Base Class for all embedding models.
    """
    def __init__(self, model_name: str, normalize: bool = True, dimension: int = 768):
        self.model_name = model_name
        self.normalize = normalize
        self.dimension = dimension

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embeds a batch of documents/chunks. Returns a float32 ndarray of shape (N, dimension).
        """
        pass

    @abstractmethod
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embeds a single query string. Returns a float32 ndarray of shape (1, dimension).
        """
        pass

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        """
        Applies L2 normalization across vectors so that dot product equals cosine similarity.
        """
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1e-12, norms)
        return (vectors / norms).astype(np.float32)


class SentenceTransformerEmbedder(BaseEmbedder):
    """
    Embedder implementation using the HuggingFace sentence-transformers library.
    """
    def __init__(self, model_name: str, normalize: bool = True, device: str = "cpu", batch_size: int = 32):
        self.device = device
        self.batch_size = batch_size
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[Embedder] Loading SentenceTransformer: {model_name} on {device}...")
            self.model = SentenceTransformer(model_name, device=device)
            dim = self.model.get_sentence_embedding_dimension()
            super().__init__(model_name=model_name, normalize=normalize, dimension=dim)
        except Exception as e:
            print(f"[Warning] Failed to load SentenceTransformer ({model_name}): {e}")
            print("  -> Falling back to deterministic MockEmbedder for testing.")
            self.model = None
            super().__init__(model_name=f"mock-{model_name}", normalize=normalize, dimension=768)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        if self.model is not None:
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=self.normalize
            )
            return embeddings.astype(np.float32)
        else:
            return self._mock_embed(texts)

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])

    def _mock_embed(self, texts: List[str]) -> np.ndarray:
        """
        Deterministic pseudo-embedding based on character hashing and TF heuristics.
        Used as a safety fallback when torch / sentence-transformers weights are inaccessible.
        """
        out = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for i, text in enumerate(texts):
            words = text.lower().split()
            vec = np.zeros(self.dimension, dtype=np.float32)
            for word in words:
                h = hash(word) % self.dimension
                vec[h] += 1.0
            out[i] = vec
        return self._normalize(out) if self.normalize else out.astype(np.float32)


class MockEmbedder(BaseEmbedder):
    """
    Lightweight, instant embedder for testing and CI pipelines without GPU or model downloads.
    """
    def __init__(self, model_name: str = "mock-embedder", dimension: int = 768, normalize: bool = True):
        super().__init__(model_name=model_name, normalize=normalize, dimension=dimension)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for i, text in enumerate(texts):
            words = text.lower().split()
            vec = np.zeros(self.dimension, dtype=np.float32)
            for word in words:
                h = hash(word) % self.dimension
                vec[h] += 1.0
            out[i] = vec
        return self._normalize(out) if self.normalize else out.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])


def get_embedder(model_name: str, normalize: bool = True, device: str = "cpu", force_mock: bool = False) -> BaseEmbedder:
    """
    Factory function to instantiate the appropriate embedder.
    """
    if force_mock:
        return MockEmbedder(model_name=model_name, normalize=normalize)
    return SentenceTransformerEmbedder(model_name=model_name, normalize=normalize, device=device)
