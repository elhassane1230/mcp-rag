"""Offline semantic embeddings via Latent Semantic Analysis (LSA).

TF-IDF over word 1-2 grams, reduced with Truncated SVD. LSA projects terms and
documents into a shared latent space where synonymous/related terms end up
close, giving genuine (if classical) semantic matching — no network, no model
download, so the demo runs anywhere. Vectors are L2-normalised so a dot product
equals cosine similarity.

Production deployments should swap in a dense neural encoder (see
``neural.py``); the retriever code is identical either way.
"""
from __future__ import annotations

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


class LSAEmbedder:
    def __init__(self, dim: int = 256):
        self.dim = dim
        self.vectorizer = TfidfVectorizer(
            lowercase=True, stop_words="english", ngram_range=(1, 2),
            sublinear_tf=True, min_df=1,
        )
        self.svd: TruncatedSVD | None = None
        self._fitted = False

    def fit(self, corpus_texts: list[str]) -> "LSAEmbedder":
        tfidf = self.vectorizer.fit_transform(corpus_texts)
        n_components = min(self.dim, tfidf.shape[1] - 1, len(corpus_texts) - 1)
        n_components = max(2, n_components)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.svd.fit(tfidf)
        self.dim = n_components
        self._fitted = True
        return self

    def _transform(self, texts: list[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Call fit() before embedding.")
        tfidf = self.vectorizer.transform(texts)
        vecs = self.svd.transform(tfidf)
        return normalize(vecs).astype("float32")

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return self._transform(texts)

    def embed_query(self, text: str) -> np.ndarray:
        return self._transform([text])[0]
