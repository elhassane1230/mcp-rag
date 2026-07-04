# Architecture

## Pipeline

```
data/corpus/*.md
   │  ingest.py — load + section-aware chunking (max_chars with overlap)
   ▼
Chunk[]  ──embed──▶  VectorStore
   │                   ├─ dense matrix (embeddings, L2-normalised)
   │                   └─ BM25 index (tokenised text)
   ▼
query ─▶ retriever (semantic | lexical | hybrid-RRF) ─▶ RetrievedChunk[]
   ▼
generator (extractive | anthropic | openai) ─▶ Answer + Citation[]
   ▼
server.py (FastMCP) ─▶ tools over stdio ─▶ MCP client
```

## Why these choices

### Hybrid retrieval (dense + sparse, fused with RRF)
Dense (semantic) retrieval matches meaning — it handles paraphrases and
synonyms that keyword search misses. Sparse (BM25) retrieval nails exact terms,
identifiers and rare tokens that embeddings can blur. **Reciprocal Rank Fusion**
combines their ranked lists with `score = Σ 1/(k+rank)` — no weights to tune,
and empirically robust. The evaluation shows hybrid matching or beating either
method alone on MRR.

### Offline-first, backend-agnostic
The `Embedder` and generator are small Protocols. The default **local LSA**
embedder (TF-IDF + Truncated SVD) gives genuine semantic matching with no
network or model download, so the repo runs and its tests pass anywhere. Swapping
to a neural encoder (Voyage/OpenAI/sentence-transformers) or an LLM generator is
a config/env change; **retrieval and serving code are untouched**.

### Grounded generation
The offline `ExtractiveGenerator` selects the retrieved sentences most relevant
to the question and stitches them together with citation markers. Because every
sentence is copied verbatim from a source chunk, the answer **cannot
hallucinate** and is always attributable — a safe default and a clean baseline
for the LLM generators, which are prompted to answer *only* from the provided
context and cite it.

### MCP integration
`server.py` uses **FastMCP** to expose the engine's methods as MCP tools over
stdio. This is the natural deployment for RAG: instead of a bespoke API, the
knowledge base becomes a tool any MCP-capable model can call, with typed
arguments and structured results. The engine is built once at startup and cached.

## Data contracts
`Document → Chunk → RetrievedChunk → Answer/Citation` (all pydantic). Typed
boundaries keep ingestion, retrieval, generation and the MCP layer decoupled and
independently testable.

## Scaling notes
For this corpus an exact numpy cosine search is instant. At larger scale, swap
the dense search for an ANN index (FAISS/HNSW) and persist the index; the
`VectorStore` interface stays the same. Chunking, RRF and the MCP surface are
size-independent.
