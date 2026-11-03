"""
FAISS Vector Store wrapper with exact Cosine/Inner-Product similarity search.
Enforces strict 1-to-1 mapping from vector index IDs to DocumentChunk metadata.
Supports Reference Benchmark mode and isolated Custom Workspace modes.
Includes a pure NumPy Cosine fallback if faiss-cpu binary is unavailable.
"""

import os
import sys
import pickle
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

try:
    from .chunking import DocumentChunk
    from .embeddings import BaseEmbedder, get_embedder
    from .utils import load_config, ensure_directory, get_project_root
except (ImportError, ValueError):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.chunking import DocumentChunk
    from src.embeddings import BaseEmbedder, get_embedder
    from src.utils import load_config, ensure_directory, get_project_root

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[Notice] FAISS not found in environment; using exact NumPy FlatIP vector engine.")


class FAISSVectorStore:
    """
    Manages FAISS IndexFlatIP indexing, persistence, and nearest-neighbor search.
    """
    def __init__(self, index_name: str = "vector_index"):
        self.index_name = index_name
        self.index = None
        self.vectors_np: Optional[np.ndarray] = None  # Fallback array
        self.metadata_map: Dict[int, DocumentChunk] = {}
        self.dimension: int = 768

    def build_from_chunks(self, chunks: List[DocumentChunk], embedder: BaseEmbedder, save_dir: Path) -> int:
        """
        Embeds chunks in batches, constructs the FAISS index, and persists index + metadata.
        """
        if not chunks:
            print("[VectorStore] No chunks provided to index.")
            return 0

        ensure_directory(str(save_dir))
        texts = [chunk.text for chunk in chunks]
        print(f"[VectorStore] Embedding {len(texts)} chunks with {embedder.model_name}...")
        vectors = embedder.embed_texts(texts)
        self.dimension = vectors.shape[1]

        # Build index
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.index.add(vectors)
        else:
            self.vectors_np = vectors

        # Record metadata mapping
        self.metadata_map = {i: chunks[i] for i in range(len(chunks))}

        # Persist to disk
        self.save(save_dir)
        print(f"[VectorStore] Successfully built and saved index with {len(chunks)} vectors at {save_dir}")
        return len(chunks)

    def save(self, save_dir: Path) -> None:
        """Saves index.faiss (or vectors.npy) and metadata_map.pkl."""
        ensure_directory(str(save_dir))
        meta_file = save_dir / "metadata_map.pkl"
        with open(meta_file, "wb") as f:
            pickle.dump(self.metadata_map, f)

        if FAISS_AVAILABLE and self.index is not None:
            index_file = save_dir / "index.faiss"
            faiss.write_index(self.index, str(index_file))
        else:
            npy_file = save_dir / "vectors.npy"
            if self.vectors_np is not None:
                np.save(str(npy_file), self.vectors_np)

    def load(self, save_dir: Path) -> bool:
        """Loads index and metadata mapping from disk, checking fallback locations if needed."""
        candidate_dirs = [save_dir]
        root = get_project_root()
        # Fallback paths
        if "reference" in str(save_dir) or "indexes/reference" in str(save_dir):
            if "english" in str(save_dir):
                candidate_dirs.append(root / "data" / "indexes" / "english")
            elif "multilingual" in str(save_dir):
                candidate_dirs.append(root / "data" / "indexes" / "multilingual")
        elif "data/indexes" in str(save_dir):
            if "english" in str(save_dir):
                candidate_dirs.append(root / "indexes" / "reference" / "english")
            elif "multilingual" in str(save_dir):
                candidate_dirs.append(root / "indexes" / "reference" / "multilingual")

        for target_dir in candidate_dirs:
            meta_file = target_dir / "metadata_map.pkl"
            if not meta_file.exists():
                continue

            with open(meta_file, "rb") as f:
                try:
                    self.metadata_map = pickle.load(f)
                except Exception:
                    f.seek(0)
                    class _SafeUnpickler(pickle.Unpickler):
                        def find_class(self, module, name):
                            if module.startswith("cross_lingual_rag.src"):
                                alt = module.replace("cross_lingual_rag.src", "src")
                                try:
                                    return super().find_class(alt, name)
                                except Exception:
                                    pass
                            elif module.startswith("src."):
                                alt = "cross_lingual_rag." + module
                                try:
                                    return super().find_class(alt, name)
                                except Exception:
                                    pass
                            return super().find_class(module, name)
                    self.metadata_map = _SafeUnpickler(f).load()

            index_file = target_dir / "index.faiss"
            npy_file = target_dir / "vectors.npy"

            if FAISS_AVAILABLE and index_file.exists():
                self.index = faiss.read_index(str(index_file))
                self.dimension = self.index.d
                return True
            elif npy_file.exists():
                self.vectors_np = np.load(str(npy_file))
                self.dimension = self.vectors_np.shape[1]
                return True

        return False

    def search(self, query_vector: np.ndarray, top_k: int = 5, subject_filter: Optional[str] = None) -> List[Tuple[DocumentChunk, float]]:
        """
        Searches index using query vector. Returns top_k (DocumentChunk, score) tuples.
        Supports filtering by subject or scope.
        """
        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)

        num_items = len(self.metadata_map)
        if num_items == 0:
            return []

        effective_filter = subject_filter
        if effective_filter == "uploaded_only":
            default_subs = {"algorithms", "automata", "computer_networks", "dbms", "operating_systems"}
            has_uploaded = any(c.subject.lower() not in default_subs for c in self.metadata_map.values())
            if not has_uploaded:
                effective_filter = "all"

        k_search = min(num_items, max(top_k * 5, 25)) if (effective_filter and effective_filter != "all") else min(top_k, num_items)

        if FAISS_AVAILABLE and self.index is not None:
            distances, indices = self.index.search(query_vector.astype(np.float32), k_search)
            scores = distances[0]
            idx_list = indices[0]
        elif self.vectors_np is not None:
            sims = np.dot(self.vectors_np, query_vector.T).flatten()
            idx_list = np.argsort(-sims)[:k_search]
            scores = sims[idx_list]
        else:
            return []

        results = []
        for rank_idx, vec_id in enumerate(idx_list):
            if vec_id in self.metadata_map and vec_id != -1:
                chunk = self.metadata_map[vec_id]
                score = float(scores[rank_idx])

                if effective_filter and effective_filter != "all":
                    if effective_filter == "uploaded_only":
                        default_subs = {"algorithms", "automata", "computer_networks", "dbms", "operating_systems"}
                        if chunk.subject.lower() in default_subs:
                            continue
                    elif chunk.subject.lower() != effective_filter.lower():
                        continue

                results.append((chunk, score))
                if len(results) >= top_k:
                    break

        return results


def build_dual_indexes(config: Dict[str, Any], chunks: Optional[List[DocumentChunk]] = None,
                       mode: str = "reference", workspace_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Builds both English index and Multilingual index on the exact same underlying chunks.
    Supports Reference mode and isolated Custom Workspace mode.
    """
    root = get_project_root()

    if chunks is None:
        if mode == "custom" and workspace_id:
            manifest_path = root / "data" / "corpus" / "custom" / workspace_id / "processed" / "chunks_manifest.json"
        else:
            manifest_path = root / "data" / "processed" / "chunks_manifest.json"

        if not manifest_path.exists():
            print(f"[Error] Chunks manifest missing at {manifest_path}. Run ingestion first.")
            return {"status": "error", "message": f"Manifest missing at {manifest_path}"}

        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        chunks = [DocumentChunk.from_dict(c) for c in data]

    print(f"[Dual Indexer] Ingested {len(chunks)} chunks for indexing (Mode: {mode}).")

    emb_cfg = config.get("embedding", {})
    norm = emb_cfg.get("normalize_embeddings", True)
    dev = emb_cfg.get("device", "cpu")

    # Determine directories based on mode
    if mode == "custom" and workspace_id:
        base_idx_dir = root / "indexes" / "custom" / workspace_id
        eng_dir = base_idx_dir / "english"
        multi_dir = base_idx_dir / "multilingual"
        manifest_file = base_idx_dir / "index_manifest.json"
    else:
        eng_dir = root / Path(config["paths"].get("english_index_dir", "indexes/reference/english"))
        multi_dir = root / Path(config["paths"].get("multilingual_index_dir", "indexes/reference/multilingual"))
        manifest_file = eng_dir.parent / "index_manifest.json"

    # 1. Build English Index (for Systems B & C)
    eng_model = emb_cfg.get("english_model", "sentence-transformers/all-mpnet-base-v2")
    eng_embedder = get_embedder(eng_model, normalize=norm, device=dev)
    eng_store = FAISSVectorStore("english_index")
    eng_store.build_from_chunks(chunks, eng_embedder, eng_dir)

    # 2. Build Multilingual Index (for System D)
    multi_model = emb_cfg.get("multilingual_model", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    multi_embedder = get_embedder(multi_model, normalize=norm, device=dev)
    multi_store = FAISSVectorStore("multilingual_index")
    multi_store.build_from_chunks(chunks, multi_embedder, multi_dir)

    # For reference mode, also mirror to data/indexes for legacy backwards-compatibility
    if mode == "reference":
        legacy_eng = root / "data" / "indexes" / "english"
        legacy_multi = root / "data" / "indexes" / "multilingual"
        eng_store.save(legacy_eng)
        multi_store.save(legacy_multi)

    # Write index manifest
    manifest_info = {
        "mode": mode,
        "workspace_id": workspace_id,
        "total_chunks": len(chunks),
        "english_model": eng_model,
        "english_dimension": eng_store.dimension,
        "multilingual_model": multi_model,
        "multilingual_dimension": multi_store.dimension,
        "normalized": norm,
        "device": dev,
        "built_at": datetime.now().isoformat()
    }
    ensure_directory(str(manifest_file.parent))
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_info, f, indent=2)

    print(f"[Dual Indexer Complete] Both English and Multilingual vector indexes successfully constructed at {manifest_file.parent}.")
    return manifest_info


if __name__ == "__main__":
    cfg = load_config()
    build_dual_indexes(cfg, mode="reference")
