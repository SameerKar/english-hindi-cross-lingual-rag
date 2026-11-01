"""
Utility script to ingest a new PDF or rebuild vector stores after adding documents.
Usage:
    # 1. Automatic: Ingests all PDFs/text files currently in cross_lingual_rag/data/corpus/
    python cross_lingual_rag/ingest_new_pdf.py

    # 2. Or pass a path directly to a PDF:
    python cross_lingual_rag/ingest_new_pdf.py "C:/path/to/textbook.pdf" --subject "machine_learning"
"""

import sys
import shutil
import argparse
from pathlib import Path

# Add project root and cross_lingual_rag to sys.path
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from src.utils import load_config, ensure_directory
from src.ingestion import CorpusIngestor
from src.vector_store import build_dual_indexes


def main():
    parser = argparse.ArgumentParser(description="Ingest a new PDF and build dual FAISS indexes.")
    parser.add_argument("pdf_path", nargs="?", default=None, help="Path to the PDF file to add (optional).")
    parser.add_argument("--subject", default="custom", help="Subject/Topic category name (default: custom).")
    args = parser.parse_args()

    config = load_config()
    corpus_dir = Path(config["paths"]["corpus_dir"])

    if args.pdf_path:
        src_pdf = Path(args.pdf_path).resolve()
        if not src_pdf.exists():
            print(f"[Error] PDF file not found at: {src_pdf}")
            sys.exit(1)

        # Destination subject folder
        target_dir = corpus_dir / args.subject.lower().replace(" ", "_")
        ensure_directory(str(target_dir))
        dest_pdf = target_dir / src_pdf.name
        shutil.copy2(src_pdf, dest_pdf)
        print(f"[+] Copied '{src_pdf.name}' into '{target_dir}'")

    print("\n[Step 1/2] Ingesting documents & splitting into page-bounded chunks...")
    ingestor = CorpusIngestor(config)
    chunks = ingestor.ingest_corpus()

    print(f"\n[Step 2/2] Generating embeddings and building dual FAISS indexes (768d English + 384d Multilingual)...")
    build_dual_indexes(config)

    print("\n" + "=" * 70)
    print("✅ SUCCESS: Your new PDF is fully ingested and indexed!")
    print(f"Total Chunks in Vector Store: {len(chunks)}")
    print("You can now test questions against it using:")
    print("    streamlit run cross_lingual_rag/app.py")
    print("=" * 70)


if __name__ == "__main__":
    main()

