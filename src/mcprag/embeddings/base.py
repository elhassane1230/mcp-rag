"""Embedding backends.

An ``Embedder`` turns text into dense vectors. The interface is deliberately
tiny so backends are interchangeable:

    fit(corpus_texts)          # optional; only transductive backends need it
    embed_documents(texts)     # -> np.ndarray (n, dim)
    embed_query(text)          # -> np.ndarray (dim,)

* ``local`` (LSA) runs fully offline and is the default so the demo needs no
  API keys or model downloads.
* ``voyage`` / ``openai`` / ``sentence-transformers`` are production backends
  (lazy-imported) that provide stronger dense semantic embeddings.
"""
from __future__ import annotations

from typing import Protocol

import numpy as np


class Embedder(Protocol):
    dim: int

    def fit(self, corpus_texts: list[str]) -> "Embedder": ...
    def embed_documents(self, texts: list[str]) -> np.ndarray: ...
    def embed_query(self, text: str) -> np.ndarray: ...


def get_embedder(backend: str, dim: int = 256, **kwargs):
    if backend == "local":
        from .local_lsa import LSAEmbedder
        return LSAEmbedder(dim=dim)
    if backend in {"voyage", "openai", "sentence-transformers"}:
        from .neural import NeuralEmbedder
        return NeuralEmbedder(backend=backend, **kwargs)
    raise ValueError(f"Unknown embedding backend: {backend}")
