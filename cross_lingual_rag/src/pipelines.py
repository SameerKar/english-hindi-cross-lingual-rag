"""
Pipeline Orchestration Engine for Systems A, B, C, and D.
Executes query workflows, monitors latencies across stages, enforces experimental controls,
logs atomic JSON audit records, and integrates deep OpenTelemetry/LangSmith observability spans.
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

from .utils import load_config, get_project_root
from .embeddings import get_embedder
from .vector_store import FAISSVectorStore
from .retrieval import Retriever
from .translation import TranslationService
from .generation import LLMGenerator
from .logging_utils import ExperimentLogger
from .observability import ObservabilityTracer

class PipelineOrchestrator:
    """
    Coordinates end-to-end execution of Systems A, B, C, and D with deep observability.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.root = get_project_root()
        
        # Initialize Logger
        self.logger = ExperimentLogger(config["paths"]["results_raw_dir"])

        # Initialize Observability Tracer (LangSmith + Local Free Traces)
        self.tracer = ObservabilityTracer()

        # Initialize Translation Service
        self.translator = TranslationService(config)

        # Initialize LLM Generator
        self.generator = LLMGenerator(config)

        # Initialize Embedding Models
        emb_cfg = config.get("embedding", {})
        norm = emb_cfg.get("normalize_embeddings", True)
        dev = emb_cfg.get("device", "cpu")
        
        self.eng_model_name = emb_cfg.get("english_model", "sentence-transformers/all-mpnet-base-v2")
        self.eng_embedder = get_embedder(self.eng_model_name, normalize=norm, device=dev)

        self.multi_model_name = emb_cfg.get("multilingual_model", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.multi_embedder = get_embedder(self.multi_model_name, normalize=norm, device=dev)

        # Initialize Vector Stores
        self.eng_store = FAISSVectorStore("english_index")
        self.eng_store_loaded = self.eng_store.load(Path(config["paths"]["english_index_dir"]))

        self.multi_store = FAISSVectorStore("multilingual_index")
        self.multi_store_loaded = self.multi_store.load(Path(config["paths"]["multilingual_index_dir"]))

        # Initialize Retrievers
        top_k = config.get("retrieval", {}).get("top_k", 5)
        self.eng_retriever = Retriever(self.eng_store, self.eng_embedder, top_k=top_k)
        self.multi_retriever = Retriever(self.multi_store, self.multi_embedder, top_k=top_k)

        # Load Prompt Templates
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, str]:
        p_dir = Path(self.config["paths"]["prompts_dir"])
        templates = {}
        
        def read_p(fname, fallback):
            path = p_dir / fname
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            return fallback

        templates["english"] = read_p("rag_prompt_english.txt", "Question: {question}\nContext:\n{context}\nAnswer:")
        templates["hindi"] = read_p("rag_prompt_hindi.txt", "Question in Hindi: {question}\nEnglish Context:\n{context}\nAnswer in Hindi:")
        templates["direct"] = read_p("direct_llm_prompt.txt", "Question: {question}\nAnswer:")
        return templates

    def execute_system_A(self, question: str, question_id: str, subject: str = "general", category: str = "general") -> Dict[str, Any]:
        """
        System A: Direct LLM Baseline (No retrieval).
        """
        start_total = time.perf_counter()
        self.tracer.start_trace(question_id, "A", question, {"subject": subject, "category": category})

        prompt = self.prompts["direct"].format(question=question)

        # Span: LLM Generation
        span_gen = self.tracer.start_span("llm_generation", "llm", {"prompt": prompt, "model": self.generator.model_name})
        ans, gen_lat, err, tokens = self.generator.generate(prompt)
        self.tracer.end_span(span_gen, {"answer": ans, "tokens": tokens}, error=err)

        total_lat = (time.perf_counter() - start_total) * 1000.0
        self.tracer.end_trace(ans, error=err)

        latencies = {
            "translation_latency_ms": 0.0,
            "retrieval_latency_ms": 0.0,
            "generation_latency_ms": gen_lat,
            "total_latency_ms": total_lat
        }

        return self.logger.log_run(
            question_id=question_id,
            system_id="A",
            subject=subject,
            category=category,
            original_question=question,
            generated_answer=ans,
            latencies=latencies,
            model_name=self.generator.model_name,
            embedding_model="none",
            top_k=0,
            temperature=self.generator.temperature,
            error_status="FAILURE" if err else "SUCCESS",
            error_message=err
        )

    def execute_system_B(self, question_en: str, question_id: str, subject: str = "general", category: str = "general", subject_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        System B: Monolingual English RAG (Upper-bound baseline).
        """
        start_total = time.perf_counter()
        self.tracer.start_trace(question_id, "B", question_en, {"subject": subject, "category": category})

        # 1. Span: English Retrieval
        span_ret = self.tracer.start_span("english_retrieval", "retriever", {"query": question_en, "top_k": self.eng_retriever.top_k})
        chunks, scores, ret_lat = self.eng_retriever.retrieve(question_en, subject_filter=subject_filter)
        context = self.eng_retriever.format_context(chunks)
        self.tracer.end_span(span_ret, {"retrieved_chunks": [c.chunk_id for c in chunks], "scores": scores})

        # 2. Span: English Prompt Formulation & Generation
        prompt = self.prompts["english"].format(question=question_en, context=context)
        span_gen = self.tracer.start_span("llm_generation", "llm", {"prompt": prompt, "model": self.generator.model_name})
        ans, gen_lat, err, tokens = self.generator.generate(prompt)
        self.tracer.end_span(span_gen, {"answer": ans, "tokens": tokens}, error=err)

        total_lat = (time.perf_counter() - start_total) * 1000.0
        self.tracer.end_trace(ans, error=err)

        latencies = {
            "translation_latency_ms": 0.0,
            "retrieval_latency_ms": ret_lat,
            "generation_latency_ms": gen_lat,
            "total_latency_ms": total_lat
        }

        return self.logger.log_run(
            question_id=question_id,
            system_id="B",
            subject=subject,
            category=category,
            original_question=question_en,
            retrieved_chunks=chunks,
            retrieval_scores=scores,
            generated_answer=ans,
            latencies=latencies,
            model_name=self.generator.model_name,
            embedding_model=self.eng_model_name,
            top_k=self.eng_retriever.top_k,
            temperature=self.generator.temperature,
            error_status="FAILURE" if err else "SUCCESS",
            error_message=err
        )

    def execute_system_C(self, question_hi: str, question_id: str, subject: str = "general", category: str = "general", subject_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        System C: Translation-Mediated RAG.
        Hindi Query -> Translate to English -> English Retrieval -> Hindi Generation.
        """
        start_total = time.perf_counter()
        self.tracer.start_trace(question_id, "C", question_hi, {"subject": subject, "category": category})

        # 1. Span: Machine Translation (Hi -> En)
        span_trans = self.tracer.start_span("machine_translation", "tool", {"source_query": question_hi, "from": "hi", "to": "en"})
        translated_en, trans_lat, trans_err = self.translator.translate_hi_to_en(question_hi)
        self.tracer.end_span(span_trans, {"translated_query": translated_en}, error=trans_err)

        # 2. Span: English Retrieval using Translated Query
        span_ret = self.tracer.start_span("english_retrieval", "retriever", {"query": translated_en, "top_k": self.eng_retriever.top_k})
        chunks, scores, ret_lat = self.eng_retriever.retrieve(translated_en, subject_filter=subject_filter)
        context = self.eng_retriever.format_context(chunks)
        self.tracer.end_span(span_ret, {"retrieved_chunks": [c.chunk_id for c in chunks], "scores": scores})

        # 3. Span: Formulate Prompt and Generate Hindi Output
        prompt = self.prompts["hindi"].format(question=question_hi, context=context)
        span_gen = self.tracer.start_span("llm_generation", "llm", {"prompt": prompt, "model": self.generator.model_name})
        ans, gen_lat, gen_err, tokens = self.generator.generate(prompt)
        self.tracer.end_span(span_gen, {"answer": ans, "tokens": tokens}, error=gen_err)

        total_lat = (time.perf_counter() - start_total) * 1000.0
        err = trans_err or gen_err
        self.tracer.end_trace(ans, error=err)

        latencies = {
            "translation_latency_ms": trans_lat,
            "retrieval_latency_ms": ret_lat,
            "generation_latency_ms": gen_lat,
            "total_latency_ms": total_lat
        }

        return self.logger.log_run(
            question_id=question_id,
            system_id="C",
            subject=subject,
            category=category,
            original_question=question_hi,
            translated_question=translated_en,
            retrieved_chunks=chunks,
            retrieval_scores=scores,
            generated_answer=ans,
            latencies=latencies,
            model_name=self.generator.model_name,
            embedding_model=self.eng_model_name,
            translation_model=self.translator.provider,
            top_k=self.eng_retriever.top_k,
            temperature=self.generator.temperature,
            error_status="FAILURE" if err else "SUCCESS",
            error_message=err
        )

    def execute_system_D(self, question_hi: str, question_id: str, subject: str = "general", category: str = "general", subject_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        System D: Direct Multilingual RAG.
        Hindi Query directly encoded by Multilingual Embedder -> Multi FAISS Index -> Hindi Generation.
        """
        start_total = time.perf_counter()
        self.tracer.start_trace(question_id, "D", question_hi, {"subject": subject, "category": category})

        # 1. Span: Direct Zero-Shot Cross-Lingual Search (No Translation)
        span_ret = self.tracer.start_span("multilingual_cross_lingual_retrieval", "retriever", {
            "query": question_hi,
            "model": self.multi_model_name,
            "top_k": self.multi_retriever.top_k
        })
        chunks, scores, ret_lat = self.multi_retriever.retrieve(question_hi, subject_filter=subject_filter)
        context = self.multi_retriever.format_context(chunks)
        self.tracer.end_span(span_ret, {"retrieved_chunks": [c.chunk_id for c in chunks], "scores": scores})

        # 2. Span: Formulate Prompt and Generate Hindi Output
        prompt = self.prompts["hindi"].format(question=question_hi, context=context)
        span_gen = self.tracer.start_span("llm_generation", "llm", {"prompt": prompt, "model": self.generator.model_name})
        ans, gen_lat, gen_err, tokens = self.generator.generate(prompt)
        self.tracer.end_span(span_gen, {"answer": ans, "tokens": tokens}, error=gen_err)

        total_lat = (time.perf_counter() - start_total) * 1000.0
        self.tracer.end_trace(ans, error=gen_err)

        latencies = {
            "translation_latency_ms": 0.0,
            "retrieval_latency_ms": ret_lat,
            "generation_latency_ms": gen_lat,
            "total_latency_ms": total_lat
        }

        return self.logger.log_run(
            question_id=question_id,
            system_id="D",
            subject=subject,
            category=category,
            original_question=question_hi,
            retrieved_chunks=chunks,
            retrieval_scores=scores,
            generated_answer=ans,
            latencies=latencies,
            model_name=self.generator.model_name,
            embedding_model=self.multi_model_name,
            translation_model="none",
            top_k=self.multi_retriever.top_k,
            temperature=self.generator.temperature,
            error_status="FAILURE" if gen_err else "SUCCESS",
            error_message=gen_err
        )

    def run_benchmark(self, max_questions: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Executes all enabled pipelines (A, B, C, D) over the benchmark CSV dataset.
        """
        csv_path = Path(self.config["paths"]["benchmark_file"])
        if not csv_path.exists():
            print(f"[Error] Benchmark dataset not found at: {csv_path}")
            return []

        df = pd.read_csv(csv_path)
        if max_questions:
            df = df.head(max_questions)

        print(f"[Benchmark] Starting execution across {len(df)} questions...")
        all_results = []

        sys_cfg = self.config.get("systems", {})
        run_a = sys_cfg.get("A_direct_llm", True)
        run_b = sys_cfg.get("B_english_rag", True)
        run_c = sys_cfg.get("C_translation_rag", True)
        run_d = sys_cfg.get("D_multilingual_rag", True)

        for idx, row in df.iterrows():
            q_id = str(row["question_id"])
            subj = str(row.get("subject", "CS"))
            cat = str(row.get("category", "Factual"))
            q_en = str(row["question_en"])
            q_hi = str(row["question_hi"])

            print(f"[{idx+1}/{len(df)}] Processing Q: {q_id} ({subj})...")

            if run_a:
                res_a = self.execute_system_A(q_hi, q_id, subj, cat)
                all_results.append(res_a)

            if run_b:
                res_b = self.execute_system_B(q_en, q_id, subj, cat)
                all_results.append(res_b)

            if run_c:
                res_c = self.execute_system_C(q_hi, q_id, subj, cat)
                all_results.append(res_c)

            if run_d:
                res_d = self.execute_system_D(q_hi, q_id, subj, cat)
                all_results.append(res_d)

        print(f"[Benchmark Complete] Executed {len(all_results)} pipeline runs.")
        return all_results

if __name__ == "__main__":
    cfg = load_config()
    orchestrator = PipelineOrchestrator(cfg)
    orchestrator.run_benchmark(max_questions=3)
