"""
Basic 10-point Smoke Test and Integration Suite for Cross-Lingual Academic RAG.
Verifies all pipelines (A, B, C, D), vector indexing, latency logging, and schema integrity.
"""

import os
import sys
import json
import pytest
import numpy as np
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.utils import load_config, get_project_root
from src.chunking import PageAwareChunker, DocumentChunk
from src.ingestion import CorpusIngestor
from src.embeddings import MockEmbedder, get_embedder
from src.vector_store import FAISSVectorStore
from src.translation import TranslationService
from src.generation import LLMGenerator
from src.pipelines import PipelineOrchestrator
from src.evaluation import EvaluationHarness

@pytest.fixture(scope="module")
def test_config():
    cfg = load_config()
    # Force mock generation and mock translation for deterministic test execution
    cfg["generation"]["provider"] = "mock"
    cfg["translation"]["provider"] = "mock"
    return cfg

def test_page_aware_chunking():
    """Verify that chunks preserve page numbers and assign stable deterministic IDs."""
    chunker = PageAwareChunker(chunk_size=300, chunk_overlap=30)
    sample_page = (
        "Dijkstra's algorithm solves the single-source shortest path problem. "
        "It uses a priority queue to greedily extract the minimum distance vertex. "
        "However, it fails when negative edge weights are present in the graph."
    )
    chunks = chunker.split_page_text(
        page_text=sample_page,
        doc_id="algo_test",
        subject="algorithms",
        page_number=4
    )
    assert len(chunks) >= 1
    chunk = chunks[0]
    assert chunk.page == 4
    assert chunk.doc_id == "algo_test"
    assert chunk.chunk_id == "algo_test_p4_c0"
    assert "Dijkstra" in chunk.text

def test_embeddings_normalization():
    """Verify that embeddings are L2 normalized to unit length."""
    embedder = MockEmbedder(dimension=768, normalize=True)
    vectors = embedder.embed_texts(["What is a deadlock?", "Dijkstra algorithm complexity"])
    assert vectors.shape == (2, 768)
    # Check L2 norm is approximately 1.0
    norms = np.linalg.norm(vectors, axis=1)
    np.testing.assert_allclose(norms, [1.0, 1.0], rtol=1e-5)

def test_vector_store_build_and_search(tmp_path):
    """Verify building, saving, loading, and searching FAISS / FlatIP vector store."""
    embedder = MockEmbedder(dimension=768, normalize=True)
    store = FAISSVectorStore("test_index")

    c1 = DocumentChunk("doc1_p1_c0", "doc1", "os", 1, 0, "Deadlock occurs when four conditions hold.", 10, {})
    c2 = DocumentChunk("doc1_p2_c0", "doc1", "os", 2, 0, "Virtual memory uses page tables and TLB.", 10, {})
    chunks = [c1, c2]

    num_indexed = store.build_from_chunks(chunks, embedder, tmp_path)
    assert num_indexed == 2

    # Test Reloading
    new_store = FAISSVectorStore("test_index")
    loaded = new_store.load(tmp_path)
    assert loaded is True
    assert len(new_store.metadata_map) == 2

    # Test Search
    query_vec = embedder.embed_query("deadlock conditions")
    results = new_store.search(query_vec, top_k=2)
    assert len(results) == 2
    assert results[0][0].chunk_id in ["doc1_p1_c0", "doc1_p2_c0"]
    assert 0.0 <= results[0][1] <= 1.01

def test_translation_service(test_config):
    """Verify translation returns text, positive latency, and handles errors cleanly."""
    translator = TranslationService(test_config)
    trans_text, lat_ms, err = translator.translate_hi_to_en("डाइक्स्ट्रा का एल्गोरिदम")
    assert "Dijkstra" in trans_text or len(trans_text) > 0
    assert lat_ms >= 0.0
    assert err is None

def test_all_four_pipelines(test_config):
    """Smoke test: executes Systems A, B, C, and D on a sample academic question."""
    orchestrator = PipelineOrchestrator(test_config)

    q_hi = "डेडलॉक की चार आवश्यक शर्तें क्या हैं?"
    q_en = "What are the four necessary conditions for deadlock?"

    # 1. System A
    res_a = orchestrator.execute_system_A(q_hi, "SMOKE_01", "Operating Systems", "Factual")
    assert res_a["system_id"] == "A"
    assert res_a["error_status"] == "SUCCESS"
    assert res_a["latencies"]["total_latency_ms"] >= 0.0

    # 2. System B
    res_b = orchestrator.execute_system_B(q_en, "SMOKE_01", "Operating Systems", "Factual")
    assert res_b["system_id"] == "B"
    assert res_b["error_status"] == "SUCCESS"

    # 3. System C
    res_c = orchestrator.execute_system_C(q_hi, "SMOKE_01", "Operating Systems", "Factual")
    assert res_c["system_id"] == "C"
    assert res_c["translated_question"] is not None
    assert res_c["error_status"] == "SUCCESS"

    # 4. System D
    res_d = orchestrator.execute_system_D(q_hi, "SMOKE_01", "Operating Systems", "Factual")
    assert res_d["system_id"] == "D"
    assert res_d["error_status"] == "SUCCESS"

def test_json_logging_schema(test_config):
    """Verify that JSON log files saved to disk contain all mandatory schema fields."""
    raw_dir = Path(test_config["paths"]["results_raw_dir"])
    log_files = list(raw_dir.rglob("*.json"))
    assert len(log_files) > 0, "At least one log file must have been written."

    sample_file = log_files[0]
    with open(sample_file, "r", encoding="utf-8") as f:
        record = json.load(f)

    required_keys = [
        "run_id", "timestamp", "question_id", "system_id", "original_question",
        "retrieved_chunks", "retrieval_scores", "source_documents", "generated_answer",
        "model_name", "embedding_model", "top_k", "temperature", "latencies",
        "error_status", "error_message"
    ]
    for key in required_keys:
        assert key in record, f"Missing mandatory field in log: {key}"

    # Latency sub-fields check
    lat = record["latencies"]
    for l_key in ["translation_latency_ms", "retrieval_latency_ms", "generation_latency_ms", "total_latency_ms"]:
        assert l_key in lat, f"Missing latency sub-field: {l_key}"

def test_evaluation_metrics_computation(test_config):
    """Verify MRR, Recall@k, and nDCG calculations."""
    evaluator = EvaluationHarness(test_config)
    gold = "algo_clrs_p45_c2"
    retrieved = ["algo_clrs_p10_c1", "algo_clrs_p45_c2", "algo_clrs_p99_c0"]

    assert evaluator.compute_recall_at_k(gold, retrieved, k=1) == 0.0
    assert evaluator.compute_recall_at_k(gold, retrieved, k=2) == 1.0
    assert evaluator.compute_recall_at_k(gold, retrieved, k=5) == 1.0
    assert evaluator.compute_mrr(gold, retrieved) == pytest.approx(0.5) # Rank 2 -> 1/2
    assert evaluator.compute_ndcg_at_k(gold, retrieved, k=5) > 0.0
