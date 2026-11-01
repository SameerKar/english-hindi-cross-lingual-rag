"""
Master End-to-End Test & Observation Recording Script (`run_complete_experiment.py`).
Executes the complete cross-lingual benchmark workflow:
1. Runs pytest cross_lingual_rag/tests/test_basic_pipeline.py -v and asserts all 7/7 tests pass.
2. Cleans all old/stale SMOKE_01 JSON logs from results/raw/ and results/traces/.
3. Verifies data/processed/chunks_manifest.json (15 chunks across 5 subjects) and both FAISS indexes (data/indexes/english/index.faiss and data/indexes/multilingual/index.faiss).
4. Runs all 17 benchmark questions x 4 systems = 68 pipeline executions (A, B, C, D).
5. Runs EvaluationHarness.run_evaluation(exclude_smoke=True) to generate:
   - cross_lingual_rag/results/csv/benchmark_results.csv (all 68 rows)
   - cross_lingual_rag/results/summaries/evaluation_report.md
   - cross_lingual_rag/results/summaries/complete_project_observations.json

Usage:
    python cross_lingual_rag/run_complete_experiment.py
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

# Fix Windows console UTF-8 output encoding for symbols and Hindi characters
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add cross_lingual_rag and project root to sys.path
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from src.utils import load_config, set_seed, ensure_directory, get_project_root
from src.ingestion import CorpusIngestor
from src.vector_store import build_dual_indexes
from src.pipelines import PipelineOrchestrator
from src.evaluation import EvaluationHarness


def run_pytest_suite() -> dict:
    """Runs the 7-point automated pytest suite and asserts all 7 tests pass."""
    print("\n" + "=" * 80)
    print("[Step 1] Running 7-Point Pytest Verification Suite...")
    print("=" * 80)
    test_file = script_dir / "tests" / "test_basic_pipeline.py"
    start_t = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    elapsed = round((time.perf_counter() - start_t), 2)
    passed = (proc.returncode == 0)
    print(proc.stdout)
    if not passed:
        print(proc.stderr)
        raise RuntimeError(f"Pytest verification failed! (Exit code: {proc.returncode})")

    summary_line = proc.stdout.strip().splitlines()[-1] if proc.stdout else ""
    print(f"[OK] Pytest Verification Succeeded: {summary_line} ({elapsed}s)")
    return {
        "passed": passed,
        "return_code": proc.returncode,
        "duration_sec": elapsed,
        "stdout_summary": summary_line
    }


def clean_stale_logs_and_traces(raw_dir: Path, traces_dir: Path):
    """Cleans all previous JSON logs and traces so only the clean 68 benchmark runs remain."""
    print("\n" + "=" * 80)
    print("[Step 2] Cleaning Old / Stale JSON Logs & Traces...")
    print("=" * 80)

    raw_count = 0
    if raw_dir.exists():
        for f in raw_dir.rglob("*.json"):
            try:
                f.unlink()
                raw_count += 1
            except Exception as e:
                print(f"[Warning] Could not delete {f}: {e}")
    print(f"  -> Cleaned {raw_count} old raw JSON logs from {raw_dir}")

    traces_count = 0
    if traces_dir.exists():
        for f in traces_dir.rglob("*.json"):
            try:
                f.unlink()
                traces_count += 1
            except Exception as e:
                print(f"[Warning] Could not delete {f}: {e}")
    print(f"  -> Cleaned {traces_count} old trace files from {traces_dir}")


def verify_corpus_and_indexes(config: dict):
    """Verifies that chunks_manifest.json has 15 chunks across 5 subjects and both FAISS indexes exist."""
    print("\n" + "=" * 80)
    print("[Step 3] Verifying Corpus Manifest & Dual FAISS Vector Stores...")
    print("=" * 80)

    processed_dir = Path(config["paths"]["processed_dir"])
    manifest_file = processed_dir / "chunks_manifest.json"
    eng_dir = Path(config["paths"]["english_index_dir"])
    multi_dir = Path(config["paths"]["multilingual_index_dir"])

    eng_idx = eng_dir / "index.faiss"
    eng_map = eng_dir / "metadata_map.pkl"
    multi_idx = multi_dir / "index.faiss"
    multi_map = multi_dir / "metadata_map.pkl"

    rebuild_corpus = False
    if not manifest_file.exists():
        rebuild_corpus = True
    else:
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            subjects = set(c.get("subject") for c in manifest_data)
            if len(manifest_data) < 15 or len(subjects) < 5:
                print(f"  -> Manifest incomplete ({len(manifest_data)} chunks, {len(subjects)} subjects). Rebuilding...")
                rebuild_corpus = True
            else:
                print(f"  -> Verified chunks_manifest.json: {len(manifest_data)} chunks across {len(subjects)} subjects.")
        except Exception:
            rebuild_corpus = True

    if rebuild_corpus:
        print("  -> Ingesting academic corpus from data/corpus/...")
        ingestor = CorpusIngestor(config)
        ingestor.ingest_corpus()

    rebuild_indexes = False
    if not (eng_idx.exists() and eng_map.exists() and multi_idx.exists() and multi_map.exists()):
        rebuild_indexes = True

    if rebuild_indexes:
        print("  -> Building Dual FAISS vector stores (English 768d + Multilingual 384d)...")
        build_dual_indexes(config)
    else:
        print("  -> Verified existing English & Multilingual FAISS vector stores.")


def main():
    print("=" * 80)
    print("[RESEARCH BENCHMARK] ENGLISH-HINDI CROSS-LINGUAL ACADEMIC RAG: COMPLETE 68-RUN SUITE")
    print("=" * 80)

    config = load_config()
    set_seed(config.get("random_seed", 42))

    # 1. Run 7-Point Pytest Suite
    pytest_status = run_pytest_suite()

    # 2. Clean stale logs and traces
    raw_dir = Path(config["paths"]["results_raw_dir"])
    traces_dir = Path(get_project_root()) / "results" / "traces"
    clean_stale_logs_and_traces(raw_dir, traces_dir)

    # 3. Verify Corpus Manifest & FAISS Vector Stores
    verify_corpus_and_indexes(config)

    # 4. Initialize Orchestrator and Execute All 17 Questions x 4 Systems = 68 Runs
    print("\n" + "=" * 80)
    print("[Step 4] Initializing Pipeline Orchestrator & Executing 68 Benchmark Runs...")
    print("=" * 80)
    orchestrator = PipelineOrchestrator(config)

    bench_csv = Path(config["paths"]["benchmark_file"])
    df_bench = pd.read_csv(bench_csv)
    total_q = len(df_bench)
    print(f"Loaded {total_q} paired benchmark questions from {bench_csv}")

    run_start_t = time.perf_counter()
    all_runs = []

    for idx, row in df_bench.iterrows():
        q_id = str(row["question_id"])
        subj = str(row["subject"])
        cat = str(row["category"])
        q_en = str(row["question_en"])
        q_hi = str(row["question_hi"])

        print(f"  -> [{idx+1:02d}/{total_q:02d}] {q_id} | Subject: {subj:<18} | Category: {cat}")

        # System A: Direct LLM Baseline
        res_a = orchestrator.execute_system_A(q_hi, q_id, subj, cat)
        all_runs.append(res_a)

        # System B: Monolingual English RAG
        res_b = orchestrator.execute_system_B(q_en, q_id, subj, cat)
        all_runs.append(res_b)

        # System C: Translation-Mediated RAG
        res_c = orchestrator.execute_system_C(q_hi, q_id, subj, cat)
        all_runs.append(res_c)

        # System D: Direct Multilingual RAG
        res_d = orchestrator.execute_system_D(q_hi, q_id, subj, cat)
        all_runs.append(res_d)

    total_bench_duration = round(time.perf_counter() - run_start_t, 2)
    print(f"\n[OK] All 68 benchmark pipeline executions completed in {total_bench_duration}s.")

    # 5. Run Evaluation Harness & Generate Reports
    print("\n" + "=" * 80)
    print("[Step 5] Running Scientific Evaluation Harness & Generating Reports...")
    print("=" * 80)
    evaluator = EvaluationHarness(config)
    df_eval, report_md = evaluator.run_evaluation(exclude_smoke=True)

    # 6. Save Complete Structured Observations JSON
    summary_dir = Path(config["paths"]["results_summary_dir"])
    obs_path = summary_dir / "complete_project_observations.json"

    sys_summary = {}
    for s_id in ["A", "B", "C", "D"]:
        sdf = df_eval[df_eval["system_id"] == s_id]
        if not sdf.empty:
            sys_summary[s_id] = {
                "num_questions": int(len(sdf)),
                "recall_at_1": round(float(sdf["recall@1"].mean()), 4) if s_id != "A" else None,
                "recall_at_3": round(float(sdf["recall@3"].mean()), 4) if s_id != "A" else None,
                "recall_at_5": round(float(sdf["recall@5"].mean()), 4) if s_id != "A" else None,
                "mrr": round(float(sdf["mrr"].mean()), 4) if s_id != "A" else None,
                "ndcg_at_5": round(float(sdf["ndcg@5"].mean()), 4) if s_id != "A" else None,
                "mean_translation_latency_ms": round(float(sdf["translation_latency_ms"].mean()), 2),
                "mean_retrieval_latency_ms": round(float(sdf["retrieval_latency_ms"].mean()), 2),
                "mean_generation_latency_ms": round(float(sdf["generation_latency_ms"].mean()), 2),
                "mean_total_latency_ms": round(float(sdf["total_latency_ms"].mean()), 2),
                "error_counts": {
                    "E1_translation_drift": int((sdf["error_classification"] == "E1 - Translation Drift").sum()),
                    "E2_retrieval_failure": int((sdf["error_classification"] == "E2 - Retrieval Failure").sum()),
                    "E3_generation_failure": int((sdf["error_classification"] == "E3 - Generation Failure").sum()),
                    "E4_language_failure": int((sdf["error_classification"] == "E4 - Language Failure").sum()),
                    "clean_success": int((sdf["error_classification"] == "NONE").sum())
                }
            }

    subj_mrr = {}
    for subj in sorted(df_eval["subject"].dropna().unique()):
        subj_df = df_eval[df_eval["subject"] == subj]
        subj_mrr[subj] = {
            "B": round(float(subj_df[subj_df["system_id"] == "B"]["mrr"].mean()), 4),
            "C": round(float(subj_df[subj_df["system_id"] == "C"]["mrr"].mean()), 4),
            "D": round(float(subj_df[subj_df["system_id"] == "D"]["mrr"].mean()), 4),
        }

    observations_payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "pytest_verification": pytest_status,
        "total_benchmark_questions": total_q,
        "total_pipeline_runs": int(len(df_eval)),
        "system_metrics_summary": sys_summary,
        "subject_wise_mrr": subj_mrr
    }
    with open(obs_path, "w", encoding="utf-8") as f:
        json.dump(observations_payload, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("[OK] EXPERIMENT & OBSERVATION RECORDING FULLY COMPLETE!")
    print("=" * 80)
    print(f"1. Consolidated CSV Table : {config['paths']['results_csv_dir']}/benchmark_results.csv")
    print(f"2. Markdown Evaluation    : {config['paths']['results_summary_dir']}/evaluation_report.md")
    print(f"3. JSON Observations Log  : {obs_path}")
    print("\nFinal Summary Preview:\n")
    print(report_md)


if __name__ == "__main__":
    main()
