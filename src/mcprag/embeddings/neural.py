"""Production neural embedding backends (lazy-imported).

Each requires network access and/or an API key, so they are never imported
unless selected. They expose the same interface as the local LSA embedder, so
switching is a one-line config change (``MCPRAG_EMBEDDING_BACKEND``).

  * voyage                 — Voyage AI (Anthropic's recommended embeddings)
  * openai                 — OpenAI text-embedding-3
  * sentence-transformers  — local open-source encoders (e.g. all-MiniLM-L6-v2)
"""
from __future__ import annotations

import os

import numpy as np


class NeuralEmbedder:
    def __init__(self, backend: str, model: str | None = None):
        self.backend = backend
        self.model = model or _DEFAULT_MODELS[backend]
        self.dim = _DIMS.get(self.model, 1024)
        self._client = None

    # Neural encoders are not transductive; fit is a no-op.
    def fit(self, corpus_texts: list[str]) -> "NeuralEmbedder":
        return self

    def _encode(self, texts: list[str]) -> np.ndarray:
        if self.backend == "voyage":
            import voyageai
            client = self._client or voyageai.Client(
                api_key=os.environ["VOYAGE_API_KEY"])
            self._client = client
            res = client.embed(texts, model=self.model, input_type="document")
            return np.asarray(res.embeddings, dtype="float32")

        if self.backend == "openai":
            from openai import OpenAI
            client = self._client or OpenAI()
            self._client = client
            res = client.embeddings.create(model=self.model, input=texts)
            return np.asarray([d.embedding for d in res.data], dtype="float32")

        if self.backend == "sentence-transformers":
            from sentence_transformers import SentenceTransformer
            model = self._client or SentenceTransformer(self.model)
            self._client = model
            return np.asarray(
                model.encode(texts, normalize_embeddings=True), dtype="float32")

        raise ValueError(self.backend)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        vecs = self._encode(texts)
        self.dim = vecs.shape[1]
        return vecs

    def embed_query(self, text: str) -> np.ndarray:
        return self._encode([text])[0]


_DEFAULT_MODELS = {
    "voyage": "voyage-3",
    "openai": "text-embedding-3-small",
    "sentence-transformers": "sentence-transformers/all-MiniLM-L6-v2",
}
_DIMS = {
    "voyage-3": 1024,
    "text-embedding-3-small": 1536,
    "sentence-transformers/all-MiniLM-L6-v2": 384,
}
