"""
Page-aware text chunking with deterministic stable identifier generation.
Enforces page boundaries so that every retrieved chunk maps precisely to a physical document page.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import re

@dataclass
class DocumentChunk:
    chunk_id: str          # Format: {doc_id}_p{page}_c{chunk_index}
    doc_id: str            # Identifier for document (e.g. algo_clrs)
    subject: str           # Subject category (e.g. algorithms, dbms)
    page: int              # Physical 1-indexed page number
    chunk_index: int       # 0-indexed chunk within the page
    text: str              # Cleaned text content
    token_count: int       # Estimated token count
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentChunk":
        return cls(**data)


class PageAwareChunker:
    """
    Splits text on a per-page basis to strictly preserve physical page references.
    """
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def estimate_tokens(self, text: str) -> int:
        """
        Estimates token count (~1.3 tokens per whitespace-separated word in English technical text).
        """
        words = text.split()
        return max(1, int(len(words) * 1.3))

    def split_page_text(self, page_text: str, doc_id: str, subject: str, page_number: int) -> List[DocumentChunk]:
        """
        Splits text from a single physical page into stable, bounded chunks.
        """
        clean_text = self._clean_text(page_text)
        if not clean_text or len(clean_text.strip()) < 20:
            return []

        # Break text into paragraphs first
        paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
        
        chunks: List[str] = []
        current_chunk_words: List[str] = []
        current_tokens = 0

        # Target token size in words (1 token ~ 0.75 words)
        target_words = int(self.chunk_size / 1.3)
        overlap_words = int(self.chunk_overlap / 1.3)

        for para in paragraphs:
            para_words = para.split()
            para_tokens = self.estimate_tokens(para)

            if current_tokens + para_tokens <= self.chunk_size:
                current_chunk_words.extend(para_words)
                current_tokens += para_tokens
            else:
                # If paragraph itself is larger than chunk_size, split by sentences
                if para_tokens > self.chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        sent_words = sent.split()
                        sent_tokens = self.estimate_tokens(sent)
                        if current_tokens + sent_tokens <= self.chunk_size:
                            current_chunk_words.extend(sent_words)
                            current_tokens += sent_tokens
                        else:
                            if current_chunk_words:
                                chunks.append(" ".join(current_chunk_words))
                                # Retain overlap
                                current_chunk_words = current_chunk_words[-overlap_words:] if len(current_chunk_words) > overlap_words else []
                                current_tokens = self.estimate_tokens(" ".join(current_chunk_words))
                            current_chunk_words.extend(sent_words)
                            current_tokens += sent_tokens
                else:
                    if current_chunk_words:
                        chunks.append(" ".join(current_chunk_words))
                        current_chunk_words = current_chunk_words[-overlap_words:] if len(current_chunk_words) > overlap_words else []
                        current_tokens = self.estimate_tokens(" ".join(current_chunk_words))
                    current_chunk_words.extend(para_words)
                    current_tokens += para_tokens

        if current_chunk_words:
            chunks.append(" ".join(current_chunk_words))

        # Generate DocumentChunk objects with stable IDs
        document_chunks: List[DocumentChunk] = []
        for idx, chunk_str in enumerate(chunks):
            chunk_str = chunk_str.strip()
            if not chunk_str:
                continue
            stable_id = f"{doc_id}_p{page_number}_c{idx}"
            chunk_obj = DocumentChunk(
                chunk_id=stable_id,
                doc_id=doc_id,
                subject=subject,
                page=page_number,
                chunk_index=idx,
                text=chunk_str,
                token_count=self.estimate_tokens(chunk_str),
                metadata={
                    "doc_id": doc_id,
                    "subject": subject,
                    "page": page_number,
                    "chunk_index": idx
                }
            )
            document_chunks.append(chunk_obj)

        return document_chunks

    def _clean_text(self, text: str) -> str:
        """
        Cleans common PDF extraction artifacts without altering mathematical or semantic content.
        """
        # Fix hyphenated words at line breaks (e.g. "algo-\nrithm" -> "algorithm")
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        # Normalize excessive carriage returns
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Replace non-breaking spaces
        text = text.replace('\xa0', ' ')
        # Normalize excessive intra-line whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
