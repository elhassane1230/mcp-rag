"""Typed data contracts shared across the RAG pipeline."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Document(BaseModel):
    """A source document before chunking."""
    doc_id: str
    source: str                       # filename / URI
    title: str
    text: str
    metadata: dict = Field(default_factory=dict)


class Chunk(BaseModel):
    """A retrievable passage derived from a document."""
    chunk_id: str
    doc_id: str
    source: str
    title: str
    text: str
    position: int                     # ordinal within the document
    metadata: dict = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """A chunk returned by the retriever with its relevance score."""
    chunk: Chunk
    score: float
    method: str = "hybrid"            # semantic | lexical | hybrid


class Citation(BaseModel):
    marker: str                       # e.g. "[1]"
    source: str
    title: str
    chunk_id: str


class Answer(BaseModel):
    """A grounded answer with the citations it was built from."""
    question: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    retrieved: list[RetrievedChunk] = Field(default_factory=list)
    generator: str = "extractive"
