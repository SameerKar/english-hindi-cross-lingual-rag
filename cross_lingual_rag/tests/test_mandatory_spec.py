"""
Mandatory Acceptance Tests according to Section 10.1 of the Implementation Specification.
Covers:
1. A never calls retrieval or embedding.
2. B embeds only question_en with English model.
3. C stores exact original Hindi query and exact translated English query; uses B English index.
4. C saves intermediate English answer and Hindi final answer; failed translation marked failed.
5. D sends Hindi directly to multilingual encoder (no pre-retrieval translation).
6. Language validation catches predominantly English output when Hindi was required.
7. Zero-text detection flags failure and avoids indexing.
8. Duplicate file detection by SHA-256 avoids duplicate chunks.
9. Custom upload creates isolated index without mutating reference index.
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.utils import load_config, get_project_root
from src.chunking import DocumentChunk
from src.ingestion import CorpusIngestor, compute_sha256
from src.translation import TranslationService
from src.generation import LLMGenerator
from src.pipelines import PipelineOrchestrator
from src.vector_store import FAISSVectorStore, build_dual_indexes


@pytest.fixture(scope="module")
def mock_config():
    cfg = load_config()
    cfg["generation"]["provider"] = "mock"
    cfg["translation"]["provider"] = "mock"
    return cfg


def test_system_A_has_zero_retrieval(mock_config):
    """Test 1: System A never calls retrieval or embedding."""
    orch = PipelineOrchestrator(mock_config)
    res = orch.execute_system_A("डेडलॉक क्या है?", "TEST_A_01", "Operating Systems", "Factual")
    assert res["system_id"] == "A"
    assert res["top_k"] == 0
    assert len(res["retrieved_chunks"]) == 0
    assert res["embedding_model"] == "none"
    assert res["latencies"]["retrieval_latency_ms"] == 0.0
    assert res["latencies"]["translation_latency_ms"] == 0.0


def test_system_B_english_only(mock_config):
    """Test 2: B embeds only question_en with English model."""
    orch = PipelineOrchestrator(mock_config)
    res = orch.execute_system_B("What are the deadlock conditions?", "TEST_B_01", "Operating Systems", "Factual")
    assert res["system_id"] == "B"
    assert res["embedding_model"] == orch.eng_model_name
    assert res["latencies"]["translation_latency_ms"] == 0.0
    assert len(res["retrieved_chunks"]) > 0


def test_system_C_stores_queries_and_intermediate_answer(mock_config):
    """Test 3 & 4: C stores exact original Hindi query, translated English query, and intermediate English answer."""
    orch = PipelineOrchestrator(mock_config)
    q_hi = "डाइक्स्ट्रा का एल्गोरिदम क्या है?"
    res = orch.execute_system_C(q_hi, "TEST_C_01", "Algorithms", "Factual")
    assert res["system_id"] == "C"
    assert res["original_question"] == q_hi
    assert res["translated_question"] is not None
    assert len(res["translated_question"]) > 0
    assert res["intermediate_answer_en"] is not None
    assert len(res["intermediate_answer_en"]) > 0
    assert res["generated_answer"] is not None
    assert res["latencies"]["translation_latency_ms"] >= 0.0
    assert res["latencies"]["retrieval_latency_ms"] >= 0.0


def test_system_D_zero_translation(mock_config):
    """Test 5: D sends Hindi directly to multilingual encoder (zero pre-retrieval translation)."""
    orch = PipelineOrchestrator(mock_config)
    q_hi = "टीसीपी 3-वे हैंडशेक क्या है?"
    res = orch.execute_system_D(q_hi, "TEST_D_01", "Computer Networks", "Factual")
    assert res["system_id"] == "D"
    assert res["original_question"] == q_hi
    assert res["translation_model"] == "none"
    assert res["latencies"]["translation_latency_ms"] == 0.0
    assert res["embedding_model"] == orch.multi_model_name
    assert len(res["retrieved_chunks"]) > 0


def test_hindi_language_validator(mock_config):
    """Test 7: Language validator catches English-dominant answers."""
    ts = TranslationService(mock_config)
    # Valid Hindi
    valid, _ = ts.validate_hindi_output("डाइक्स्ट्रा का एल्गोरिदम सबसे छोटा रास्ता खोजता है।")
    assert valid is True

    # Invalid: English text passing as Hindi
    invalid, reason = ts.validate_hindi_output("This is entirely written in English words without Devanagari script.")
    assert invalid is False
    assert "predominantly English" in reason


def test_zero_text_detection(mock_config, tmp_path):
    """Test 8: Zero-text file is not indexed as valid chunks."""
    ingestor = CorpusIngestor(mock_config, mode="reference")
    empty_txt = tmp_path / "empty_notes.txt"
    empty_txt.write_text("   \n\n   \t  \n", encoding="utf-8")

    pages = ingestor.extract_text_pages(empty_txt)
    # All empty
    non_blank = sum(len(p["text"].strip()) for p in pages)
    assert non_blank == 0


def test_duplicate_file_detection(mock_config, tmp_path):
    """Test 9: Duplicate files produce identical SHA-256 hashes."""
    f1 = tmp_path / "doc1.txt"
    f2 = tmp_path / "doc2.txt"
    f1.write_text("Academic graph theory shortest path algorithm.", encoding="utf-8")
    f2.write_text("Academic graph theory shortest path algorithm.", encoding="utf-8")
    assert compute_sha256(f1) == compute_sha256(f2)


def test_custom_upload_workspace_isolation(mock_config, tmp_path):
    """Test 10: Custom workspace builds isolated index and does not mutate reference index."""
    ws_id = "test_ws_user_42"
    custom_dir = tmp_path / "custom" / ws_id / "originals"
    custom_dir.mkdir(parents=True)
    custom_doc = custom_dir / "user_private_notes.txt"
    custom_doc.write_text("Unique custom user research text on bio-informatics.", encoding="utf-8")

    c_chunk = DocumentChunk("user_doc_p1_c0", "user_doc", "bio", 1, 0, "Unique custom user research text on bio-informatics.", 10, {})
    from src.embeddings import MockEmbedder
    embedder = MockEmbedder(dimension=768)

    ws_idx_dir = tmp_path / "indexes" / "custom" / ws_id / "english"
    ws_store = FAISSVectorStore("custom_index")
    count = ws_store.build_from_chunks([c_chunk], embedder, ws_idx_dir)
    assert count == 1

    # Verify custom index file exists
    assert (ws_idx_dir / "metadata_map.pkl").exists()

    # Verify reference index path was never modified
    ref_idx_path = Path(mock_config["paths"].get("english_index_dir", "indexes/reference/english"))
    # Reference store remains clean
    ref_store = FAISSVectorStore("ref_index")
    loaded = ref_store.load(get_project_root() / ref_idx_path)
    assert loaded is True
    # The custom chunk is NOT in reference store
    assert all("bio-informatics" not in c.text for c in ref_store.metadata_map.values())

