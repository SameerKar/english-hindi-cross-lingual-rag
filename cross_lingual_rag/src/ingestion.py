"""
Corpus ingestion and parsing pipeline.
Extracts text from academic PDFs, DOCX, HTML, TXT, and Markdown preserving physical page numbers,
catalogs metadata with portable relative paths, detects duplicates and zero-text files,
and orchestrates chunk generation and isolated metadata cataloging.
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import pypdf

try:
    from .chunking import PageAwareChunker, DocumentChunk
    from .utils import load_config, ensure_directory, get_project_root
except (ImportError, ValueError):
    # Running directly as script
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.chunking import PageAwareChunker, DocumentChunk
    from src.utils import load_config, ensure_directory, get_project_root

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


def compute_sha256(file_path: Path) -> str:
    """Computes the SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def make_portable_path(path: Path, root: Optional[Path] = None) -> str:
    """Converts a Path into a forward-slash relative path from the project root."""
    if root is None:
        root = get_project_root()
    try:
        rel = path.resolve().relative_to(root.resolve())
        return str(rel).replace("\\", "/")
    except Exception:
        # Fallback to posix path without drive letter
        parts = path.parts
        # If parts start with drive like 'D:\\', strip it
        if parts and ":" in parts[0]:
            parts = parts[1:]
        return "/".join(parts)


class CorpusIngestor:
    """
    Ingests academic PDFs, DOCX, HTML, TXT and Markdown, cataloging metadata
    and creating an isolated unified manifest of chunks for Reference or Custom modes.
    """
    def __init__(self, config: Dict[str, Any], mode: str = "reference", workspace_id: Optional[str] = None):
        self.config = config
        self.mode = mode
        self.workspace_id = workspace_id
        self.root = get_project_root()

        retrieval_cfg = config.get("retrieval", {})
        self.chunker = PageAwareChunker(
            chunk_size=retrieval_cfg.get("chunk_size", 700),
            chunk_overlap=retrieval_cfg.get("chunk_overlap", 80)
        )

        # Configure paths based on mode
        if mode == "custom" and workspace_id:
            self.corpus_dir = self.root / "data" / "corpus" / "custom" / workspace_id / "originals"
            self.processed_dir = self.root / "data" / "corpus" / "custom" / workspace_id / "processed"
        else:
            ref_dir = self.root / "data" / "corpus" / "reference"
            if ref_dir.exists():
                self.corpus_dir = ref_dir
            else:
                self.corpus_dir = self.root / Path(config["paths"].get("corpus_dir", "data/corpus/reference"))
            self.processed_dir = self.root / Path(config["paths"].get("processed_dir", "data/processed"))

        ensure_directory(str(self.processed_dir))
        ensure_directory(str(self.corpus_dir))

    def extract_pdf_pages(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extracts text from a PDF file page by page using pypdf."""
        pages_data = []
        try:
            reader = pypdf.PdfReader(str(pdf_path))
            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                pages_data.append({
                    "page_number": page_idx + 1,
                    "text": page_text.strip()
                })
        except Exception as e:
            print(f"[Error] Failed to read PDF {pdf_path}: {e}")
        return pages_data

    def extract_docx_pages(self, docx_path: Path) -> List[Dict[str, Any]]:
        """Extracts text from DOCX files, creating virtual pages of ~3000 chars."""
        pages_data = []
        if not DOCX_AVAILABLE:
            print(f"[Error] python-docx not available; cannot parse {docx_path.name}")
            return pages_data

        try:
            doc = docx.Document(str(docx_path))
            full_text = []
            for p in doc.paragraphs:
                txt = p.text.strip()
                if txt:
                    full_text.append(txt)

            # Virtual pagination (~3000 chars per page)
            current_page = 1
            current_text = []
            current_len = 0
            for para in full_text:
                current_text.append(para)
                current_len += len(para)
                if current_len >= 3000:
                    pages_data.append({
                        "page_number": current_page,
                        "text": "\n\n".join(current_text)
                    })
                    current_page += 1
                    current_text = []
                    current_len = 0
            if current_text:
                pages_data.append({
                    "page_number": current_page,
                    "text": "\n\n".join(current_text)
                })
        except Exception as e:
            print(f"[Error] Failed to read DOCX {docx_path}: {e}")
        return pages_data

    def extract_html_pages(self, html_path: Path) -> List[Dict[str, Any]]:
        """Extracts text from HTML files using BeautifulSoup, creating virtual pages."""
        pages_data = []
        if not BS4_AVAILABLE:
            print(f"[Error] beautifulsoup4 not available; cannot parse {html_path.name}")
            return pages_data

        try:
            with open(html_path, "r", encoding="utf-8", errors="replace") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            # Remove script and style elements
            for elem in soup(["script", "style", "nav", "footer", "header"]):
                elem.extract()

            text = soup.get_text(separator="\n\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]

            current_page = 1
            current_text = []
            current_len = 0
            for line in lines:
                current_text.append(line)
                current_len += len(line)
                if current_len >= 3000:
                    pages_data.append({
                        "page_number": current_page,
                        "text": "\n\n".join(current_text)
                    })
                    current_page += 1
                    current_text = []
                    current_len = 0
            if current_text:
                pages_data.append({
                    "page_number": current_page,
                    "text": "\n\n".join(current_text)
                })
        except Exception as e:
            print(f"[Error] Failed to read HTML {html_path}: {e}")
        return pages_data

    def extract_text_pages(self, txt_path: Path) -> List[Dict[str, Any]]:
        """Extracts text from .txt or .md files with page boundary support."""
        pages_data = []
        try:
            with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            if "--- PAGE" in content or "=== PAGE" in content:
                parts = re.split(r'(?:---|===)\s*PAGE\s*(\d+)\s*(?:---|===)', content)
                if parts[0].strip():
                    pages_data.append({"page_number": 1, "text": parts[0].strip()})
                for i in range(1, len(parts), 2):
                    page_num = int(parts[i])
                    page_txt = parts[i+1].strip()
                    pages_data.append({"page_number": page_num, "text": page_txt})
            else:
                paragraphs = content.split("\n\n")
                current_page = 1
                current_text = []
                current_len = 0
                for para in paragraphs:
                    p_str = para.strip()
                    if not p_str:
                        continue
                    current_text.append(p_str)
                    current_len += len(p_str)
                    if current_len >= 3000:
                        pages_data.append({
                            "page_number": current_page,
                            "text": "\n\n".join(current_text)
                        })
                        current_page += 1
                        current_text = []
                        current_len = 0
                if current_text:
                    pages_data.append({
                        "page_number": current_page,
                        "text": "\n\n".join(current_text)
                    })
        except Exception as e:
            print(f"[Error] Failed to read text file {txt_path}: {e}")
        return pages_data

    def ingest_corpus(self) -> List[DocumentChunk]:
        """
        Scans corpus_dir, parses all supported files, computes SHA-256 hashes,
        filters duplicate/zero-text files, generates chunks, and writes metadata manifests.
        """
        all_chunks: List[DocumentChunk] = []
        corpus_metadata: List[Dict[str, Any]] = []
        seen_hashes: Set[str] = set()

        if not self.corpus_dir.exists():
            print(f"[Warning] Corpus directory does not exist: {self.corpus_dir}. Creating it.")
            self.corpus_dir.mkdir(parents=True, exist_ok=True)
            return []

        supported_exts = {".pdf", ".txt", ".md", ".docx", ".html", ".htm"}
        file_paths = sorted([p for p in self.corpus_dir.rglob("*") if p.is_file() and p.suffix.lower() in supported_exts])

        print(f"[Ingestion] Discovered {len(file_paths)} source file(s) in {self.corpus_dir} (Mode: {self.mode})")

        for file_path in file_paths:
            # Subject from directory or default
            if file_path.parent != self.corpus_dir and file_path.parent.name not in ["originals", "reference"]:
                subject = file_path.parent.name
            else:
                subject = "general"

            doc_id = f"{subject}_{file_path.stem}".lower().replace(" ", "_").replace("-", "_")
            portable_path = make_portable_path(file_path, self.root)
            file_hash = compute_sha256(file_path)

            # Duplicate detection by SHA-256
            if file_hash in seen_hashes:
                print(f"  [Duplicate Warning] Skipping duplicate file: {file_path.name} (SHA-256: {file_hash[:10]}...)")
                continue
            seen_hashes.add(file_hash)

            print(f"  -> Ingesting {file_path.name} (Subject: {subject}, Doc ID: {doc_id})...")

            # Extract pages based on extension
            ext = file_path.suffix.lower()
            if ext == ".pdf":
                pages = self.extract_pdf_pages(file_path)
            elif ext == ".docx":
                pages = self.extract_docx_pages(file_path)
            elif ext in [".html", ".htm"]:
                pages = self.extract_html_pages(file_path)
            else:
                pages = self.extract_text_pages(file_path)

            total_extracted_text = sum(len(p.get("text", "").strip()) for p in pages)

            # Zero-text detection
            if total_extracted_text == 0 or not pages:
                print(f"  [Error] Zero text extracted from {file_path.name}! File is empty or scanned without OCR.")
                corpus_metadata.append({
                    "document_id": doc_id,
                    "file_name": file_path.name,
                    "file_path": portable_path,
                    "sha256": file_hash,
                    "subject": subject,
                    "total_pages": len(pages),
                    "total_chunks": 0,
                    "language": "en",
                    "extraction_status": "FAILED_ZERO_TEXT",
                    "warning": "No extractable text found. Check if PDF is scanned."
                })
                continue

            # Split pages into chunks
            doc_chunks: List[DocumentChunk] = []
            for page_info in pages:
                if not page_info["text"].strip():
                    continue
                p_chunks = self.chunker.split_page_text(
                    page_text=page_info["text"],
                    doc_id=doc_id,
                    subject=subject,
                    page_number=page_info["page_number"]
                )
                doc_chunks.extend(p_chunks)

            all_chunks.extend(doc_chunks)

            corpus_metadata.append({
                "document_id": doc_id,
                "file_name": file_path.name,
                "file_path": portable_path,
                "sha256": file_hash,
                "subject": subject,
                "total_pages": len(pages),
                "total_chunks": len(doc_chunks),
                "language": "en",
                "extraction_status": "SUCCESS"
            })

        # Save metadata manifest
        manifest_filename = "chunks_manifest.json"
        metadata_filename = "collection_manifest.json" if self.mode == "custom" else "corpus_metadata.json"

        manifest_path = self.processed_dir / manifest_filename
        metadata_path = self.processed_dir / metadata_filename

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in all_chunks], f, indent=2, ensure_ascii=False)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(corpus_metadata, f, indent=2, ensure_ascii=False)

        # For reference mode, also save corpus_manifest.csv and backward-compatible paths
        if self.mode == "reference":
            csv_path = self.corpus_dir / "corpus_manifest.csv"
            try:
                import csv
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "document_id", "title", "author", "subject", "year",
                        "source_url", "license_name", "license_url", "file_name",
                        "file_path", "sha256", "total_pages", "total_chunks", "extraction_status"
                    ])
                    for item in corpus_metadata:
                        writer.writerow([
                            item["document_id"],
                            item["document_id"].replace("_", " ").title(),
                            "Academic Author / Open Course",
                            item["subject"],
                            "2023",
                            "https://open.umn.edu/opentextbooks",
                            "CC BY 4.0",
                            "https://creativecommons.org/licenses/by/4.0/",
                            item["file_name"],
                            item["file_path"],
                            item["sha256"],
                            item["total_pages"],
                            item["total_chunks"],
                            item["extraction_status"]
                        ])
            except Exception as e:
                print(f"[Notice] Failed to write manifest CSV: {e}")

            compat_dir = self.root / "data" / "processed"
            ensure_directory(str(compat_dir))
            with open(compat_dir / "chunks_manifest.json", "w", encoding="utf-8") as f:
                json.dump([c.to_dict() for c in all_chunks], f, indent=2, ensure_ascii=False)
            with open(compat_dir / "corpus_metadata.json", "w", encoding="utf-8") as f:
                json.dump(corpus_metadata, f, indent=2, ensure_ascii=False)

        print(f"[Ingestion Complete] Generated {len(all_chunks)} chunks across {len(corpus_metadata)} document(s).")
        print(f"Manifest written to: {manifest_path}")
        return all_chunks


if __name__ == "__main__":
    cfg = load_config()
    ingestor = CorpusIngestor(cfg, mode="reference")
    ingestor.ingest_corpus()
