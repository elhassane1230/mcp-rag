"""Configuration. Backends are selected here and overridable via env vars
(prefix ``MCPRAG_``), so the same code runs offline (local embeddings +
extractive answers) or in production (neural embeddings + an LLM)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class ChunkConfig:
    max_chars: int = 700           # target chunk size
    overlap: int = 120             # overlap between consecutive chunks


@dataclass
class RetrievalConfig:
    top_k: int = 4                 # chunks returned to the generator
    candidate_k: int = 20          # candidates fetched from each retriever
    method: str = "hybrid"         # semantic | lexical | hybrid
    rrf_k: int = 60                # reciprocal-rank-fusion constant


@dataclass
class Config:
    corpus_dir: Path = ROOT / "data" / "corpus"
    embedding_backend: str = os.getenv("MCPRAG_EMBEDDING_BACKEND", "local")   # local|voyage|openai|sentence-transformers
    generator_backend: str = os.getenv("MCPRAG_GENERATOR_BACKEND", "extractive")  # extractive|anthropic|openai
    embedding_dim: int = 256       # for the local LSA embedder
    chunk: ChunkConfig = field(default_factory=ChunkConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    seed: int = 42


def get_config() -> Config:
    return Config()
