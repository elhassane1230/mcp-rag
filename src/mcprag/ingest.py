"""Ingestion: load documents and split them into overlapping chunks.

Chunking strategy: split on markdown headings first (so a chunk stays within one
logical section), then pack paragraphs up to ``max_chars`` with a character
overlap between consecutive chunks so context isn't lost at boundaries.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .config import ChunkConfig
from .schemas import Chunk, Document


def _doc_id(source: str) -> str:
    return hashlib.sha1(source.encode()).hexdigest()[:10]


def load_documents(corpus_dir: str | Path) -> list[Document]:
    corpus_dir = Path(corpus_dir)
    docs: list[Document] = []
    for path in sorted(corpus_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = m.group(1).strip() if m else path.stem
        docs.append(Document(doc_id=_doc_id(path.name), source=path.name,
                             title=title, text=text))
    return docs


def _split_sections(text: str) -> list[str]:
    """Split on markdown H2/H3 headings, keeping the heading with its body."""
    parts = re.split(r"(?m)^(#{2,3}\s+.+)$", text)
    if len(parts) <= 1:
        return [text.strip()]
    sections, buf = [], parts[0].strip()
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        if buf:
            sections.append(buf)
            buf = ""
        sections.append((heading + "\n" + body).strip())
    return [s for s in sections if s]


def _pack(section: str, cfg: ChunkConfig) -> list[str]:
    """Pack a section into <=max_chars windows with character overlap."""
    if len(section) <= cfg.max_chars:
        return [section]
    chunks, start = [], 0
    while start < len(section):
        end = start + cfg.max_chars
        # try to break on a paragraph/sentence boundary near the window end
        window = section[start:end]
        brk = max(window.rfind("\n\n"), window.rfind(". "))
        if brk > cfg.max_chars * 0.5:
            end = start + brk + 1
        chunks.append(section[start:end].strip())
        if end >= len(section):
            break
        start = max(end - cfg.overlap, start + 1)
    return [c for c in chunks if c]


def chunk_document(doc: Document, cfg: ChunkConfig | None = None) -> list[Chunk]:
    cfg = cfg or ChunkConfig()
    chunks: list[Chunk] = []
    pos = 0
    for section in _split_sections(doc.text):
        for piece in _pack(section, cfg):
            chunks.append(Chunk(
                chunk_id=f"{doc.doc_id}:{pos}",
                doc_id=doc.doc_id, source=doc.source, title=doc.title,
                text=piece, position=pos,
            ))
            pos += 1
    return chunks


def ingest(corpus_dir: str | Path, cfg: ChunkConfig | None = None) -> list[Chunk]:
    """Load and chunk every document in the corpus directory."""
    chunks: list[Chunk] = []
    for doc in load_documents(corpus_dir):
        chunks.extend(chunk_document(doc, cfg))
    return chunks
