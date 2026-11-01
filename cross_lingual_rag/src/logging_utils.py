"""
Experiment logging and observability module.
Enforces strict JSON schema per execution run, saving granular latency, chunk rankings, and errors.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from .chunking import DocumentChunk
from .utils import ensure_directory

class ExperimentLogger:
    """
    Manages structured JSON run logging for scientific auditing and metric calculation.
    """
    def __init__(self, results_raw_dir: str):
        self.raw_dir = Path(results_raw_dir)
        ensure_directory(str(self.raw_dir))

    def log_run(
        self,
        question_id: str,
        system_id: str,
        original_question: str,
        generated_answer: str,
        latencies: Dict[str, float],
        subject: str = "general",
        category: str = "general",
        translated_question: Optional[str] = None,
        retrieved_chunks: Optional[List[DocumentChunk]] = None,
        retrieval_scores: Optional[List[float]] = None,
        intermediate_answer_en: Optional[str] = None,
        model_name: str = "unknown",
        embedding_model: str = "unknown",
        translation_model: str = "none",
        top_k: int = 5,
        temperature: float = 0.0,
        error_status: str = "SUCCESS",
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates and writes a verified JSON record conforming to the research schema.
        """
        run_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        chunk_ids = [c.chunk_id for c in (retrieved_chunks or [])]
        scores = [float(s) for s in (retrieval_scores or [])]
        
        source_documents = []
        if retrieved_chunks:
            for rank, c in enumerate(retrieved_chunks, 1):
                source_documents.append({
                    "doc_id": c.doc_id,
                    "page": c.page,
                    "chunk_id": c.chunk_id,
                    "subject": c.subject,
                    "rank": rank
                })

        record = {
            "run_id": run_id,
            "timestamp": timestamp,
            "question_id": question_id,
            "system_id": system_id,
            "subject": subject,
            "category": category,
            "original_question": original_question,
            "translated_question": translated_question,
            "top_k": top_k,
            "retrieved_chunks": chunk_ids,
            "retrieval_scores": scores,
            "source_documents": source_documents,
            "generated_answer": generated_answer,
            "intermediate_answer_en": intermediate_answer_en,
            "model_name": model_name,
            "embedding_model": embedding_model,
            "translation_model": translation_model,
            "temperature": temperature,
            "latencies": {
                "translation_latency_ms": round(latencies.get("translation_latency_ms", 0.0), 2),
                "retrieval_latency_ms": round(latencies.get("retrieval_latency_ms", 0.0), 2),
                "generation_latency_ms": round(latencies.get("generation_latency_ms", 0.0), 2),
                "total_latency_ms": round(latencies.get("total_latency_ms", 0.0), 2)
            },
            "error_status": error_status,
            "error_message": error_message
        }

        # Save to results/raw/system_{system_id}/{run_id}.json
        sys_folder = self.raw_dir / f"system_{system_id}"
        ensure_directory(str(sys_folder))

        file_path = sys_folder / f"{run_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        return record
