"""
Scientific Evaluation Harness for Cross-Lingual Academic RAG.
Computes Recall@1/3/5, MRR, nDCG@5, latency distributions, and classifies runs under the E1-E4 Error Taxonomy.
Outputs consolidated CSV and Markdown research reports.
"""

import os
import sys
import json
import glob
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from .utils import load_config, ensure_directory, get_project_root


class EvaluationHarness:
    """
    Evaluates raw JSON experiment logs against the benchmark ground truth dataset.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.benchmark_path = Path(config["paths"]["benchmark_file"])
        self.raw_dir = Path(config["paths"]["results_raw_dir"])
        self.csv_dir = Path(config["paths"]["results_csv_dir"])
        self.summary_dir = Path(config["paths"]["results_summary_dir"])

        ensure_directory(str(self.csv_dir))
        ensure_directory(str(self.summary_dir))

        self.benchmark_df = self._load_benchmark()

    def _load_benchmark(self) -> pd.DataFrame:
        if not self.benchmark_path.exists():
            print(f"[Warning] Benchmark CSV does not exist: {self.benchmark_path}")
            return pd.DataFrame()
        return pd.read_csv(self.benchmark_path)

    def load_all_logs(self, exclude_smoke: bool = True, deduplicate_latest: bool = True) -> List[Dict[str, Any]]:
        """
        Gathers all individual JSON run records across all systems.
        - exclude_smoke: Ignores SMOKE_* logs created by pytest unit tests during official benchmark evaluation.
        - deduplicate_latest: Keeps the most recent execution per (question_id, system_id) pair.
        """
        all_logs = []
        log_files = sorted(self.raw_dir.rglob("*.json"), key=os.path.getmtime)
        for log_f in log_files:
            try:
                with open(log_f, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    qid = str(data.get("question_id", ""))
                    if exclude_smoke and qid.startswith("SMOKE_"):
                        continue
                    all_logs.append(data)
            except Exception as e:
                print(f"[Error] Corrupted log file {log_f}: {e}")

        if deduplicate_latest and all_logs:
            dedup_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
            for log in all_logs:
                key = (str(log.get("question_id", "")), str(log.get("system_id", "")))
                dedup_map[key] = log
            return list(dedup_map.values())

        return all_logs

    def compute_mrr(self, gold_chunk: str, retrieved_chunks: List[str]) -> float:
        """
        Calculates Reciprocal Rank (1/rank) if gold_chunk is in retrieved_chunks; 0.0 otherwise.
        """
        if not gold_chunk or not gold_chunk.strip() or not retrieved_chunks:
            return 0.0
        gold_clean = gold_chunk.strip()
        for i, chunk_id in enumerate(retrieved_chunks):
            if gold_clean == chunk_id or chunk_id.startswith(gold_clean):
                return 1.0 / (i + 1)
        return 0.0

    def compute_recall_at_k(self, gold_chunk: str, retrieved_chunks: List[str], k: int) -> float:
        """
        Checks if gold_chunk is present within top-k chunks.
        """
        if not gold_chunk or not gold_chunk.strip() or not retrieved_chunks:
            return 0.0
        gold_clean = gold_chunk.strip()
        sub_list = retrieved_chunks[:k]
        for chunk_id in sub_list:
            if gold_clean == chunk_id or chunk_id.startswith(gold_clean):
                return 1.0
        return 0.0

    def compute_ndcg_at_k(self, gold_chunk: str, retrieved_chunks: List[str], k: int = 5) -> float:
        """
        Computes binary nDCG at rank k, bounded strictly in [0.0, 1.0].
        Only counts the first matching gold chunk to prevent >1.0 scores if duplicate IDs exist.
        """
        if not gold_chunk or not gold_chunk.strip() or not retrieved_chunks:
            return 0.0
        gold_clean = gold_chunk.strip()
        sub_list = retrieved_chunks[:k]
        dcg = 0.0
        for i, chunk_id in enumerate(sub_list):
            rel = 1.0 if (gold_clean == chunk_id or chunk_id.startswith(gold_clean)) else 0.0
            if rel > 0:
                dcg += (math.pow(2.0, rel) - 1.0) / math.log2(i + 2)
                break  # Binary relevance for single target chunk
        idcg = (math.pow(2.0, 1.0) - 1.0) / math.log2(2)
        return round(dcg / idcg, 4) if idcg > 0 else 0.0

    def classify_error(self, record: Dict[str, Any], gold_chunk: str, gold_ans: str) -> Optional[str]:
        """
        Classifies errors into the E1-E4 Scientific Error Taxonomy.
        """
        sys_id = record.get("system_id", "")
        ret_chunks = record.get("retrieved_chunks", [])
        ans = record.get("generated_answer", "")
        trans_q = record.get("translated_question", "")
        err_msg = record.get("error_message") or ""

        # E1 - Translation Drift (System C only)
        if sys_id == "C":
            if not trans_q or "[ERROR" in trans_q or len(trans_q.strip()) < 5:
                return "E1 - Translation Drift"
            # If translation failed completely and left the query identical to Devanagari input
            if trans_q.strip() == record.get("original_question", "").strip():
                return "E1 - Translation Drift"

        # E2 - Retrieval Failure (Systems B, C, D)
        if sys_id in ["B", "C", "D"] and gold_chunk:
            rec5 = self.compute_recall_at_k(gold_chunk, ret_chunks, 5)
            if rec5 == 0.0:
                return "E2 - Retrieval Failure"

        # E3 - Generation Failure
        if "[ERROR" in ans or "insufficient" in ans.lower() or "अपर्याप्त" in ans:
            return "E3 - Generation Failure"

        # E4 - Language / Terminology Failure
        if sys_id in ["C", "D"]:
            if len(ans.strip()) < 10 or ("?" in ans and len(ans) < 20):
                return "E4 - Language Failure"

        if "Translation failed" in err_msg and sys_id == "C":
            return "E1 - Translation Drift"

        return None

    def run_evaluation(self, exclude_smoke: bool = True) -> Tuple[pd.DataFrame, str]:
        """
        Evaluates all logs and generates tabular data and summary report.
        """
        logs = self.load_all_logs(exclude_smoke=exclude_smoke, deduplicate_latest=True)
        if not logs:
            # Fallback to including smoke logs if no benchmark logs exist yet
            logs = self.load_all_logs(exclude_smoke=False, deduplicate_latest=True)

        if not logs:
            print("[Evaluation] No logs found in results/raw/ to evaluate.")
            return pd.DataFrame(), ""

        print(f"[Evaluation] Processing {len(logs)} deduplicated log records...")

        # Build lookup from benchmark CSV
        bench_lookup = {}
        if not self.benchmark_df.empty:
            for _, row in self.benchmark_df.iterrows():
                qid = str(row["question_id"])
                bench_lookup[qid] = {
                    "gold_chunk_id": str(row.get("gold_chunk_id", "")),
                    "gold_document_id": str(row.get("gold_document_id", "")),
                    "gold_answer": str(row.get("gold_answer", ""))
                }

        # Fallback mapping for SMOKE_01 if evaluated
        bench_lookup.setdefault("SMOKE_01", {
            "gold_chunk_id": "operating_systems_operating_systems_p2_c0",
            "gold_document_id": "operating_systems_operating_systems",
            "gold_answer": "Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait."
        })

        evaluated_rows = []
        for log in logs:
            qid = str(log.get("question_id", ""))
            sys_id = str(log.get("system_id", ""))
            gold_info = bench_lookup.get(qid, {})
            gold_chunk = gold_info.get("gold_chunk_id", "")
            gold_ans = gold_info.get("gold_answer", "")

            ret_chunks = log.get("retrieved_chunks", [])
            lat = log.get("latencies", {})

            rec1 = self.compute_recall_at_k(gold_chunk, ret_chunks, 1) if sys_id != "A" else 0.0
            rec3 = self.compute_recall_at_k(gold_chunk, ret_chunks, 3) if sys_id != "A" else 0.0
            rec5 = self.compute_recall_at_k(gold_chunk, ret_chunks, 5) if sys_id != "A" else 0.0
            mrr = self.compute_mrr(gold_chunk, ret_chunks) if sys_id != "A" else 0.0
            ndcg = self.compute_ndcg_at_k(gold_chunk, ret_chunks, 5) if sys_id != "A" else 0.0

            err_tag = self.classify_error(log, gold_chunk, gold_ans)

            row = {
                "run_id": log.get("run_id"),
                "question_id": qid,
                "system_id": sys_id,
                "subject": log.get("subject", ""),
                "category": log.get("category", ""),
                "recall@1": round(rec1, 4),
                "recall@3": round(rec3, 4),
                "recall@5": round(rec5, 4),
                "mrr": round(mrr, 4),
                "ndcg@5": round(ndcg, 4),
                "top_1_chunk": ret_chunks[0] if ret_chunks else "NONE",
                "gold_chunk": gold_chunk,
                "top_1_score": round(float(log.get("retrieval_scores", [0.0])[0]), 4) if log.get("retrieval_scores") else 0.0,
                "translation_latency_ms": lat.get("translation_latency_ms", 0.0),
                "retrieval_latency_ms": lat.get("retrieval_latency_ms", 0.0),
                "generation_latency_ms": lat.get("generation_latency_ms", 0.0),
                "total_latency_ms": lat.get("total_latency_ms", 0.0),
                "error_classification": err_tag or "NONE",
                "error_status": log.get("error_status", "SUCCESS")
            }
            evaluated_rows.append(row)

        df_eval = pd.DataFrame(evaluated_rows).sort_values(by=["question_id", "system_id"])
        csv_out = self.csv_dir / "benchmark_results.csv"
        df_eval.to_csv(csv_out, index=False)
        print(f"[Evaluation] Saved consolidated results to: {csv_out}")

        report_md = self._generate_markdown_report(df_eval)
        report_out = self.summary_dir / "evaluation_report.md"
        with open(report_out, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"[Evaluation] Saved summary report to: {report_out}")

        return df_eval, report_md

    def _generate_markdown_report(self, df: pd.DataFrame) -> str:
        """
        Creates a comprehensive academic markdown report contrasting System C vs System D.
        """
        md = []
        md.append("# Scientific Evaluation Report: English–Hindi Cross-Lingual Academic RAG")
        md.append(f"**Total Benchmark Executions Evaluated:** {len(df)}\n")

        sys_groups = df.groupby("system_id")

        md.append("## 1. System Retrieval & Quality Metrics Comparison")
        md.append("| System ID | Description | Questions | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 | Avg Total Latency (ms) |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

        sys_names = {
            "A": "Direct LLM Baseline (Zero Retrieval)",
            "B": "Monolingual English RAG (Upper Bound)",
            "C": "Translation-Mediated Hindi RAG",
            "D": "Direct Multilingual Hindi RAG"
        }

        for s_id in ["A", "B", "C", "D"]:
            if s_id in sys_groups.groups:
                sdf = sys_groups.get_group(s_id)
                q_cnt = len(sdf)
                r1 = f"{sdf['recall@1'].mean():.3f}" if s_id != "A" else "N/A"
                r3 = f"{sdf['recall@3'].mean():.3f}" if s_id != "A" else "N/A"
                r5 = f"{sdf['recall@5'].mean():.3f}" if s_id != "A" else "N/A"
                mrr = f"{sdf['mrr'].mean():.3f}" if s_id != "A" else "N/A"
                ndcg = f"{sdf['ndcg@5'].mean():.3f}" if s_id != "A" else "N/A"
                lat = f"{sdf['total_latency_ms'].mean():.1f}"
                md.append(f"| **{s_id}** | {sys_names.get(s_id, s_id)} | {q_cnt} | {r1} | {r3} | {r5} | {mrr} | {ndcg} | {lat} |")

        md.append("\n## 2. Latency Breakdown by Component (Mean Milliseconds)")
        md.append("| System ID | Translation Latency (ms) | Retrieval Latency (ms) | Generation Latency (ms) | Total Latency (ms) |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for s_id in ["A", "B", "C", "D"]:
            if s_id in sys_groups.groups:
                sdf = sys_groups.get_group(s_id)
                t_lat = f"{sdf['translation_latency_ms'].mean():.2f}"
                r_lat = f"{sdf['retrieval_latency_ms'].mean():.2f}"
                g_lat = f"{sdf['generation_latency_ms'].mean():.2f}"
                tot_lat = f"{sdf['total_latency_ms'].mean():.2f}"
                md.append(f"| **{s_id}** | {t_lat} | {r_lat} | {g_lat} | {tot_lat} |")

        md.append("\n## 3. Subject-Wise MRR Breakdown (System B vs C vs D)")
        md.append("| Subject | System B (English RAG) | System C (Translation RAG) | System D (Multilingual RAG) |")
        md.append("| :--- | :--- | :--- | :--- |")
        subjects = sorted(df["subject"].dropna().unique())
        for subj in subjects:
            subj_df = df[df["subject"] == subj]
            b_mrr = subj_df[subj_df["system_id"] == "B"]["mrr"].mean()
            c_mrr = subj_df[subj_df["system_id"] == "C"]["mrr"].mean()
            d_mrr = subj_df[subj_df["system_id"] == "D"]["mrr"].mean()
            b_str = f"{b_mrr:.3f}" if not pd.isna(b_mrr) else "N/A"
            c_str = f"{c_mrr:.3f}" if not pd.isna(c_mrr) else "N/A"
            d_str = f"{d_mrr:.3f}" if not pd.isna(d_mrr) else "N/A"
            md.append(f"| **{subj}** | {b_str} | {c_str} | {d_str} |")

        md.append("\n## 4. Error Taxonomy Breakdown (E1 - E4)")
        md.append("| System ID | E1 (Translation Drift) | E2 (Retrieval Failure) | E3 (Generation Failure) | E4 (Language Failure) | Clean Success Rate |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for s_id in ["A", "B", "C", "D"]:
            if s_id in sys_groups.groups:
                sdf = sys_groups.get_group(s_id)
                n = len(sdf)
                e1 = int((sdf["error_classification"] == "E1 - Translation Drift").sum())
                e2 = int((sdf["error_classification"] == "E2 - Retrieval Failure").sum())
                e3 = int((sdf["error_classification"] == "E3 - Generation Failure").sum())
                e4 = int((sdf["error_classification"] == "E4 - Language Failure").sum())
                succ = int((sdf["error_classification"] == "NONE").sum())
                succ_rate = f"{(succ / n) * 100:.1f}%" if n > 0 else "0.0%"
                md.append(f"| **{s_id}** | {e1} | {e2} | {e3} | {e4} | {succ_rate} |")

        return "\n".join(md)


if __name__ == "__main__":
    cfg = load_config()
    evaluator = EvaluationHarness(cfg)
    evaluator.run_evaluation()