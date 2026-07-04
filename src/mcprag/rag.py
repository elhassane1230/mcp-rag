"""The RAG engine: ties ingestion, indexing, retrieval and generation together.

    engine = RAGEngine.from_corpus("data/corpus")
    engine.answer("How do I rotate my API key?")

Backends (embeddings, generator) are chosen from config, so the same object runs
offline or in production.
"""
from __future__ import annotations

from pathlib import Path

from .config import Config, get_config
from .embeddings import get_embedder
from .generator import get_generator
from .index import VectorStore
from .ingest import ingest
from .schemas import Answer, Chunk, RetrievedChunk


class RAGEngine:
    def __init__(self, store: VectorStore, generator, cfg: Config):
        self.store = store
        self.generator = generator
        self.cfg = cfg

    @classmethod
    def from_corpus(cls, corpus_dir: str | Path | None = None,
                    cfg: Config | None = None) -> "RAGEngine":
        cfg = cfg or get_config()
        corpus_dir = corpus_dir or cfg.corpus_dir
        chunks = ingest(corpus_dir, cfg.chunk)
        embedder = get_embedder(cfg.embedding_backend, dim=cfg.embedding_dim)
        store = VectorStore(embedder).build(chunks)
        generator = get_generator(cfg.generator_backend)
        return cls(store, generator, cfg)

    # -- retrieval only -------------------------------------------------- #
    def retrieve(self, query: str, top_k: int | None = None,
                 method: str | None = None) -> list[RetrievedChunk]:
        r = self.cfg.retrieval
        return self.store.search(
            query, top_k=top_k or r.top_k, method=method or r.method,
            candidate_k=r.candidate_k, rrf_k=r.rrf_k,
        )

    # -- full RAG -------------------------------------------------------- #
    def answer(self, question: str, top_k: int | None = None,
               method: str | None = None) -> Answer:
        retrieved = self.retrieve(question, top_k=top_k, method=method)
        return self.generator.generate(question, retrieved)

    # -- introspection --------------------------------------------------- #
    @property
    def chunks(self) -> list[Chunk]:
        return self.store.chunks

    def sources(self) -> list[dict]:
        seen: dict[str, dict] = {}
        for c in self.store.chunks:
            if c.source not in seen:
                seen[c.source] = {"source": c.source, "title": c.title,
                                  "chunks": 0}
            seen[c.source]["chunks"] += 1
        return list(seen.values())

    def stats(self) -> dict:
        return {
            "documents": len(self.sources()),
            "chunks": len(self.store.chunks),
            "embedding_backend": self.cfg.embedding_backend,
            "embedding_dim": self.store.embedder.dim,
            "generator_backend": self.cfg.generator_backend,
            "retrieval_method": self.cfg.retrieval.method,
        }
