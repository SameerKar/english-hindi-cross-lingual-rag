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
from fastapi.responses import HTMLResponse, JSONResponse
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
