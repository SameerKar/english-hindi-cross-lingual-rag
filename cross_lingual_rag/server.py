"""
Unified FastAPI + WebSocket Server for English-Hindi Cross-Lingual Academic RAG.
Provides real-time terminal streaming, dynamic multi-PDF upload, live chunk inspection,
cross-lingual query execution (Systems A, B, C, D), and automated test runner.
"""

import os
import sys
import time
import json
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

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

from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware

# Ensure cross_lingual_rag and project root are in sys.path
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from src.utils import load_config, ensure_directory, get_project_root
from src.ingestion import CorpusIngestor
from src.vector_store import build_dual_indexes
from src.evaluation import EvaluationHarness
from src.pipelines import PipelineOrchestrator
from src.evaluation import EvaluationHarness

app = FastAPI(title="Cross-Lingual Academic RAG Studio API", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global State & Terminal Manager
# ---------------------------------------------------------------------------
class TerminalManager:
    """Manages WebSocket connections to broadcast terminal commands & logs in real time."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.history: List[str] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send initial history
        for line in self.history[-60:]:
            await websocket.send_text(line)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Timestamped terminal log
        ts = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{ts}] {message}"
        self.history.append(formatted)
        if len(self.history) > 1000:
            self.history.pop(0)

        for connection in list(self.active_connections):
            try:
                await connection.send_text(formatted)
            except Exception:
                self.disconnect(connection)

from datetime import datetime
terminal = TerminalManager()

# Global orchestrator cache
_orchestrator: Optional[PipelineOrchestrator] = None

def get_orchestrator_instance() -> PipelineOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        cfg = load_config()
        _orchestrator = PipelineOrchestrator(cfg)
    return _orchestrator

def reload_orchestrator_instance():
    global _orchestrator
    cfg = load_config()
    _orchestrator = PipelineOrchestrator(cfg)
    return _orchestrator


@app.on_event("startup")
async def startup_warmup():
    """Pre-warms the orchestrator and embedders on server boot to eliminate query cold start."""
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, get_orchestrator_instance)
        await terminal.broadcast("[SYSTEM] RAG Orchestrator & Embedder models pre-warmed and ready.")
    except Exception as e:
        print(f"[Startup Warning] Pre-warm notice: {e}")


# ---------------------------------------------------------------------------
# WebSocket Endpoint for Real-Time Live Terminal
# ---------------------------------------------------------------------------
@app.websocket("/ws/terminal")
async def websocket_terminal(websocket: WebSocket):
    await terminal.connect(websocket)
    await terminal.broadcast("[SYSTEM] Connected to Live Terminal Stream. Ready for commands.")
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client commands if sent via WS
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        terminal.disconnect(websocket)


# ---------------------------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/system-status")
async def get_system_status():
    """Returns current active model configuration, FAISS index stats, and corpus metadata."""
    cfg = load_config()
    orch = get_orchestrator_instance()
    
    # Manifest statistics
    manifest_file = Path(cfg["paths"]["processed_dir"]) / "chunks_manifest.json"
    total_chunks = 0
    subjects = []
    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                total_chunks = len(data)
                subjects = sorted(list(set(c.get("subject", "general") for c in data)))
        except Exception:
            pass

    # Check API keys
    has_openai_key = bool(os.getenv("OPENAI_API_KEY"))
    has_gemini_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    return {
        "status": "ONLINE",
        "provider": orch.generator.provider,
        "model_name": orch.generator.model_name,
        "temperature": orch.generator.temperature,
        "translation_engine": orch.translator.provider,
        "english_embed_model": orch.eng_model_name,
        "multilingual_embed_model": orch.multi_model_name,
        "total_chunks_indexed": total_chunks,
        "subjects": subjects,
        "has_openai_key": has_openai_key,
        "has_gemini_key": has_gemini_key,
        "active_mode": "Real API" if (has_openai_key or has_gemini_key) else "Deterministic Context-Grounded Mock ($0 Cost)"
    }


@app.get("/api/chunks")
async def get_chunks(subject: Optional[str] = None, search: Optional[str] = None):
    """Returns all current chunks in the manifest with optional subject and keyword filtering."""
    cfg = load_config()
    manifest_file = Path(cfg["paths"]["processed_dir"]) / "chunks_manifest.json"
    if not manifest_file.exists():
        return {"chunks": [], "total": 0}

    with open(manifest_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if subject and subject.lower() != "all":
        chunks = [c for c in chunks if c.get("subject", "").lower() == subject.lower()]

    if search and search.strip():
        q = search.lower()
        chunks = [c for c in chunks if q in c.get("text", "").lower() or q in c.get("chunk_id", "").lower()]

    return {"chunks": chunks, "total": len(chunks)}


@app.post("/api/upload-pdfs")
async def upload_pdfs(
    files: List[UploadFile] = File(...),
    subject: str = Form("custom_kb"),
    replace_corpus: bool = Form(False)
):
    """
    Accepts a bunch of PDFs, saves them into data/corpus/<subject>/,
    extracts physical pages with pypdf, creates page-aware chunks, and rebuilds FAISS indexes.
    Streams progress live to the WebSocket terminal.
    """
    cfg = load_config()
    corpus_dir = Path(cfg["paths"]["corpus_dir"])
    clean_subj = subject.strip().lower().replace(" ", "_").replace("-", "_")
    target_dir = corpus_dir / clean_subj
    ensure_directory(str(target_dir))

    await terminal.broadcast(f"[UPLOAD] Received {len(files)} PDF file(s) for subject category: '{clean_subj}'")

    if replace_corpus:
        await terminal.broadcast("[CLEAN] 'Replace Corpus' selected: archiving existing corpus files...")
        # Backup existing to backup directory
        backup_dir = corpus_dir.parent / "corpus_backup"
        if not backup_dir.exists() and corpus_dir.exists():
            shutil.copytree(corpus_dir, backup_dir, dirs_exist_ok=True)
        # Clear out current corpus
        for item in corpus_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            elif item.is_file():
                item.unlink(missing_ok=True)
        ensure_directory(str(target_dir))
        await terminal.broadcast("[CLEAN] Corpus directory refreshed.")

    # Save uploaded files
    saved_files = []
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            continue
        dest_path = target_dir / f.filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        saved_files.append(dest_path)
        await terminal.broadcast(f"[SAVE] Saved '{f.filename}' ({dest_path.stat().st_size / 1024:.1f} KB)")

    if not saved_files:
        return JSONResponse(status_code=400, content={"error": "No valid PDF files were uploaded."})

    # Step 1: Run Ingestion
    await terminal.broadcast(f"[INGEST] Starting page-by-page text extraction on {len(saved_files)} new PDF(s)...")
    ingestor = CorpusIngestor(cfg)
    all_chunks = ingestor.ingest_corpus()
    await terminal.broadcast(f"[CHUNK] Created {len(all_chunks)} page-aware chunks across knowledge base.")

    # Step 2: Build Vector Indexes
    await terminal.broadcast("[EMBED] Encoding chunks with English 768d (all-mpnet-base-v2) & Multilingual 384d models...")
    build_dual_indexes(cfg)
    await terminal.broadcast("[FAISS] Successfully updated English and Multilingual FAISS vector stores.")

    # Step 3: Reload Orchestrator
    reload_orchestrator_instance()
    await terminal.broadcast(f"[READY] Knowledge base live! Total indexed chunks: {len(all_chunks)}. Ready to query.")

    return {
        "success": True,
        "files_uploaded": len(saved_files),
        "total_chunks": len(all_chunks),
        "subject": clean_subj
    }


@app.post("/api/restore-default-corpus")
async def restore_default_corpus():
    """Restores the original 5-subject benchmark corpus and rebuilds indexes."""
    await terminal.broadcast("[RESTORE] Restoring original 5 Computer Science textbook corpus...")
    cfg = load_config()
    backup_dir = Path(cfg["paths"]["corpus_dir"]).parent / "corpus_backup"
    corpus_dir = Path(cfg["paths"]["corpus_dir"])

    if backup_dir.exists():
        shutil.copytree(backup_dir, corpus_dir, dirs_exist_ok=True)
        await terminal.broadcast("[RESTORE] Copied backup files back into data/corpus/.")
    
    ingestor = CorpusIngestor(cfg)
    chunks = ingestor.ingest_corpus()
    build_dual_indexes(cfg)
    reload_orchestrator_instance()
    await terminal.broadcast(f"[RESTORE] Complete! Restored {len(chunks)} default chunks across 5 subjects.")
    return {"success": True, "total_chunks": len(chunks)}


class SaveEnvRequest(BaseModel):
    gemini_api_key: Optional[str] = ""
    openai_api_key: Optional[str] = ""


@app.get("/api/get-env")
async def get_env_config():
    """Returns the current environment setup and masked keys."""
    load_config()
    g_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    o_key = os.getenv("OPENAI_API_KEY") or ""
    
    masked_g = (g_key[:6] + "..." + g_key[-4:]) if len(g_key) > 10 else ("***" if g_key else "")
    masked_o = (o_key[:5] + "..." + o_key[-4:]) if len(o_key) > 9 else ("***" if o_key else "")

    orch = get_orchestrator_instance()
    active_mode = f"Google {orch.generator.model_name} (Cloud API)" if g_key else ("OpenAI API" if o_key else "Deterministic Context-Grounded Synthesizer ($0 Cost)")

    return {
        "has_gemini_key": bool(g_key),
        "has_openai_key": bool(o_key),
        "masked_gemini_key": masked_g,
        "masked_openai_key": masked_o,
        "active_mode": active_mode,
        "provider": orch.generator.provider,
        "model_name": orch.generator.model_name
    }


@app.post("/api/save-env")
async def save_env_config(req: SaveEnvRequest):
    """
    Saves the user's API key directly into .env file,
    updates os.environ, and reloads the generation pipeline live.
    """
    cfg = load_config()
    root = get_project_root()
    env_file = root / ".env"
    if not env_file.exists() and (root.parent / ".env").exists():
        env_file = root.parent / ".env"
    elif not env_file.exists():
        env_file = root / ".env"

    g_key = (req.gemini_api_key or "").strip()
    o_key = (req.openai_api_key or "").strip()

    # Read existing lines if any
    existing_lines = []
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            existing_lines = [line.strip() for line in f.readlines() if line.strip()]

    # Filter out existing GEMINI_API_KEY and OPENAI_API_KEY
    new_lines = [line for line in existing_lines if not line.startswith("GEMINI_API_KEY=") and not line.startswith("OPENAI_API_KEY=")]
    
    if g_key:
        new_lines.append(f"GEMINI_API_KEY={g_key}")
        os.environ["GEMINI_API_KEY"] = g_key
    elif "GEMINI_API_KEY" in os.environ and not g_key:
        del os.environ["GEMINI_API_KEY"]

    if o_key:
        new_lines.append(f"OPENAI_API_KEY={o_key}")
        os.environ["OPENAI_API_KEY"] = o_key
    elif "OPENAI_API_KEY" in os.environ and not o_key:
        del os.environ["OPENAI_API_KEY"]

    # Write back to .env
    with open(env_file, "w", encoding="utf-8") as f:
        f.write("# Cross-Lingual Academic RAG Auto-Generated .env\n")
        for line in new_lines:
            f.write(line + "\n")

    # Also sync to cross_lingual_rag/.env if distinct
    alt_env = script_dir / ".env"
    if alt_env != env_file:
        try:
            shutil.copy(env_file, alt_env)
        except Exception:
            pass

    # Reload orchestrator live
    reload_orchestrator_instance()
    orch = get_orchestrator_instance()

    active_mode = "Gemini 2.0 Flash (Free API)" if g_key else ("OpenAI API" if o_key else "Deterministic Context-Grounded Synthesizer ($0 Cost)")
    await terminal.broadcast(f"[ENV] Environment updated live! Active LLM Mode: {active_mode} (Provider: {orch.generator.provider}, Model: {orch.generator.model_name})")

    return {
        "success": True,
        "active_mode": active_mode,
        "provider": orch.generator.provider,
        "model_name": orch.generator.model_name,
        "has_gemini_key": bool(g_key),
        "has_openai_key": bool(o_key),
        "env_path": str(env_file)
    }


class QueryRequest(BaseModel):
    question_hi: str
    question_en: Optional[str] = None
    subject: Optional[str] = "custom"
    category: Optional[str] = "general"
    question_id: Optional[str] = "LIVE_Q"
    systems: List[str] = ["A", "B", "C", "D"]
    subject_filter: Optional[str] = "all"


@app.post("/api/query")
async def execute_query(req: QueryRequest):
    """
    Executes a cross-lingual query across Systems A, B, C, and D.
    Streams step-by-step progress to the live terminal and returns structured results.
    """
    orch = get_orchestrator_instance()
    q_hi = req.question_hi.strip()
    q_en = (req.question_en or q_hi).strip()
    qid = req.question_id or "LIVE_01"
    subj = req.subject or "general"
    cat = req.category or "general"
    s_filter = req.subject_filter or "all"

    await terminal.broadcast(f"[QUERY] Received query: '{q_hi[:60]}...' (Scope Filter: {s_filter})")

    results: Dict[str, Any] = {}

    # System C: Translation-Mediated RAG
    if "C" in req.systems:
        await terminal.broadcast("[SYS-C] Step 1/3: Translating Hindi query to English...")
        t0 = time.perf_counter()
        res_c = orch.execute_system_C(q_hi, qid, subj, cat, subject_filter=s_filter)
        dur_c = round((time.perf_counter() - t0) * 1000.0, 1)
        trans_q = res_c.get("translated_question", "")
        top_chunk = res_c.get("retrieved_chunks", ["NONE"])[0]
        top_score = res_c.get("retrieval_scores", [0.0])[0] if res_c.get("retrieval_scores") else 0.0
        await terminal.broadcast(f"[SYS-C] Translated: '{trans_q}'")
        await terminal.broadcast(f"[SYS-C] Top-1 Chunk: `{top_chunk}` (Score: {top_score:.4f}) in {dur_c}ms")
        results["C"] = res_c

    # System D: Direct Multilingual RAG
    if "D" in req.systems:
        await terminal.broadcast("[SYS-D] Zero-Shot Multilingual Search (No translation)...")
        t0 = time.perf_counter()
        res_d = orch.execute_system_D(q_hi, qid, subj, cat, subject_filter=s_filter)
        dur_d = round((time.perf_counter() - t0) * 1000.0, 1)
        top_chunk_d = res_d.get("retrieved_chunks", ["NONE"])[0]
        top_score_d = res_d.get("retrieval_scores", [0.0])[0] if res_d.get("retrieval_scores") else 0.0
        await terminal.broadcast(f"[SYS-D] Top-1 Chunk: `{top_chunk_d}` (Score: {top_score_d:.4f}) in {dur_d}ms")
        results["D"] = res_d

    # System B: Monolingual English RAG
    if "B" in req.systems:
        await terminal.broadcast("[SYS-B] Running Monolingual English Upper-Bound RAG...")
        res_b = orch.execute_system_B(q_en, qid, subj, cat, subject_filter=s_filter)
        results["B"] = res_b

    # System A: Direct LLM Baseline
    if "A" in req.systems:
        await terminal.broadcast("[SYS-A] Running Direct Parametric LLM Baseline (Zero Retrieval)...")
        res_a = orch.execute_system_A(q_hi, qid, subj, cat)
        lat_a = res_a.get("latencies", {}).get("total_latency_ms", 0.0)
        ans_preview = (res_a.get("generated_answer") or "").replace("\n", " ")[:60]
        await terminal.broadcast(f"[SYS-A] Answer generated in {lat_a:.1f}ms: '{ans_preview}...'")
        results["A"] = res_a

    await terminal.broadcast("[QUERY] All requested systems completed successfully.")
    return {"success": True, "results": results}


@app.post("/api/run-pytest")
async def run_pytest_command():
    """Runs the 7-point pytest suite and streams stdout live to the terminal."""
    await terminal.broadcast("[PYTEST] Triggering 7-Point Automated Verification Suite...")
    
    test_file = script_dir / "tests" / "test_basic_pipeline.py"
    proc = subprocess.Popen(
        [sys.executable, "-m", "pytest", str(test_file), "-v"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )

    for line in proc.stdout:
        await terminal.broadcast(line.strip())
    proc.wait()

    passed = (proc.returncode == 0)
    status_str = "PASSED (7/7)" if passed else f"FAILED (Code {proc.returncode})"
    await terminal.broadcast(f"[PYTEST] Verification Suite Finished: {status_str}")
    return {"passed": passed, "exit_code": proc.returncode}


@app.post("/api/run-benchmark")
async def run_benchmark_command():
    """Runs the complete 68-run benchmark and streams stdout live to the terminal."""
    await terminal.broadcast("[BENCHMARK] Launching 68-Run Scientific Benchmark Suite...")
    
    bench_file = script_dir / "run_complete_experiment.py"
    proc = subprocess.Popen(
        [sys.executable, str(bench_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )

    for line in proc.stdout:
        await terminal.broadcast(line.strip())
    proc.wait()

    reload_orchestrator_instance()
    await terminal.broadcast("[BENCHMARK] Complete 68-Run Execution Finished and Reports Updated.")
    return {"success": proc.returncode == 0, "exit_code": proc.returncode}


# ---------------------------------------------------------------------------
# Report Generation & Download Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/report/latest")
async def get_latest_report():
    """
    Returns the latest scientific evaluation report in Markdown and summary metrics.
    If the report file doesn't exist yet, it automatically runs the evaluation harness.
    """
    cfg = load_config()
    report_path = Path(cfg["paths"]["results_summary_dir"]) / "evaluation_report.md"
    csv_path = Path(cfg["paths"]["results_csv_dir"]) / "benchmark_results.csv"

    if not report_path.exists():
        harness = EvaluationHarness(cfg)
        harness.run_evaluation()

    content = ""
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

    mtime_str = ""
    if report_path.exists():
        mtime = datetime.fromtimestamp(report_path.stat().st_mtime)
        mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "success": True,
        "markdown": content,
        "last_updated": mtime_str,
        "has_csv": csv_path.exists(),
        "has_markdown": report_path.exists()
    }


@app.get("/api/report/download/markdown")
async def download_report_markdown():
    """Downloads the evaluation_report.md file as an attachment."""
    cfg = load_config()
    report_path = Path(cfg["paths"]["results_summary_dir"]) / "evaluation_report.md"
    if not report_path.exists():
        harness = EvaluationHarness(cfg)
        harness.run_evaluation()
    if not report_path.exists():
        return JSONResponse(status_code=404, content={"error": "Report not found"})
    return FileResponse(
        str(report_path),
        media_type="text/markdown",
        filename="cross_lingual_rag_evaluation_report.md"
    )


@app.get("/api/report/download/csv")
async def download_report_csv():
    """Downloads the consolidated benchmark_results.csv as an attachment."""
    cfg = load_config()
    csv_path = Path(cfg["paths"]["results_csv_dir"]) / "benchmark_results.csv"
    if not csv_path.exists():
        harness = EvaluationHarness(cfg)
        harness.run_evaluation()
    if not csv_path.exists():
        return JSONResponse(status_code=404, content={"error": "Benchmark CSV not found"})
    return FileResponse(
        str(csv_path),
        media_type="text/csv",
        filename="cross_lingual_rag_benchmark_results.csv"
    )


class QueryReportPayload(BaseModel):
    question_hi: str
    question_en: Optional[str] = ""
    scope: Optional[str] = "all"
    results: Dict[str, Any]


@app.post("/api/report/download/query")
async def download_query_report(payload: QueryReportPayload):
    """
    Dynamically generates and returns a structured Markdown evaluation report for the latest live query execution.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md = []
    md.append("# Live Query Execution Report: English–Hindi Cross-Lingual RAG")
    md.append(f"**Execution Timestamp:** {ts}")
    md.append(f"**Search Scope Filter:** `{payload.scope}`\n")
    md.append("## Query Inputs")
    md.append(f"- **Hindi Input Query:** {payload.question_hi}")
    if payload.question_en:
        md.append(f"- **English Baseline Query:** {payload.question_en}")
    md.append("\n---\n")

    md.append("## Systems Comparison Breakdown\n")

    res = payload.results
    # System C
    if "C" in res:
        c = res["C"]
        lat = c.get("latencies", {}).get("total_latency_ms", 0.0)
        trans = c.get("translated_question", "N/A")
        ans = c.get("generated_answer", "")
        md.append("### System C · Translation-Mediated RAG")
        md.append(f"- **Total Latency:** {lat:.1f} ms")
        md.append(f"- **Machine Translated Query:** `{trans}`")
        md.append(f"- **Synthesized Answer:**\n> {ans}\n")
        md.append("#### Retrieved Evidentiary Chunks (Top-5):")
        for idx, item in enumerate(c.get("retrieved_chunks_details", [])[:5]):
            md.append(f"{idx+1}. **`{item.get('chunk_id')}`** | Doc: `{item.get('doc_id')}` | Page: **{item.get('page')}** | Cosine Score: **{item.get('score')}** ({item.get('relevance_pct')}%)")
            md.append(f"   > *Snippet:* {item.get('text', '')[:220]}...\n")

    # System D
    if "D" in res:
        d = res["D"]
        lat = d.get("latencies", {}).get("total_latency_ms", 0.0)
        ans = d.get("generated_answer", "")
        md.append("### System D · Direct Multilingual RAG (Zero MT)")
        md.append(f"- **Total Latency:** {lat:.1f} ms (Zero Machine Translation)")
        md.append(f"- **Synthesized Answer:**\n> {ans}\n")
        md.append("#### Retrieved Evidentiary Chunks (Top-5):")
        for idx, item in enumerate(d.get("retrieved_chunks_details", [])[:5]):
            md.append(f"{idx+1}. **`{item.get('chunk_id')}`** | Doc: `{item.get('doc_id')}` | Page: **{item.get('page')}** | Cosine Score: **{item.get('score')}** ({item.get('relevance_pct')}%)")
            md.append(f"   > *Snippet:* {item.get('text', '')[:220]}...\n")

    # System B
    if "B" in res:
        b = res["B"]
        lat = b.get("latencies", {}).get("total_latency_ms", 0.0)
        ans = b.get("generated_answer", "")
        md.append("### System B · Monolingual English RAG (Upper Bound)")
        md.append(f"- **Total Latency:** {lat:.1f} ms")
        md.append(f"- **Synthesized Answer:**\n> {ans}\n")
        for idx, item in enumerate(b.get("retrieved_chunks_details", [])[:3]):
            md.append(f"{idx+1}. **`{item.get('chunk_id')}`** | Page: **{item.get('page')}** | Score: **{item.get('score')}**")

    # System A
    if "A" in res:
        a = res["A"]
        lat = a.get("latencies", {}).get("total_latency_ms", 0.0)
        ans = a.get("generated_answer", "")
        md.append("### System A · Direct Parametric LLM Baseline")
        md.append(f"- **Total Latency:** {lat:.1f} ms (Zero Retrieval)")
        md.append(f"- **Generated Answer:**\n> {ans}\n")

    report_text = "\n".join(md)
    return Response(
        content=report_text,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=latest_query_execution_report.md"}
    )


# ---------------------------------------------------------------------------
# Static Files & Single-Page Frontend
# ---------------------------------------------------------------------------
static_dir = script_dir / "static"
ensure_directory(str(static_dir))
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = static_dir / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h3>Frontend not found. Please build static/index.html</h3>", status_code=404)
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("[STARTING] Cross-Lingual Academic RAG Studio Unified Web Server on port 8000...")
    print("=" * 80)
    uvicorn.run(app, host="0.0.0.0", port=8000)
