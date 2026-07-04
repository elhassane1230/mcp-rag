# Proposed improvements & roadmap

## 1. Neural embeddings + persisted ANN index
Wire the Voyage/OpenAI/sentence-transformers backends into a persisted FAISS or
HNSW index so retrieval scales to millions of chunks and survives restarts. The
`VectorStore` interface already isolates this change.

## 2. Re-ranking stage
Add a cross-encoder (or LLM) re-ranker over the top-N fused candidates before
generation. Cross-encoders read the query and passage jointly and typically lift
MRR/precision noticeably beyond bi-encoder + BM25.

## 3. Answer-quality evaluation (RAGAS-style)
Beyond retrieval hit@k/MRR, measure *faithfulness* (is every claim supported by a
cited chunk?), *answer relevance*, and *context precision/recall*. Automate with
an LLM judge and track regressions in CI.

## 4. Query understanding
Add query expansion / HyDE (hypothetical-document embeddings) and multi-query
retrieval for hard questions, plus a small router that skips retrieval for
chit-chat.

## 5. Richer MCP surface
Expose MCP **resources** (browse documents) and **prompts** (a "cite-your-sources"
template) in addition to tools; add an `add_document` tool with live re-indexing
so the KB is editable at runtime.

## 6. Ingestion breadth
Support PDF/HTML/Docx ingestion, semantic (embedding-based) chunking, and
metadata filters (source, date, section) so retrieval can be scoped.

## 7. Observability & guardrails
Log queries, retrieved chunk IDs and latencies; add an "insufficient context"
refusal path when top scores fall below a threshold, so the system says
"I don't know" instead of stretching weak matches.

## 8. Evaluation corpus at scale
Replace the 8-doc demo with a large real corpus (with permissive licence) and a
bigger gold set to make hit@k discriminating and stress the ANN index.
