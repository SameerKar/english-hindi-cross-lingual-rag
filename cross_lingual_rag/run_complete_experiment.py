"""
Master End-to-End Test & Observation Recording Script (`run_complete_experiment.py`).
Executes the cross-lingual benchmark workflow:
1. Runs pytest cross_lingual_rag/tests/test_basic_pipeline.py -v and asserts tests pass.
2. Archives / cleans old stale logs.
3. Verifies reference corpus manifest and dual FAISS vector stores (indexes/reference/).
4. Runs benchmark questions (120 full or --limit N) across all 4 systems (A, B, C, D).
5. Runs EvaluationHarness.run_evaluation() to generate:
   - results/benchmark/csv/benchmark_results.csv
   - results/benchmark/summaries/evaluation_report.md
   - results/benchmark/summaries/complete_project_observations.json

Usage:
    python run_complete_experiment.py                # Full 120 questions (480 runs)
    python run_complete_experiment.py --smoke        # Quick 5-question smoke test (20 runs)
    python run_complete_experiment.py --limit 10     # 10 questions (40 runs)
"""

import os
import sys
import time
import json
import shutil
import argparse
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
    """Runs the automated pytest suite and asserts tests pass."""
    print("\n" + "=" * 80)
    print("[Step 1] Running Automated Verification Suite...")
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


def update_history_manifest(archive_base: Path, root: Path):
    """Scans results/archive/runs/ and writes history_manifest.json with all historical runs."""
    runs = []
    for p in sorted(archive_base.iterdir(), reverse=True):
        if p.is_dir() and p.name.startswith("run_"):
            rep = p / "evaluation_report.md"
            csv = p / "benchmark_results.csv"
            obs = p / "complete_project_observations.json"
            obs_data = {}
            if obs.exists():
                try:
                    with open(obs, "r", encoding="utf-8") as f:
                        obs_data = json.load(f)
                except Exception:
                    pass

            time_label = p.name.replace("run_", "").replace("_", " ").title()

            runs.append({
                "run_id": p.name,
                "name": f"Run {time_label}",
                "path": str(p.relative_to(root)).replace("\\", "/"),
                "has_markdown": rep.exists(),
                "has_csv": csv.exists(),
                "has_observations": obs.exists(),
                "total_runs": obs_data.get("total_pipeline_runs", 0),
                "timestamp": obs_data.get("timestamp_utc", datetime.fromtimestamp(p.stat().st_mtime).isoformat()),
                "metrics": obs_data.get("system_metrics_summary", {})
            })

    manifest_file = archive_base / "history_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(runs, f, indent=2, ensure_ascii=False)
    return runs


def archive_previous_run_logs(raw_dir: Path, traces_dir: Path, root: Path, config: dict):
    """Archives previous run logs and reports into results/archive/runs/run_YYYYMMDD_HHMMSS before starting a new isolated run."""
    print("\n" + "=" * 80)
    print("[Step 2] Archiving Previous Run Logs & Traces to History...")
    print("=" * 80)

    archive_base = root / "results" / "archive" / "runs"
    ensure_directory(str(archive_base))

    # Check if there are active logs or reports from a previous run
    has_logs = raw_dir.exists() and any(raw_dir.rglob("*.json"))
    if has_logs:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = archive_base / f"run_{ts}_archived"
        ensure_directory(str(archive_dir / "raw"))
        ensure_directory(str(archive_dir / "traces"))

        summary_dir = root / Path(config["paths"].get("results_summary_dir", "results/benchmark/summaries"))
        csv_dir = root / Path(config["paths"].get("results_csv_dir", "results/benchmark/csv"))
        if (summary_dir / "evaluation_report.md").exists():
            shutil.copy2(summary_dir / "evaluation_report.md", archive_dir / "evaluation_report.md")
        if (summary_dir / "complete_project_observations.json").exists():
            shutil.copy2(summary_dir / "complete_project_observations.json", archive_dir / "complete_project_observations.json")
        if (csv_dir / "benchmark_results.csv").exists():
            shutil.copy2(csv_dir / "benchmark_results.csv", archive_dir / "benchmark_results.csv")

        moved_raw = 0
        for f in list(raw_dir.rglob("*.json")):
            try:
                rel = f.relative_to(raw_dir)
                target = archive_dir / "raw" / rel
                ensure_directory(str(target.parent))
                shutil.move(str(f), str(target))
                moved_raw += 1
            except Exception as e:
                print(f"[Notice] Could not move {f}: {e}")

        moved_traces = 0
        if traces_dir.exists():
            for f in list(traces_dir.rglob("*.json")):
                try:
                    target = archive_dir / "traces" / f.name
                    shutil.move(str(f), str(target))
                    moved_traces += 1
                except Exception as e:
                    print(f"[Notice] Could not move trace {f}: {e}")

        print(f"  -> Preserved and archived previous run to: {archive_dir}")
        print(f"     ({moved_raw} raw JSON logs and {moved_traces} traces preserved in history)")
        update_history_manifest(archive_base, root)
    else:
        print("  -> No pending previous logs to archive. Ready for fresh run.")


def verify_corpus_and_indexes(config: dict):
    """Verifies that reference chunks and indexes exist, rebuilding if necessary."""
    print("\n" + "=" * 80)
    print("[Step 3] Verifying Reference Corpus Manifest & FAISS Vector Stores...")
    print("=" * 80)

    root = get_project_root()
    processed_dir = root / Path(config["paths"].get("processed_dir", "data/processed"))
    manifest_file = processed_dir / "chunks_manifest.json"
    eng_dir = root / Path(config["paths"].get("english_index_dir", "indexes/reference/english"))
    multi_dir = root / Path(config["paths"].get("multilingual_index_dir", "indexes/reference/multilingual"))

    rebuild = False
    if not manifest_file.exists():
        rebuild = True
    elif not (eng_dir / "metadata_map.pkl").exists() or not (multi_dir / "metadata_map.pkl").exists():
        rebuild = True

    if rebuild:
        print("  -> Ingesting reference academic corpus...")
        ingestor = CorpusIngestor(config, mode="reference")
        chunks = ingestor.ingest_corpus()
        print(f"  -> Ingested {len(chunks)} chunks.")
        print("  -> Building Dual FAISS vector stores...")
        build_dual_indexes(config, chunks=chunks, mode="reference")
    else:
        print("  -> Verified existing reference manifest and vector stores.")


def main():
    parser = argparse.ArgumentParser(description="Cross-Lingual RAG Experiment Runner")
    parser.add_argument("--smoke", action="store_true", help="Run quick 5-question smoke test")
    parser.add_argument("--dry-run", "--scenarios", dest="dry_run", action="store_true", help="Run 5-scenario cross-subject dry run (1 question per subject)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions to evaluate")
    parser.add_argument("--strict", action="store_true", help="Enforce strict benchmark mode (no local LLM fallback)")
    parser.add_argument("--skip-pytest", action="store_true", help="Skip running pytest suite")
    args = parser.parse_args()

    if args.dry_run:
        run_type = "dry_run"
        max_q = 5
    elif args.smoke:
        run_type = "smoke"
        max_q = 5
    else:
        run_type = "benchmark"
        max_q = args.limit

    print("=" * 80)
    print(f"[RESEARCH BENCHMARK] ENGLISH-HINDI CROSS-LINGUAL ACADEMIC RAG: {run_type.upper()} SUITE")
    print("=" * 80)

    config = load_config()
    set_seed(config.get("random_seed", 42))
    root = get_project_root()

    # 1. Run Pytest Suite
    pytest_status = {}
    if not args.skip_pytest:
        pytest_status = run_pytest_suite()

    # 2. Archive previous run logs and traces to history
    raw_dir = root / Path(config["paths"].get("results_raw_dir", "results/benchmark/raw"))
    traces_dir = root / "results" / "traces"
    archive_previous_run_logs(raw_dir, traces_dir, root, config)

    # 3. Verify Reference Corpus & FAISS Stores
    verify_corpus_and_indexes(config)

    # 4. Initialize Orchestrator and Execute Benchmark Questions
    print("\n" + "=" * 80)
    print(f"[Step 4] Initializing Pipeline Orchestrator & Executing Runs (Mode: {run_type})...")
    print("=" * 80)
    orchestrator = PipelineOrchestrator(config)

    bench_csv = root / Path(config["paths"].get("benchmark_file", "data/benchmark/questions.csv"))
    df_bench = pd.read_csv(bench_csv)
    if args.dry_run:
        # Sample 1 representative scenario from each subject (Algorithms, Automata, DBMS, Operating Systems, Computer Networks)
        df_bench = df_bench.groupby("subject", as_index=False, sort=False).first()
        if max_q:
            df_bench = df_bench.head(max_q)
    elif max_q:
        df_bench = df_bench.head(max_q)
    total_q = len(df_bench)
    print(f"Loaded {total_q} paired benchmark questions from {bench_csv}")

    run_start_t = time.perf_counter()
    all_runs = []

    for idx, row in df_bench.iterrows():
        q_id = str(row["question_id"])
        subj = str(row.get("subject", "CS"))
        cat = str(row.get("category", "General"))
        q_en = str(row["question_en"])
        q_hi = str(row["question_hi"])

        print(f"  -> [{idx+1:02d}/{total_q:02d}] {q_id} | Subject: {subj:<18} | Category: {cat}")

        # System A: Direct LLM Baseline
        res_a = orchestrator.execute_system_A(q_hi, q_id, subj, cat, run_type=run_type, strict_benchmark=args.strict)
        all_runs.append(res_a)

        # System B: Monolingual English RAG
        res_b = orchestrator.execute_system_B(q_en, q_id, subj, cat, run_type=run_type, strict_benchmark=args.strict)
        all_runs.append(res_b)

        # System C: Translation-Mediated RAG
        res_c = orchestrator.execute_system_C(q_hi, q_id, subj, cat, run_type=run_type, strict_benchmark=args.strict)
        all_runs.append(res_c)

        # System D: Direct Multilingual RAG
        res_d = orchestrator.execute_system_D(q_hi, q_id, subj, cat, run_type=run_type, strict_benchmark=args.strict)
        all_runs.append(res_d)

    total_bench_duration = round(time.perf_counter() - run_start_t, 2)
    print(f"\n[OK] All {len(all_runs)} benchmark pipeline executions completed in {total_bench_duration}s.")

    # 5. Run Evaluation Harness & Generate Reports
    print("\n" + "=" * 80)
    print("[Step 5] Running Scientific Evaluation Harness & Generating Reports...")
    print("=" * 80)
    evaluator = EvaluationHarness(config)
    df_eval, report_md = evaluator.run_evaluation(exclude_smoke=False if (args.smoke or args.dry_run) else True)

    # 6. Save Complete Structured Observations JSON
    summary_dir = root / Path(config["paths"].get("results_summary_dir", "results/benchmark/summaries"))
    obs_path = summary_dir / ("dry_run_observations.json" if args.dry_run else "complete_project_observations.json")

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

    observations_payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "pytest_verification": pytest_status,
        "total_benchmark_questions": total_q,
        "total_pipeline_runs": int(len(df_eval)),
        "system_metrics_summary": sys_summary
    }
    ensure_directory(str(obs_path.parent))
    with open(obs_path, "w", encoding="utf-8") as f:
        json.dump(observations_payload, f, indent=2, ensure_ascii=False)

    if args.dry_run:
        # Also save dedicated dry_run files for immediate tester review
        dry_run_csv = evaluator.csv_dir / "dry_run_results.csv"
        dry_run_md = evaluator.summary_dir / "dry_run_evaluation_report.md"
        df_eval.to_csv(dry_run_csv, index=False)
        with open(dry_run_md, "w", encoding="utf-8") as f:
            f.write(report_md)

    # 7. Persist this completed run into historical archive
    archive_base = root / "results" / "archive" / "runs"
    ensure_directory(str(archive_base))
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_archive_dir = archive_base / f"run_{run_ts}_{run_type}"
    ensure_directory(str(run_archive_dir / "raw"))

    if (evaluator.summary_dir / "evaluation_report.md").exists():
        shutil.copy2(evaluator.summary_dir / "evaluation_report.md", run_archive_dir / "evaluation_report.md")
    if obs_path.exists():
        shutil.copy2(obs_path, run_archive_dir / "complete_project_observations.json")
    if (evaluator.csv_dir / "benchmark_results.csv").exists():
        shutil.copy2(evaluator.csv_dir / "benchmark_results.csv", run_archive_dir / "benchmark_results.csv")

    for f in raw_dir.rglob("*.json"):
        rel = f.relative_to(raw_dir)
        target = run_archive_dir / "raw" / rel
        ensure_directory(str(target.parent))
        shutil.copy2(str(f), str(target))

    update_history_manifest(archive_base, root)

    print("\n" + "=" * 80)
    print("[OK] EXPERIMENT & OBSERVATION RECORDING FULLY COMPLETE!")
    print("=" * 80)
    print(f"1. Consolidated CSV Table : {evaluator.csv_dir}/benchmark_results.csv")
    if args.dry_run:
        print(f"   Dedicated Dry-Run CSV  : {evaluator.csv_dir}/dry_run_results.csv")
    print(f"2. Markdown Evaluation    : {evaluator.summary_dir}/evaluation_report.md")
    if args.dry_run:
        print(f"   Dedicated Dry-Run MD   : {evaluator.summary_dir}/dry_run_evaluation_report.md")
    print(f"3. JSON Observations Log  : {obs_path}")
    print(f"4. Historical Run Archive : {run_archive_dir}")
    print("\nFinal Summary Preview:\n")
    print(report_md)


if __name__ == "__main__":
    main()
