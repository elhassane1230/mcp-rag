"""Index over the chunks supporting three retrieval modes.

* semantic  — cosine similarity over embedding vectors (numpy; for corpora of
              this size an exact search is instant, no FAISS needed).
* lexical   — Okapi BM25 over tokenised text (rank_bm25).
* hybrid    — Reciprocal Rank Fusion (RRF) of the two ranked lists, which is a
              strong, tuning-free way to combine dense and sparse retrieval and
              usually beats either alone.

The ablation in ``scripts/run_eval.py`` compares all three.
"""
from __future__ import annotations

import re

import numpy as np
from rank_bm25 import BM25Okapi

from ..schemas import Chunk, RetrievedChunk

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class VectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.chunks: list[Chunk] = []
        self._matrix: np.ndarray | None = None   # (n, dim), L2-normalised
        self._bm25: BM25Okapi | None = None

    def build(self, chunks: list[Chunk]) -> "VectorStore":
        self.chunks = chunks
        texts = [c.text for c in chunks]
        self.embedder.fit(texts)
        self._matrix = self.embedder.embed_documents(texts)
        self._bm25 = BM25Okapi([_tokenize(t) for t in texts])
        return self

    # -- individual retrievers ------------------------------------------- #
    def _semantic(self, query: str, k: int) -> list[tuple[int, float]]:
        q = self.embedder.embed_query(query)
        sims = self._matrix @ q                      # cosine (both normalised)
        idx = np.argsort(-sims)[:k]
        return [(int(i), float(sims[i])) for i in idx]

    def _lexical(self, query: str, k: int) -> list[tuple[int, float]]:
        scores = self._bm25.get_scores(_tokenize(query))
        idx = np.argsort(-scores)[:k]
        return [(int(i), float(scores[i])) for i in idx]

    @staticmethod
    def _rrf(rank_lists: list[list[int]], k_const: int = 60) -> dict[int, float]:
        """Reciprocal Rank Fusion: score = Σ 1/(k + rank)."""
        fused: dict[int, float] = {}
        for ranks in rank_lists:
            for rank, idx in enumerate(ranks):
                fused[idx] = fused.get(idx, 0.0) + 1.0 / (k_const + rank)
        return fused

    # -- public API ------------------------------------------------------ #
    def search(self, query: str, top_k: int = 4, method: str = "hybrid",
               candidate_k: int = 20, rrf_k: int = 60) -> list[RetrievedChunk]:
        if self._matrix is None:
            raise RuntimeError("Call build() first.")

        if method == "semantic":
            hits = self._semantic(query, top_k)
        elif method == "lexical":
            hits = self._lexical(query, top_k)
        elif method == "hybrid":
            sem = self._semantic(query, candidate_k)
            lex = self._lexical(query, candidate_k)
            fused = self._rrf([[i for i, _ in sem], [i for i, _ in lex]], rrf_k)
            ranked = sorted(fused.items(), key=lambda kv: -kv[1])[:top_k]
            hits = ranked
        else:
            raise ValueError(f"Unknown method: {method}")

        return [RetrievedChunk(chunk=self.chunks[i], score=s, method=method)
                for i, s in hits]
