"""
Pipeline Orchestration Engine for Systems A, B, C, and D.
Executes query workflows, monitors latencies across stages, enforces experimental controls,
logs atomic JSON audit records, and integrates deep OpenTelemetry/LangSmith observability spans.
Conforms strictly to the English-Hindi Cross-Lingual Academic RAG Experimentation Platform specification.
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

try:
    from .utils import load_config, get_project_root
    from .embeddings import get_embedder
    from .vector_store import FAISSVectorStore
    from .retrieval import Retriever
    from .translation import TranslationService
    from .generation import LLMGenerator
    from .logging_utils import ExperimentLogger
    from .observability import ObservabilityTracer
except (ImportError, ValueError):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.utils import load_config, get_project_root
    from src.embeddings import get_embedder
    from src.vector_store import FAISSVectorStore
    from src.retrieval import Retriever
    from src.translation import TranslationService
    from src.generation import LLMGenerator
    from src.logging_utils import ExperimentLogger
    from src.observability import ObservabilityTracer


class PipelineOrchestrator:
    """
    Coordinates end-to-end execution of Systems A, B, C, and D with deep observability.
    """
    def __init__(self, config: Dict[str, Any], workspace_id: str = "reference"):
        self.config = config
        self.root = get_project_root()
        self.workspace_id = workspace_id or "reference"

        # Initialize Logger (isolated raw results per workspace)
        if self.workspace_id == "reference":
            raw_results_dir = config["paths"].get("results_raw_dir", "results/benchmark/raw")
        else:
            raw_results_dir = f"results/custom/{self.workspace_id}/raw"
        self.logger = ExperimentLogger(raw_results_dir)

        # Initialize Observability Tracer
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

        # Initialize Vector Stores (isolated reference vs custom workspace)
        self.eng_store = FAISSVectorStore(f"english_index_{self.workspace_id}")
        if self.workspace_id == "reference":
            eng_idx_dir = Path(config["paths"].get("english_index_dir", "indexes/reference/english"))
        else:
            eng_idx_dir = Path(f"indexes/custom/{self.workspace_id}/english")
        self.eng_store_loaded = self.eng_store.load(self.root / eng_idx_dir)

        self.multi_store = FAISSVectorStore(f"multilingual_index_{self.workspace_id}")
        if self.workspace_id == "reference":
            multi_idx_dir = Path(config["paths"].get("multilingual_index_dir", "indexes/reference/multilingual"))
        else:
            multi_idx_dir = Path(f"indexes/custom/{self.workspace_id}/multilingual")
        self.multi_store_loaded = self.multi_store.load(self.root / multi_idx_dir)

        # Initialize Retrievers
        top_k = config.get("retrieval", {}).get("top_k", 5)
        self.eng_retriever = Retriever(self.eng_store, self.eng_embedder, top_k=top_k)
        self.multi_retriever = Retriever(self.multi_store, self.multi_embedder, top_k=top_k)

        # Load Prompt Templates
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, str]:
        p_dir = self.root / Path(self.config["paths"].get("prompts_dir", "prompts"))
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

    def execute_system_A(self, question: str, question_id: str,
                           subject: str = "general", category: str = "general",
                           run_type: str = "benchmark",
                           strict_benchmark: bool = False) -> Dict[str, Any]:
        """
        System A: Direct LLM Baseline (No retrieval).
        Zero external document context; answers purely from parametric memory.
        """
        start_total = time.perf_counter()
        self.tracer.start_trace(question_id, "A", question, {"subject": subject, "category": category})

        prompt = self.prompts["direct"].format(question=question)

        span_gen = self.tracer.start_span("llm_generation", "llm", {"prompt": prompt, "model": self.generator.model_name})
        ans, gen_lat, err, tokens, audit = self.generator.generate(
            prompt, strict_benchmark=strict_benchmark, allow_fallback=(not strict_benchmark)
        )
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
            model_name=audit.get("actual_model", self.generator.model_name),
            embedding_model="none",
            top_k=0,
            temperature=self.generator.temperature,
            run_type=run_type,
            requested_provider=audit.get("requested_provider"),
            actual_provider=audit.get("actual_provider"),
            fallback_used=audit.get("fallback_used", False),
            fallback_reason=audit.get("fallback_reason"),
            error_status="FAILURE" if err else "SUCCESS",
            error_message=err
        )

    def execute_system_B(self, question_en: str, question_id: str,
                           subject: str = "general", category: str = "general",
                           subject_filter: Optional[str] = None,
                           run_type: str = "benchmark",
                           strict_benchmark: bool = False) -> Dict[str, Any]:
        """
        System B: Monolingual English RAG (Upper-bound baseline).
        English question -> English embedding -> FAISS English index -> English answer.
        """
        start_total = time.perf_counter()
        self.tracer.start_trace(question_id, "B", question_en, {"subject": subject, "category": category})

        # 1. English Retrieval
        span_ret = self.tracer.start_span("english_retrieval", "retriever", {"query": question_en, "top_k": self.eng_retriever.top_k})
        chunks, scores, ret_lat = self.eng_retriever.retrieve(question_en, subject_filter=subject_filter)
        context = self.eng_retriever.format_context(chunks)
        self.tracer.end_span(span_ret, {"retrieved_chunks": [c.chunk_id for c in chunks], "scores": scores})

        # 2. English Generation
        prompt = self.prompts["english"].format(question=question_en, context=context)
        span_gen = self.tracer.start_span("llm_generation", "llm", {"prompt": prompt, "model": self.generator.model_name})
        ans, gen_lat, err, tokens, audit = self.generator.generate(
            prompt, strict_benchmark=strict_benchmark, allow_fallback=(not strict_benchmark)
        )
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
            model_name=audit.get("actual_model", self.generator.model_name),
            embedding_model=self.eng_model_name,
            top_k=self.eng_retriever.top_k,
            temperature=self.generator.temperature,
            run_type=run_type,
            requested_provider=audit.get("requested_provider"),
            actual_provider=audit.get("actual_provider"),
            fallback_used=audit.get("fallback_used", False),
            fallback_reason=audit.get("fallback_reason"),
            error_status="FAILURE" if err else "SUCCESS",
            error_message=err
        )

    def execute_system_C(self, question_hi: str, question_id: str,
                           subject: str = "general", category: str = "general",
                           subject_filter: Optional[str] = None,
                           run_type: str = "benchmark",
                           strict_benchmark: bool = False) -> Dict[str, Any]:
        """
        System C: Translation-Mediated RAG.
        Hindi Query -> Translate to English -> English Retrieval (same as B) ->
        Intermediate English Generation -> Translate to Final Hindi Answer.
        """
        start_total = time.perf_counter()
        self.tracer.start_trace(question_id, "C", question_hi, {"subject": subject, "category": category})

        # 1. Step 1: Query Translation (Hi -> En)
        span_trans1 = self.tracer.start_span("query_translation", "tool", {"source_query": question_hi, "from": "hi", "to": "en"})
        translated_en, trans1_lat, trans1_err = self.translator.translate_hi_to_en(question_hi)
        self.tracer.end_span(span_trans1, {"translated_query": translated_en}, error=trans1_err)

        if trans1_err or not translated_en:
            # Translation failed; strict research protocol marks failure
            total_lat = (time.perf_counter() - start_total) * 1000.0
            latencies = {
                "translation_latency_ms": trans1_lat,
                "retrieval_latency_ms": 0.0,
                "generation_latency_ms": 0.0,
                "total_latency_ms": total_lat
            }
            return self.logger.log_run(
                question_id=question_id,
                system_id="C",
                subject=subject,
                category=category,
                original_question=question_hi,
                translated_question=translated_en or "[TRANSLATION_FAILED]",
                generated_answer="",
                latencies=latencies,
                model_name=self.generator.model_name,
                embedding_model=self.eng_model_name,
                translation_model=self.translator.provider,
                run_type=run_type,
                error_status="FAILURE",
                error_message=f"Translation failure (Hi->En): {trans1_err}"
            )

        # 2. Step 2: English Retrieval using Translated Query (same index as B)
        span_ret = self.tracer.start_span("english_retrieval", "retriever", {"query": translated_en, "top_k": self.eng_retriever.top_k})
        chunks, scores, ret_lat = self.eng_retriever.retrieve(translated_en, subject_filter=subject_filter)
        context = self.eng_retriever.format_context(chunks)
        self.tracer.end_span(span_ret, {"retrieved_chunks": [c.chunk_id for c in chunks], "scores": scores})

        # 3. Step 3: Intermediate English Answer Generation
        prompt_en = self.prompts["english"].format(question=translated_en, context=context)
        span_gen = self.tracer.start_span("intermediate_generation", "llm", {"prompt": prompt_en, "model": self.generator.model_name})
        intermediate_ans, gen_lat, gen_err, tokens, audit = self.generator.generate(
            prompt_en, strict_benchmark=strict_benchmark, allow_fallback=(not strict_benchmark)
        )
        self.tracer.end_span(span_gen, {"intermediate_answer": intermediate_ans, "tokens": tokens}, error=gen_err)

        # 4. Step 4: Final Hindi Answer Generation / Translation (En -> Hi)
        trans2_lat = 0.0
        final_ans = ""
        trans2_err = None

        if intermediate_ans and not gen_err:
            span_trans2 = self.tracer.start_span("answer_translation", "tool", {"text": intermediate_ans, "from": "en", "to": "hi"})
            final_ans, trans2_lat, trans2_err = self.translator.translate_en_to_hi(intermediate_ans)
            self.tracer.end_span(span_trans2, {"hindi_answer": final_ans}, error=trans2_err)

            if not final_ans or trans2_err:
                # If direct MT on answer failed, use prompt-based hindi generation
                prompt_hi = self.prompts["hindi"].format(question=question_hi, context=context)
                final_ans, fallback_gen_lat, gen_err2, _, _ = self.generator.generate(
                    prompt_hi, strict_benchmark=strict_benchmark, allow_fallback=(not strict_benchmark)
                )
                gen_lat += fallback_gen_lat

        # 5. Language validation
        is_hindi, lang_reason = self.translator.validate_hindi_output(final_ans)
        combined_err = trans1_err or gen_err or trans2_err
        if not is_hindi and not combined_err:
            combined_err = f"Language check warning: {lang_reason}"

        total_trans_lat = trans1_lat + trans2_lat
        total_lat = (time.perf_counter() - start_total) * 1000.0
        self.tracer.end_trace(final_ans, error=combined_err)

        latencies = {
            "translation_latency_ms": total_trans_lat,
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
            intermediate_answer_en=intermediate_ans,
            generated_answer=final_ans,
            latencies=latencies,
            model_name=audit.get("actual_model", self.generator.model_name),
            embedding_model=self.eng_model_name,
            translation_model=self.translator.provider,
            top_k=self.eng_retriever.top_k,
            temperature=self.generator.temperature,
            run_type=run_type,
            requested_provider=audit.get("requested_provider"),
            actual_provider=audit.get("actual_provider"),
            fallback_used=audit.get("fallback_used", False),
            fallback_reason=audit.get("fallback_reason"),
            error_status="FAILURE" if (combined_err and not final_ans) else "SUCCESS",
            error_message=combined_err
        )

    def execute_system_D(self, question_hi: str, question_id: str,
                           subject: str = "general", category: str = "general",
                           subject_filter: Optional[str] = None,
                           run_type: str = "benchmark",
                           strict_benchmark: bool = False) -> Dict[str, Any]:
        """
        System D: Direct Multilingual RAG.
        Hindi Query directly encoded by Multilingual Embedder -> Multi FAISS Index ->
        Generates Hindi output directly. NO PRE-RETRIEVAL TRANSLATION!
        """
        start_total = time.perf_counter()
        self.tracer.start_trace(question_id, "D", question_hi, {"subject": subject, "category": category})

        # 1. Zero-shot cross-lingual retrieval (Hindi query directly into multilingual encoder)
        span_ret = self.tracer.start_span("multilingual_cross_lingual_retrieval", "retriever", {
            "query": question_hi,
            "model": self.multi_model_name,
            "top_k": self.multi_retriever.top_k
        })
        chunks, scores, ret_lat = self.multi_retriever.retrieve(question_hi, subject_filter=subject_filter)
        context = self.multi_retriever.format_context(chunks)
        self.tracer.end_span(span_ret, {"retrieved_chunks": [c.chunk_id for c in chunks], "scores": scores})

        # 2. Direct Hindi answer generation from English context
        prompt = self.prompts["hindi"].format(question=question_hi, context=context)
        span_gen = self.tracer.start_span("llm_generation", "llm", {"prompt": prompt, "model": self.generator.model_name})
        ans, gen_lat, gen_err, tokens, audit = self.generator.generate(
            prompt, strict_benchmark=strict_benchmark, allow_fallback=(not strict_benchmark)
        )
        self.tracer.end_span(span_gen, {"answer": ans, "tokens": tokens}, error=gen_err)

        # 3. Language validation
        is_hindi, lang_reason = self.translator.validate_hindi_output(ans)
        combined_err = gen_err
        if not is_hindi and not combined_err and ans:
            combined_err = f"Language check warning: {lang_reason}"

        total_lat = (time.perf_counter() - start_total) * 1000.0
        self.tracer.end_trace(ans, error=combined_err)

        latencies = {
            "translation_latency_ms": 0.0,  # Zero translation for System D
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
            model_name=audit.get("actual_model", self.generator.model_name),
            embedding_model=self.multi_model_name,
            translation_model="none",
            top_k=self.multi_retriever.top_k,
            temperature=self.generator.temperature,
            run_type=run_type,
            requested_provider=audit.get("requested_provider"),
            actual_provider=audit.get("actual_provider"),
            fallback_used=audit.get("fallback_used", False),
            fallback_reason=audit.get("fallback_reason"),
            error_status="FAILURE" if (combined_err and not ans) else "SUCCESS",
            error_message=combined_err
        )

    def run_benchmark(self, max_questions: Optional[int] = None, run_type: str = "benchmark",
                      strict_benchmark: bool = False) -> List[Dict[str, Any]]:
        """
        Executes all enabled pipelines (A, B, C, D) over the benchmark CSV dataset.
        """
        csv_path = self.root / Path(self.config["paths"].get("benchmark_file", "data/benchmark/questions.csv"))
        if not csv_path.exists():
            print(f"[Error] Benchmark dataset not found at: {csv_path}")
            return []

        df = pd.read_csv(csv_path)
        if max_questions:
            df = df.head(max_questions)

        print(f"[Benchmark] Starting execution across {len(df)} questions (Run Type: {run_type}, Strict: {strict_benchmark})...")
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
                res_a = self.execute_system_A(q_hi, q_id, subj, cat, run_type=run_type, strict_benchmark=strict_benchmark)
                all_results.append(res_a)

            if run_b:
                res_b = self.execute_system_B(q_en, q_id, subj, cat, run_type=run_type, strict_benchmark=strict_benchmark)
                all_results.append(res_b)

            if run_c:
                res_c = self.execute_system_C(q_hi, q_id, subj, cat, run_type=run_type, strict_benchmark=strict_benchmark)
                all_results.append(res_c)

            if run_d:
                res_d = self.execute_system_D(q_hi, q_id, subj, cat, run_type=run_type, strict_benchmark=strict_benchmark)
                all_results.append(res_d)

        print(f"[Benchmark Complete] Executed {len(all_results)} pipeline runs.")
        return all_results


if __name__ == "__main__":
    cfg = load_config()
    orchestrator = PipelineOrchestrator(cfg)
    orchestrator.run_benchmark(max_questions=1, run_type="smoke", strict_benchmark=False)
