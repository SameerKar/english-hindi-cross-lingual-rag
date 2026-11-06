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

# Global orchestrator cache per workspace
_orchestrators: Dict[str, PipelineOrchestrator] = {}

def get_orchestrator_instance(workspace_id: str = "reference") -> PipelineOrchestrator:
    clean_ws = workspace_id or "reference"
    if clean_ws not in _orchestrators:
        cfg = load_config()
        _orchestrators[clean_ws] = PipelineOrchestrator(cfg, workspace_id=clean_ws)
    return _orchestrators[clean_ws]

def reload_orchestrator_instance(workspace_id: str = "reference") -> PipelineOrchestrator:
    clean_ws = workspace_id or "reference"
    cfg = load_config()
    _orchestrators[clean_ws] = PipelineOrchestrator(cfg, workspace_id=clean_ws)
    return _orchestrators[clean_ws]


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


@app.get("/api/workspaces")
async def list_workspaces():
    """Lists all user custom workspaces in data/corpus/custom/."""
    cfg = load_config()
    root = get_project_root()
    custom_dir = root / "data" / "corpus" / "custom"
    ensure_directory(str(custom_dir))

    workspaces = []
    for item in sorted(custom_dir.iterdir()):
        if item.is_dir():
            ws_id = item.name
            orig_dir = item / "originals"
            docs = list(orig_dir.glob("*.*")) if orig_dir.exists() else []
            manifest_file = item / "processed" / "chunks_manifest.json"
            chunks_count = 0
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        chunks_count = len(json.load(f))
                except Exception:
                    pass
            workspaces.append({
                "workspace_id": ws_id,
                "name": ws_id.replace("_", " ").title(),
                "documents_count": len(docs),
                "chunks_count": chunks_count,
                "is_indexed": chunks_count > 0
            })
    return {"workspaces": workspaces}


class CreateWorkspaceRequest(BaseModel):
    workspace_id: str


@app.post("/api/workspaces/create")
async def create_workspace(req: CreateWorkspaceRequest):
    root = get_project_root()
    clean_id = "".join(c for c in req.workspace_id if c.isalnum() or c in "-_").lower().strip() or "workspace_1"
    ws_dir = root / "data" / "corpus" / "custom" / clean_id
    ensure_directory(str(ws_dir / "originals"))
    ensure_directory(str(ws_dir / "processed"))
    await terminal.broadcast(f"[WORKSPACE] Created custom collection '{clean_id}'")
    return {"success": True, "workspace_id": clean_id}


@app.post("/api/workspaces/delete")
async def delete_workspace(workspace_id: str = Form(...)):
    root = get_project_root()
    clean_id = "".join(c for c in workspace_id if c.isalnum() or c in "-_").lower().strip()
    if clean_id in ["reference", "default_backup", "corpus"]:
        return JSONResponse(status_code=400, content={"error": "Cannot delete protected reference corpus."})
    ws_dir = root / "data" / "corpus" / "custom" / clean_id
    idx_dir = root / "indexes" / "custom" / clean_id
    if ws_dir.exists():
        shutil.rmtree(ws_dir, ignore_errors=True)
    if idx_dir.exists():
        shutil.rmtree(idx_dir, ignore_errors=True)
    await terminal.broadcast(f"[WORKSPACE] Deleted custom collection '{clean_id}'")
    return {"success": True, "deleted_id": clean_id}


@app.post("/api/upload-pdfs")
@app.post("/api/upload-docs")
async def upload_documents(
    files: List[UploadFile] = File(...),
    workspace_id: str = Form("default"),
    subject: str = Form("custom_docs")
):
    """
    Accepts academic documents (.pdf, .txt, .md, .docx, .html), saves them into
    isolated workspace: data/corpus/custom/<workspace_id>/originals/,
    extracts physical/virtual pages, builds isolated custom FAISS indexes.
    STRICTLY NEVER MODIFIES OR MUTATES THE REFERENCE BENCHMARK CORPUS!
    """
    cfg = load_config()
    root = get_project_root()
    clean_ws = "".join(c for c in workspace_id if c.isalnum() or c in "-_").lower().strip() or "default"
    clean_subj = "".join(c for c in subject if c.isalnum() or c in "-_").lower().strip() or "custom_docs"

    target_dir = root / "data" / "corpus" / "custom" / clean_ws / "originals"
    ensure_directory(str(target_dir))

    await terminal.broadcast(f"[UPLOAD] Received {len(files)} document(s) for Custom Workspace '{clean_ws}'...")

    allowed_exts = {".pdf", ".txt", ".md", ".docx", ".html", ".htm"}
    saved_files = []
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in allowed_exts:
            await terminal.broadcast(f"[WARN] Skipped unsupported file: '{f.filename}' (Allowed: PDF, TXT, MD, DOCX, HTML)")
            continue
        dest_path = target_dir / f.filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        saved_files.append(dest_path)
        await terminal.broadcast(f"[SAVE] Saved '{f.filename}' ({format_file_size(dest_path.stat().st_size)})")

    if not saved_files:
        return JSONResponse(status_code=400, content={"error": "No supported files uploaded. Only PDF, TXT, MD, DOCX, HTML accepted."})

    # Step 1: Ingest into isolated custom workspace
    await terminal.broadcast(f"[INGEST] Ingesting documents for workspace '{clean_ws}'...")
    ingestor = CorpusIngestor(cfg, mode="custom", workspace_id=clean_ws)
    chunks = ingestor.ingest_corpus()
    await terminal.broadcast(f"[CHUNK] Created {len(chunks)} chunks in custom workspace '{clean_ws}'.")

    # Step 2: Build isolated custom FAISS vector stores
    await terminal.broadcast(f"[EMBED] Building custom FAISS vector stores in indexes/custom/{clean_ws}/...")
    build_dual_indexes(cfg, chunks=chunks, mode="custom", workspace_id=clean_ws)
    reload_orchestrator_instance(clean_ws)
    await terminal.broadcast(f"[READY] Custom Workspace '{clean_ws}' indexed ({len(chunks)} chunks). Reference corpus untouched.")

    return {
        "success": True,
        "workspace_id": clean_ws,
        "files_uploaded": len(saved_files),
        "total_chunks": len(chunks)
    }


@app.get("/api/documents/tree")
async def get_documents_tree(mode: str = "reference", workspace_id: Optional[str] = None):
    """
    Scans corpus folder (Reference or Custom Workspace) and returns a structured tree
    grouped by folder/subject, with file metadata (format, size, pages, chunks).
    """
    cfg = load_config()
    root = get_project_root()

    if mode == "custom" and workspace_id:
        corpus_dir = root / "data" / "corpus" / "custom" / workspace_id / "originals"
        metadata_path = root / "data" / "corpus" / "custom" / workspace_id / "processed" / "collection_manifest.json"
    else:
        corpus_dir = root / "data" / "corpus" / "reference"
        if not corpus_dir.exists():
            corpus_dir = root / Path(cfg["paths"].get("corpus_dir", "data/corpus/reference"))
        metadata_path = root / "data" / "processed" / "corpus_metadata.json"

    meta_lookup = {}
    if metadata_path.exists():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta_list = json.load(f)
                for item in meta_list:
                    rel = item.get("file_name", "")
                    subj = item.get("subject", "")
                    meta_lookup[f"{subj}/{rel}"] = item
                    meta_lookup[rel] = item
        except Exception as e:
            print(f"[Warning] Failed to load metadata: {e}")

    supported_exts = {".pdf", ".txt", ".md", ".docx", ".html", ".htm"}
    folders: Dict[str, List[Dict[str, Any]]] = {}
    total_docs = 0
    type_counts = {"pdf": 0, "txt": 0, "md": 0, "docx": 0, "html": 0}

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
                type_counts["pdf"] += 1
                type_label = "PDF"
            elif ext == ".md":
                type_counts["md"] += 1
                type_label = "Markdown"
            elif ext == ".docx":
                type_counts["docx"] += 1
                type_label = "DOCX"
            elif ext in [".html", ".htm"]:
                type_counts["html"] += 1
                type_label = "HTML"
            else:
                type_counts["txt"] += 1
                type_label = "Text"

            st = file_path.stat()
            size_bytes = st.st_size
            mod_time = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")

            meta = meta_lookup.get(f"{folder_name}/{file_path.name}") or meta_lookup.get(file_path.name) or {}
            total_pages = meta.get("total_pages", 1)
            total_chunks = meta.get("total_chunks", 0)
            doc_id = meta.get("document_id", f"{folder_name}_{file_path.stem}".lower())

            raw_url = f"/api/document/raw?path={rel_path}&mode={mode}"
            if workspace_id:
                raw_url += f"&workspace_id={workspace_id}"

            view_url = f"/api/document/view?path={rel_path}&mode={mode}"
            if workspace_id:
                view_url += f"&workspace_id={workspace_id}"

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
                "document_id": doc_id,
                "view_url": view_url,
                "raw_url": raw_url
            }

            if folder_name not in folders:
                folders[folder_name] = []
            folders[folder_name].append(doc_info)
            total_docs += 1

    return {
        "success": True,
        "mode": mode,
        "workspace_id": workspace_id,
        "total_documents": total_docs,
        "total_folders": len(folders),
        "summary": type_counts,
        "folders": folders
    }


@app.get("/api/document/view")
async def view_document_content(path: str, mode: str = "reference", workspace_id: Optional[str] = None):
    """
    Securely reads and returns the extracted content and page breakdown of any document.
    Supports .pdf, .docx, .html, .txt, and .md files strictly within allowed paths.
    """
    cfg = load_config()
    root = get_project_root()

    if mode == "custom" and workspace_id:
        corpus_dir = (root / "data" / "corpus" / "custom" / workspace_id / "originals").resolve()
    else:
        corpus_dir = (root / "data" / "corpus" / "reference").resolve()
        if not corpus_dir.exists():
            corpus_dir = (root / Path(cfg["paths"].get("corpus_dir", "data/corpus/reference"))).resolve()

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
                    "text": txt if txt else "[Scanned image or non-extractable page]"
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
            "raw_url": f"/api/document/raw?path={rel_path}&mode={mode}" + (f"&workspace_id={workspace_id}" if workspace_id else "")
        }

    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(str(target_file))
            full_paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            cur_p = 1
            cur_lines = []
            cur_len = 0
            for para in full_paras:
                cur_lines.append(para)
                cur_len += len(para)
                if cur_len >= 3000:
                    pages.append({"page_number": cur_p, "text": "\n\n".join(cur_lines)})
                    cur_p += 1
                    cur_lines = []
                    cur_len = 0
            if cur_lines:
                pages.append({"page_number": cur_p, "text": "\n\n".join(cur_lines)})
            if not pages:
                pages.append({"page_number": 1, "text": "\n\n".join(full_paras)})
            return {
                "success": True,
                "file_name": target_file.name,
                "folder": target_file.parent.name,
                "relative_path": rel_path,
                "extension": ext,
                "type": "DOCX",
                "size_formatted": format_file_size(file_size),
                "total_pages": len(pages),
                "pages": pages,
                "full_text": "\n\n".join(full_paras),
                "can_embed_pdf": False,
                "raw_url": f"/api/document/raw?path={rel_path}&mode={mode}"
            }
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to read DOCX: {str(e)}"})

    elif ext in [".html", ".htm"]:
        try:
            from bs4 import BeautifulSoup
            with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            for elem in soup(["script", "style", "nav", "footer", "header"]):
                elem.extract()
            text = soup.get_text(separator="\n\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cur_p = 1
            cur_lines = []
            cur_len = 0
            for l in lines:
                cur_lines.append(l)
                cur_len += len(l)
                if cur_len >= 3000:
                    pages.append({"page_number": cur_p, "text": "\n\n".join(cur_lines)})
                    cur_p += 1
                    cur_lines = []
                    cur_len = 0
            if cur_lines:
                pages.append({"page_number": cur_p, "text": "\n\n".join(cur_lines)})
            return {
                "success": True,
                "file_name": target_file.name,
                "folder": target_file.parent.name,
                "relative_path": rel_path,
                "extension": ext,
                "type": "HTML",
                "size_formatted": format_file_size(file_size),
                "total_pages": len(pages),
                "pages": pages,
                "full_text": text,
                "can_embed_pdf": False,
                "raw_url": f"/api/document/raw?path={rel_path}&mode={mode}"
            }
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to read HTML: {str(e)}"})

    elif ext in {".txt", ".md"}:
        try:
            with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

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
                "raw_url": f"/api/document/raw?path={rel_path}&mode={mode}"
            }
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to read document: {str(e)}"})

    return JSONResponse(status_code=400, content={"error": "Unsupported file format."})


@app.get("/api/document/raw")
async def get_raw_document(path: str, mode: str = "reference", workspace_id: Optional[str] = None):
    """
    Serves the raw document file directly for in-browser PDF viewing or download.
    """
    cfg = load_config()
    root = get_project_root()
    if mode == "custom" and workspace_id:
        corpus_dir = (root / "data" / "corpus" / "custom" / workspace_id / "originals").resolve()
    else:
        corpus_dir = (root / "data" / "corpus" / "reference").resolve()
        if not corpus_dir.exists():
            corpus_dir = (root / Path(cfg["paths"].get("corpus_dir", "data/corpus/reference"))).resolve()

    clean_path = path.strip().replace("\\", "/").lstrip("/")
    target_file = (corpus_dir / clean_path).resolve()

    if not str(target_file).startswith(str(corpus_dir)) or not target_file.exists() or not target_file.is_file():
        return JSONResponse(status_code=404, content={"error": "File not found or access denied."})

    ext = target_file.suffix.lower()
    media_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain; charset=utf-8",
        ".md": "text/markdown; charset=utf-8",
        ".html": "text/html; charset=utf-8",
        ".htm": "text/html; charset=utf-8",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    media_type = media_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(target_file),
        media_type=media_type,
        filename=target_file.name,
        headers={"Content-Disposition": f"inline; filename=\"{target_file.name}\""}
    )


@app.post("/api/reference/rebuild")
@app.post("/api/restore-default-corpus")
@app.post("/api/refresh-everything")
async def rebuild_reference_corpus():
    """
    Rebuilds the official 5-discipline academic Reference Corpus (Algorithms, Automata, DBMS, OS, Networks)
    from data/corpus/reference/, regenerates chunks_manifest.json (15 chunks), and builds FAISS indexes.
    """
    await terminal.broadcast("[REFERENCE] Rebuilding official academic reference corpus and indexes...")
    cfg = load_config()
    ingestor = CorpusIngestor(cfg, mode="reference")
    chunks = ingestor.ingest_corpus()
    await terminal.broadcast(f"[REFERENCE] Ingested {len(chunks)} reference chunks across 5 academic disciplines.")
    build_dual_indexes(cfg, chunks=chunks, mode="reference")
    await terminal.broadcast("[REFERENCE] Dual English & Multilingual FAISS indexes successfully rebuilt.")
    reload_orchestrator_instance()
    await terminal.broadcast("[READY] Reference benchmark indexes live and verified.")
    return {
        "success": True,
        "mode": "reference",
        "total_chunks": len(chunks),
        "message": f"Successfully rebuilt Reference Benchmark indexes ({len(chunks)} chunks)."
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
    workspace_id: Optional[str] = "reference"


@app.post("/api/query")
async def execute_query(req: QueryRequest):
    """
    Executes a cross-lingual query across Systems A, B, C, and D.
    Streams step-by-step progress to the live terminal and returns structured results.
    """
    ws_id = req.workspace_id or "reference"
    orch = get_orchestrator_instance(ws_id)
    q_hi = req.question_hi.strip()
    q_en = (req.question_en or q_hi).strip()
    qid = req.question_id or "LIVE_01"
    subj = req.subject or "general"
    cat = req.category or "general"
    s_filter = req.subject_filter or "all"

    await terminal.broadcast(f"[QUERY] [{ws_id.upper()}] Query: '{q_hi[:60]}...' (Scope Filter: {s_filter})")

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


class BenchmarkRunRequest(BaseModel):
    mode: Optional[str] = "smoke"
    limit: Optional[int] = 5
    strict: Optional[bool] = False


@app.post("/api/run-benchmark")
async def run_benchmark_command(req: Optional[BenchmarkRunRequest] = None):
    """Runs the benchmark suite (smoke or full 120 items) and streams stdout live to the terminal."""
    mode = (req.mode if req else "smoke") or "smoke"
    limit = req.limit if (req and req.limit) else (5 if mode == "smoke" else 120)
    strict = req.strict if req else False

    await terminal.broadcast(f"[BENCHMARK] Launching {mode.upper()} Suite ({limit} questions, Strict: {strict})...")
    
    bench_file = script_dir / "run_complete_experiment.py"
    cmd = [sys.executable, str(bench_file), f"--limit={limit}"]
    if strict:
        cmd.append("--strict")
    if mode == "smoke":
        cmd.append("--smoke")

    proc = subprocess.Popen(
        cmd,
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
    await terminal.broadcast(f"[BENCHMARK] Execution completed with status code {proc.returncode}.")
    return {"success": proc.returncode == 0, "exit_code": proc.returncode, "mode": mode, "limit": limit}


# ---------------------------------------------------------------------------
# Report Generation & History Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/reports/history")
async def get_reports_history():
    """
    Returns the persistent history of all benchmark runs and evaluation reports.
    """
    cfg = load_config()
    root = get_project_root()
    archive_base = root / "results" / "archive" / "runs"
    manifest_file = archive_base / "history_manifest.json"

    runs = []
    # 1. Add current active run
    latest_md = Path(cfg["paths"]["results_summary_dir"]) / "evaluation_report.md"
    latest_csv = Path(cfg["paths"]["results_csv_dir"]) / "benchmark_results.csv"
    latest_obs = Path(cfg["paths"]["results_summary_dir"]) / "complete_project_observations.json"
    latest_mtime = ""
    total_active = 0
    if latest_md.exists():
        latest_mtime = datetime.fromtimestamp(latest_md.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    if latest_obs.exists():
        try:
            with open(latest_obs, "r", encoding="utf-8") as f:
                d = json.load(f)
                total_active = d.get("total_pipeline_runs", 0)
        except Exception:
            pass

    runs.append({
        "run_id": "latest",
        "name": "Current Active Results (Latest)",
        "timestamp": latest_mtime or "Active",
        "has_markdown": latest_md.exists(),
        "has_csv": latest_csv.exists(),
        "total_runs": total_active
    })

    # 2. Add archived historical runs
    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                archived = json.load(f)
                for item in archived:
                    if item.get("run_id") != "latest":
                        runs.append(item)
        except Exception as e:
            print(f"[Warning] Failed to read history manifest: {e}")
    elif archive_base.exists():
        for p in sorted(archive_base.iterdir(), reverse=True):
            if p.is_dir() and p.name.startswith("run_"):
                runs.append({
                    "run_id": p.name,
                    "name": f"Run {p.name.replace('run_', '').replace('_', ' ').title()}",
                    "timestamp": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "has_markdown": (p / "evaluation_report.md").exists(),
                    "has_csv": (p / "benchmark_results.csv").exists(),
                    "total_runs": 0
                })

    return {"success": True, "runs": runs}


@app.get("/api/report/latest")
async def get_latest_report(run_id: str = "latest"):
    """
    Returns the scientific evaluation report in Markdown and summary metrics.
    Supports querying 'latest' or any specific historical 'run_id'.
    """
    cfg = load_config()
    root = get_project_root()

    if run_id and run_id != "latest":
        run_dir = root / "results" / "archive" / "runs" / run_id
        report_path = run_dir / "evaluation_report.md"
        csv_path = run_dir / "benchmark_results.csv"
    else:
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
        "run_id": run_id,
        "markdown": content,
        "last_updated": mtime_str,
        "has_csv": csv_path.exists(),
        "has_markdown": report_path.exists()
    }


@app.get("/api/report/download/markdown")
async def download_report_markdown(run_id: str = "latest"):
    """Downloads the evaluation_report.md file as an attachment for the specified run."""
    cfg = load_config()
    root = get_project_root()

    if run_id and run_id != "latest":
        report_path = root / "results" / "archive" / "runs" / run_id / "evaluation_report.md"
    else:
        report_path = Path(cfg["paths"]["results_summary_dir"]) / "evaluation_report.md"
        if not report_path.exists():
            harness = EvaluationHarness(cfg)
            harness.run_evaluation()

    if not report_path.exists():
        return JSONResponse(status_code=404, content={"error": f"Report not found for run: {run_id}"})
    return FileResponse(
        str(report_path),
        media_type="text/markdown",
        filename=f"evaluation_report_{run_id}.md"
    )


@app.get("/api/report/download/csv")
async def download_report_csv(run_id: str = "latest"):
    """Downloads the consolidated benchmark_results.csv as an attachment for the specified run."""
    cfg = load_config()
    root = get_project_root()

    if run_id and run_id != "latest":
        csv_path = root / "results" / "archive" / "runs" / run_id / "benchmark_results.csv"
    else:
        csv_path = Path(cfg["paths"]["results_csv_dir"]) / "benchmark_results.csv"
        if not csv_path.exists():
            harness = EvaluationHarness(cfg)
            harness.run_evaluation()

    if not csv_path.exists():
        return JSONResponse(status_code=404, content={"error": f"Benchmark CSV not found for run: {run_id}"})
    return FileResponse(
        str(csv_path),
        media_type="text/csv",
        filename=f"benchmark_results_{run_id}.csv"
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
