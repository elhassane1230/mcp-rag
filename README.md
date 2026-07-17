# mcp-rag: Semantic RAG served over the Model Context Protocol

A **semantic Retrieval-Augmented Generation** engine, exposed as an **MCP
server** so any MCP client (Claude Desktop, an IDE agent, …) can search and
question a knowledge base as a native tool.

```
 documents ─▶ chunk ─▶ embed ─▶ index ─┐
                                        ├─▶ hybrid retrieval ─▶ grounded answer
 query ─────────────────────────────────┘   (semantic + BM25,     with citations
                                              fused by RRF)              │
                                                                         ▼
                                                    MCP server ─▶ any MCP client
```

The whole thing **runs offline out of the box**, local LSA embeddings + an
extractive, citation-grounded answerer, with **zero API keys or model
downloads**. Production backends (Voyage / OpenAI / sentence-transformers for
embeddings, Anthropic / OpenAI for generation) are a one-line config switch.

**Demo corpus:** a self-contained fictional SaaS knowledge base ("Nimbus", a
cloud data platform): authentication, billing, rate limits, data retention,
security, incident runbook, webhooks, SDK. Nothing copyrighted; every answer is
traceable to a source.

---

## What it does

Ask a question phrased in your own words and get an answer grounded in the docs:

```
$ python scripts/demo_query.py "what happens if I go over my included usage?"

A: When you exceed your included quota, Nimbus does not cut off your service;
   instead, additional usage is billed as overage at the metered rate
   ($0.50 per extra 10k calls, $0.10 per extra GB). [1]
Sources:
   [1] billing.md, Billing and quotas
```

Note there's **no keyword overlap** between "go over my included usage" and
"exceed your quota / overage", that match is *semantic*, which is the point.

---

## MCP tools exposed

| Tool | Purpose |
|------|---------|
| `search_documents(query, top_k, method)` | Return the most relevant passages (`semantic` / `lexical` / `hybrid`). |
| `answer_question(question, top_k)` | A grounded answer with citations. |
| `list_sources()` | Documents currently indexed. |
| `get_stats()` | Index size + active backends. |

Verified end-to-end over the real MCP stdio protocol (see `tests/`). Register it
in a client with [`mcp.json`](mcp.json).

---

## Retrieval ablation (computed by `make eval`)

17 gold questions, deliberately paraphrased away from the documents' wording.
`hit@k` = correct document in the top-k; `MRR` = how highly it's ranked.

| Method | hit@4 | MRR |
|--------|:-----:|:---:|
| Lexical (BM25) | 0.941 | 0.873 |
| Semantic (LSA) | 0.941 | 0.912 |
| **Hybrid (RRF fusion)** | 0.941 | **0.941** |

All three usually *find* the right document on this clean corpus, but **hybrid
ranks it highest most consistently**, fusing dense (semantic) and sparse
(keyword) retrieval is a tuning-free win, and the paraphrased questions are
exactly where pure keyword search ranks worse.

> With a neural embedding backend (Voyage/OpenAI/ST) on a larger, noisier corpus
> the gap between lexical and semantic widens further; the local LSA backend
> keeps the demo runnable anywhere while preserving the same ranking behaviour.

---

## Quickstart

```bash
pip install -r requirements.txt && pip install -e .

make demo     # ask a question from the CLI
make eval     # retrieval ablation → reports/eval_results.json
make server   # run the MCP server (stdio)
make test     # 10 tests, incl. an end-to-end MCP protocol check
```

### Use it from Claude Desktop
Copy `mcp.json` into your client config (set the absolute `cwd`), restart the
client, and the four tools appear. Ask *"search the Nimbus docs for how failover
works"* and the model calls `search_documents` / `answer_question`.

### Switch to production backends
```bash
pip install -r requirements-prod.txt
export MCPRAG_EMBEDDING_BACKEND=voyage   VOYAGE_API_KEY=...
export MCPRAG_GENERATOR_BACKEND=anthropic ANTHROPIC_API_KEY=...
```
No code changes, the retriever and server are backend-agnostic.

---

## Layout

```
src/mcprag/
  ingest.py            markdown loading + section-aware chunking w/ overlap
  embeddings/          Embedder protocol · local LSA (offline) · neural backends
  index/vector_store.py  cosine + BM25 + hybrid RRF retrieval
  generator/           extractive (offline, cited) · LLM backends
  rag.py               RAGEngine (ingest→embed→index→retrieve→generate)
  evaluation.py        hit@k / MRR
  server.py            FastMCP server exposing the tools
data/corpus/           the Nimbus knowledge base (8 markdown docs)
eval/qa_gold.json      paraphrased gold questions
scripts/               demo_query · run_eval
tests/                 retrieval, answers, evaluation, MCP protocol
```

## Design notes
- **Grounded by construction.** The offline generator only emits sentences taken
  verbatim from retrieved chunks, each with a citation, it cannot hallucinate.
- **Hybrid retrieval.** Reciprocal Rank Fusion of dense + sparse rankings needs
  no weight tuning and is robust across query types.
- **Backend-agnostic.** Embeddings and generation are pluggable Protocols;
  offline and production share identical retrieval/serving code.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md),
[`docs/RESULTS.md`](docs/RESULTS.md), and
[`docs/IMPROVEMENTS.md`](docs/IMPROVEMENTS.md).

## Tech stack
Python · MCP SDK (FastMCP) · scikit-learn (TF-IDF + LSA) · rank_bm25 · numpy ·
pydantic. Optional: Voyage / OpenAI / sentence-transformers / Anthropic.

## License
MIT. The demo corpus is fictional.
