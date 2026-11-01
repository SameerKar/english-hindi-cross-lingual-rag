"""
Corpus ingestion and parsing pipeline.
Extracts text from academic PDFs preserving physical page numbers, cleans artifacts,
and orchestrates chunk generation and metadata cataloging.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pypdf

from .chunking import PageAwareChunker, DocumentChunk
from .utils import load_config, ensure_directory, get_project_root

class CorpusIngestor:
    """
    Ingests academic PDFs and text notes, cataloging metadata and creating a unified manifest of chunks.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.corpus_dir = Path(config["paths"]["corpus_dir"])
        self.processed_dir = Path(config["paths"]["processed_dir"])
        ensure_directory(str(self.processed_dir))

        retrieval_cfg = config.get("retrieval", {})
        self.chunker = PageAwareChunker(
            chunk_size=retrieval_cfg.get("chunk_size", 700),
            chunk_overlap=retrieval_cfg.get("chunk_overlap", 80)
        )

    def extract_pdf_pages(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts text from a PDF file page by page using pypdf.
        """
        pages_data = []
        try:
            reader = pypdf.PdfReader(str(pdf_path))
            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                pages_data.append({
                    "page_number": page_idx + 1,
                    "text": page_text
                })
        except Exception as e:
            print(f"[Error] Failed to read PDF {pdf_path}: {e}")
        return pages_data

    def extract_text_pages(self, txt_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts text from .txt or .md files. If page separator '--- PAGE X ---' is present,
        splits accordingly; otherwise treats each ~500 words or entire file as page 1.
        """
        pages_data = []
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "--- PAGE" in content or "=== PAGE" in content:
                # Custom page delimiter support
                import re
                parts = re.split(r'(?:---|===)\s*PAGE\s*(\d+)\s*(?:---|===)', content)
                # First element before any marker
                if parts[0].strip():
                    pages_data.append({"page_number": 1, "text": parts[0].strip()})
                for i in range(1, len(parts), 2):
                    page_num = int(parts[i])
                    page_txt = parts[i+1].strip()
                    pages_data.append({"page_number": page_num, "text": page_txt})
            else:
                # Split large text files into virtual pages of ~3500 chars (approx 1 textbook page)
                paragraphs = content.split("\n\n")
                current_page = 1
                current_text = []
                current_len = 0
                for para in paragraphs:
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
            print(f"[Error] Failed to read text file {txt_path}: {e}")
        return pages_data

    def ingest_corpus(self) -> List[DocumentChunk]:
        """
        Scans data/corpus/ directories, extracts text preserving page numbers,
        generates chunks, and writes chunks_manifest.json and corpus_metadata.json.
        """
        all_chunks: List[DocumentChunk] = []
        corpus_metadata: List[Dict[str, Any]] = []

        if not self.corpus_dir.exists():
            print(f"[Warning] Corpus directory does not exist: {self.corpus_dir}. Creating it.")
            self.corpus_dir.mkdir(parents=True, exist_ok=True)
            return []

        # Walk through subject subfolders or root of corpus_dir
        supported_exts = {".pdf", ".txt", ".md"}
        file_paths = [p for p in self.corpus_dir.rglob("*") if p.suffix.lower() in supported_exts]

        print(f"[Ingestion] Discovered {len(file_paths)} academic source files in {self.corpus_dir}")

        for file_path in file_paths:
            # Determine subject from parent folder name or default
            subject = file_path.parent.name if file_path.parent != self.corpus_dir else "general"
            doc_id = f"{subject}_{file_path.stem}".lower().replace(" ", "_").replace("-", "_")

            print(f"  -> Ingesting {file_path.name} (Subject: {subject}, Doc ID: {doc_id})...")

            if file_path.suffix.lower() == ".pdf":
                pages = self.extract_pdf_pages(file_path)
            else:
                pages = self.extract_text_pages(file_path)

            doc_chunks: List[DocumentChunk] = []
            for page_info in pages:
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
                "file_path": str(file_path),
                "subject": subject,
                "total_pages": len(pages),
                "total_chunks": len(doc_chunks),
                "language": "en"
            })

        # Save metadata manifest
        manifest_path = self.processed_dir / "chunks_manifest.json"
        metadata_path = self.processed_dir / "corpus_metadata.json"

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in all_chunks], f, indent=2, ensure_ascii=False)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(corpus_metadata, f, indent=2, ensure_ascii=False)

        print(f"[Ingestion Complete] Generated {len(all_chunks)} chunks across {len(corpus_metadata)} documents.")
        print(f"Manifest written to: {manifest_path}")
        return all_chunks

if __name__ == "__main__":
    cfg = load_config()
    ingestor = CorpusIngestor(cfg)
    ingestor.ingest_corpus()
