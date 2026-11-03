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


def format_file_size(size_bytes: int) -> str:
    """Formats file size in bytes into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


@app.post("/api/upload-pdfs")
@app.post("/api/upload-docs")
async def upload_documents(
    files: List[UploadFile] = File(...),
    subject: str = Form("uploaded_docs"),
    replace_corpus: bool = Form(False)
):
    """
    Accepts academic documents (.pdf, .txt, .md), saves them into data/corpus/<subject>/,
    extracts physical/virtual pages, creates page-aware chunks, and rebuilds FAISS indexes.
    Streams progress live to the WebSocket terminal.
    """
    cfg = load_config()
    corpus_dir = Path(cfg["paths"]["corpus_dir"])
    clean_subj = subject.strip().lower().replace(" ", "_").replace("-", "_") or "uploaded_docs"
    target_dir = corpus_dir / clean_subj
    ensure_directory(str(target_dir))

    await terminal.broadcast(f"[UPLOAD] Received {len(files)} document(s) (.pdf, .txt, .md) for collection: '{clean_subj}'")

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

    # Save uploaded files (.pdf, .txt, .md)
    allowed_exts = {".pdf", ".txt", ".md"}
    saved_files = []
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in allowed_exts:
            await terminal.broadcast(f"[WARN] Skipped unsupported file format: '{f.filename}' (only .pdf, .txt, .md accepted)")
            continue
        dest_path = target_dir / f.filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        saved_files.append(dest_path)
        await terminal.broadcast(f"[SAVE] Saved '{f.filename}' ({format_file_size(dest_path.stat().st_size)})")

    if not saved_files:
        return JSONResponse(status_code=400, content={"error": "No valid PDF, TXT, or MD files were uploaded."})

    # Step 1: Run Ingestion
    await terminal.broadcast(f"[INGEST] Starting page-aware extraction across {len(saved_files)} new file(s)...")
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


@app.get("/api/documents/tree")
async def get_documents_tree():
    """
    Scans data/corpus/ and returns a structured tree grouped by folder/subject,
    with file metadata (format, size, pages, chunks, last modified).
    """
    cfg = load_config()
    corpus_dir = Path(cfg["paths"]["corpus_dir"])
    metadata_path = Path(cfg["paths"].get("processed_dir", "data/processed")) / "corpus_metadata.json"

    meta_lookup = {}
    if metadata_path.exists():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta_list = json.load(f)
                for item in meta_list:
                    # Key by relative path or file_name + subject
                    rel = item.get("file_name", "")
                    subj = item.get("subject", "")
                    meta_lookup[f"{subj}/{rel}"] = item
                    meta_lookup[rel] = item
        except Exception as e:
            print(f"[Warning] Failed to load corpus_metadata.json: {e}")

    supported_exts = {".pdf", ".txt", ".md"}
    folders: Dict[str, List[Dict[str, Any]]] = {}
    total_docs = 0
    pdf_count = 0
    txt_count = 0
    md_count = 0

    if corpus_dir.exists():
        for file_path in sorted(corpus_dir.rglob("*")):
            if not file_path.is_file():
                continue
            ext = file_path.suffix.lower()
            if ext not in supported_exts:
                continue

            folder_name = file_path.parent.name if file_path.parent != corpus_dir else "general"
            rel_path = str(file_path.relative_to(corpus_dir)).replace("\\", "/")

            if ext == ".pdf":
                pdf_count += 1
                type_label = "PDF"
            elif ext == ".md":
                md_count += 1
                type_label = "Markdown"
            else:
                txt_count += 1
                type_label = "Text"

            st = file_path.stat()
            size_bytes = st.st_size
            mod_time = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")

            # Look up ingestion metadata
            meta = meta_lookup.get(f"{folder_name}/{file_path.name}") or meta_lookup.get(file_path.name) or {}
            total_pages = meta.get("total_pages", 1)
            total_chunks = meta.get("total_chunks", 0)
            doc_id = meta.get("document_id", f"{folder_name}_{file_path.stem}".lower())

            doc_info = {
                "name": file_path.name,
                "folder": folder_name,
                "relative_path": rel_path,
                "extension": ext,
                "type": type_label,
                "size_bytes": size_bytes,
                "size_formatted": format_file_size(size_bytes),
                "modified_at": mod_time,
                "total_pages": total_pages,
                "total_chunks": total_chunks,
                "document_id": doc_id
            }

            if folder_name not in folders:
                folders[folder_name] = []
            folders[folder_name].append(doc_info)
            total_docs += 1

    return {
        "success": True,
        "total_documents": total_docs,
        "total_folders": len(folders),
        "summary": {
            "pdf_count": pdf_count,
            "txt_count": txt_count,
            "md_count": md_count
        },
        "folders": folders
    }


@app.get("/api/document/view")
async def view_document_content(path: str):
    """
    Securely reads and returns the extracted content and page-by-page breakdown of any document.
    Supports .pdf (via pypdf), .txt, and .md files strictly within data/corpus/.
    """
    cfg = load_config()
    corpus_dir = Path(cfg["paths"]["corpus_dir"]).resolve()
    
    # Path traversal protection
    clean_path = path.strip().replace("\\", "/").lstrip("/")
    target_file = (corpus_dir / clean_path).resolve()

    if not str(target_file).startswith(str(corpus_dir)) or not target_file.exists() or not target_file.is_file():
        return JSONResponse(status_code=404, content={"error": "Document not found or access denied."})

    ext = target_file.suffix.lower()
    rel_path = str(target_file.relative_to(corpus_dir)).replace("\\", "/")
    file_size = target_file.stat().st_size
    pages: List[Dict[str, Any]] = []

    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(str(target_file))
            for idx, page in enumerate(reader.pages):
                txt = (page.extract_text() or "").strip()
                pages.append({
                    "page_number": idx + 1,
                    "text": txt if txt else "[No extractable text found on this page - likely a scanned or diagram page]"
                })
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to extract PDF: {str(e)}"})
        
        full_text = "\n\n" + ("=" * 40) + "\n\n".join(f"--- PAGE {p['page_number']} ---\n{p['text']}" for p in pages)
        return {
            "success": True,
            "file_name": target_file.name,
            "folder": target_file.parent.name,
            "relative_path": rel_path,
            "extension": ext,
            "type": "PDF",
            "size_formatted": format_file_size(file_size),
            "total_pages": len(pages),
            "pages": pages,
            "full_text": full_text,
            "can_embed_pdf": True,
            "raw_url": f"/api/document/raw?path={rel_path}"
        }

    elif ext in {".txt", ".md"}:
        try:
            with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Check if page delimiters exist
            if "--- PAGE" in content or "=== PAGE" in content:
                import re
                parts = re.split(r'(?:---|===)\s*PAGE\s*(\d+)\s*(?:---|===)', content)
                if parts[0].strip():
                    pages.append({"page_number": 1, "text": parts[0].strip()})
                for i in range(1, len(parts), 2):
                    page_num = int(parts[i])
                    page_txt = parts[i+1].strip()
                    pages.append({"page_number": page_num, "text": page_txt})
            else:
                # Break down into virtual pages
                paragraphs = content.split("\n\n")
                current_p = 1
                current_chunks = []
                cur_len = 0
                for para in paragraphs:
                    current_chunks.append(para)
                    cur_len += len(para)
                    if cur_len >= 3000:
                        pages.append({"page_number": current_p, "text": "\n\n".join(current_chunks)})
                        current_p += 1
                        current_chunks = []
                        cur_len = 0
                if current_chunks:
                    pages.append({"page_number": current_p, "text": "\n\n".join(current_chunks)})
                if not pages:
                    pages.append({"page_number": 1, "text": content})

            return {
                "success": True,
                "file_name": target_file.name,
                "folder": target_file.parent.name,
                "relative_path": rel_path,
                "extension": ext,
                "type": "Markdown" if ext == ".md" else "Text",
                "size_formatted": format_file_size(file_size),
                "total_pages": len(pages),
                "pages": pages,
                "full_text": content,
                "can_embed_pdf": False,
                "raw_url": f"/api/document/raw?path={rel_path}"
            }
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to read document: {str(e)}"})

    return JSONResponse(status_code=400, content={"error": "Unsupported file format."})


@app.get("/api/document/raw")
async def get_raw_document(path: str):
    """
    Serves the raw document file directly for in-browser PDF viewing or raw text download.
    Strictly constrained to data/corpus/.
    """
    cfg = load_config()
    corpus_dir = Path(cfg["paths"]["corpus_dir"]).resolve()
    clean_path = path.strip().replace("\\", "/").lstrip("/")
    target_file = (corpus_dir / clean_path).resolve()

    if not str(target_file).startswith(str(corpus_dir)) or not target_file.exists() or not target_file.is_file():
        return JSONResponse(status_code=404, content={"error": "File not found or access denied."})

    ext = target_file.suffix.lower()
    media_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain; charset=utf-8",
        ".md": "text/markdown; charset=utf-8"
    }
    media_type = media_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(target_file),
        media_type=media_type,
        filename=target_file.name,
        headers={"Content-Disposition": f"inline; filename=\"{target_file.name}\""}
    )


@app.post("/api/restore-default-corpus")
@app.post("/api/refresh-everything")
async def restore_default_corpus():
    """
    Completely refreshes the system back to the original 5 Computer Science textbook corpus:
    - Clears all custom/uploaded documents from data/corpus/
    - Restores the original 5 subject folders (algorithms, automata, computer_networks, dbms, operating_systems)
    - Purges all old indexes (.faiss, .pkl, .dat, .npy) and chunk manifests
    - Ingests the 5 textbooks to produce exactly 15 page-aware chunks
    - Rebuilds both English 768d and Multilingual 384d FAISS vector stores
    - Reloads orchestrator live
    - Streams progress step-by-step to the live terminal
    """
    await terminal.broadcast("[REFRESH] Initiating complete system refresh to original 5 Computer Science textbooks...")
    cfg = load_config()
    data_dir = Path(cfg["paths"]["corpus_dir"]).parent
    corpus_dir = Path(cfg["paths"]["corpus_dir"])
    backup_dir = data_dir / "corpus_default_backup"

    # 1. Clean out all current files in data/corpus/
    await terminal.broadcast("[CLEAN] Wiping all custom and uploaded documents from data/corpus/...")
    if corpus_dir.exists():
        for item in corpus_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            elif item.is_file():
                item.unlink(missing_ok=True)
    ensure_directory(str(corpus_dir))

    # 2. Restore 5 original subject folders
    original_subjects = ["algorithms", "automata", "computer_networks", "dbms", "operating_systems"]
    if backup_dir.exists():
        for subj in original_subjects:
            src = backup_dir / subj
            dst = corpus_dir / subj
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        # Fallback: extract directly from git commit 8742fe9 if backup dir is missing
        import subprocess
        for subj in original_subjects:
            dst = corpus_dir / subj
            ensure_directory(str(dst))
            fname = f"{subj}_fundamentals.txt" if subj == "algorithms" else (f"{subj}_theory.txt" if subj == "automata" else (f"database_systems.txt" if subj == "dbms" else f"{subj}.txt"))
            git_path = f"cross_lingual_rag/data/corpus/{subj}/{fname}"
            try:
                content = subprocess.check_output(["git", "show", f"8742fe9:{git_path}"]).decode("utf-8")
                with open(dst / fname, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                print(f"[Warning] Git fallback restore for {git_path}: {e}")

    await terminal.broadcast("[RESTORE] Restored 5 default subjects: algorithms, automata, computer_networks, dbms, operating_systems.")

    # 3. Purge existing indexes (.faiss, .pkl, .dat, .npy) in english and multilingual index dirs
    await terminal.broadcast("[PURGE] Purging legacy FAISS vector index files (.faiss, .pkl, .dat)...")
    for idx_key in ["english_index_dir", "multilingual_index_dir"]:
        p = Path(cfg["paths"].get(idx_key, ""))
        if p.exists() and p.is_dir():
            for f in p.iterdir():
                if f.is_file():
                    try:
                        f.unlink(missing_ok=True)
                    except Exception:
                        pass

    # 4. Purge processed artifacts
    processed_dir = Path(cfg["paths"].get("processed_dir", "data/processed"))
    for art in ["chunks_manifest.json", "corpus_metadata.json"]:
        p = processed_dir / art
        if p.exists():
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass

    # 5. Ingestion of 5 default books
    await terminal.broadcast("[INGEST] Re-extracting text & generating page-aware chunks for 5 original textbooks...")
    ingestor = CorpusIngestor(cfg)
    chunks = ingestor.ingest_corpus()
    await terminal.broadcast(f"[CHUNK] Created exactly {len(chunks)} page-aware chunks across 5 original subjects.")

    # 6. Rebuild Dual FAISS Indexes
    await terminal.broadcast("[EMBED] Rebuilding dual vector stores: English 768d (all-mpnet-base-v2) & Multilingual 384d...")
    build_dual_indexes(cfg)
    await terminal.broadcast("[FAISS] Vector stores successfully regenerated and persisted.")

    # 7. Reload Orchestrator live
    reload_orchestrator_instance()
    await terminal.broadcast(f"[READY] Complete system refresh successful! Active: 5 Computer Science textbooks ({len(chunks)} chunks).")

    return {
        "success": True,
        "total_chunks": len(chunks),
        "total_documents": 5,
        "subjects": original_subjects,
        "message": f"Successfully restored pristine 5-subject baseline ({len(chunks)} chunks)."
    }


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

    try:
        # System C: Translation-Mediated RAG
        if "C" in req.systems:
            await terminal.broadcast("[SYS-C] Step 1/3: Translating Hindi query to English...")
            t0 = time.perf_counter()
            res_c = orch.execute_system_C(q_hi, qid, subj, cat, subject_filter=s_filter)
            dur_c = round((time.perf_counter() - t0) * 1000.0, 1)
            trans_q = res_c.get("translated_question", "")
            chunks_c = res_c.get("retrieved_chunks") or []
            top_chunk = chunks_c[0] if chunks_c else "NONE"
            scores_c = res_c.get("retrieval_scores") or []
            top_score = scores_c[0] if scores_c else 0.0
            await terminal.broadcast(f"[SYS-C] Translated: '{trans_q}'")
            await terminal.broadcast(f"[SYS-C] Top-1 Chunk: `{top_chunk}` (Score: {top_score:.4f}) in {dur_c}ms")
            results["C"] = res_c

        # System D: Direct Multilingual RAG
        if "D" in req.systems:
            await terminal.broadcast("[SYS-D] Zero-Shot Multilingual Search (No translation)...")
            t0 = time.perf_counter()
            res_d = orch.execute_system_D(q_hi, qid, subj, cat, subject_filter=s_filter)
            dur_d = round((time.perf_counter() - t0) * 1000.0, 1)
            chunks_d = res_d.get("retrieved_chunks") or []
            top_chunk_d = chunks_d[0] if chunks_d else "NONE"
            scores_d = res_d.get("retrieval_scores") or []
            top_score_d = scores_d[0] if scores_d else 0.0
            await terminal.broadcast(f"[SYS-D] Top-1 Chunk: `{top_chunk_d}` (Score: {top_score_d:.4f}) in {dur_d}ms")
            results["D"] = res_d

        # System B: Monolingual English RAG
        if "B" in req.systems:
            await terminal.broadcast("[SYS-B] Running Monolingual English Upper-Bound RAG...")
            t0 = time.perf_counter()
            res_b = orch.execute_system_B(q_en, qid, subj, cat, subject_filter=s_filter)
            dur_b = round((time.perf_counter() - t0) * 1000.0, 1)
            chunks_b = res_b.get("retrieved_chunks") or []
            top_chunk_b = chunks_b[0] if chunks_b else "NONE"
            scores_b = res_b.get("retrieval_scores") or []
            top_score_b = scores_b[0] if scores_b else 0.0
            await terminal.broadcast(f"[SYS-B] Top-1 Chunk: `{top_chunk_b}` (Score: {top_score_b:.4f}) in {dur_b}ms")
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

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[Query Error] Exception in /api/query: {tb}")
        await terminal.broadcast(f"[ERROR] Query failed: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e), "traceback": tb})


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
