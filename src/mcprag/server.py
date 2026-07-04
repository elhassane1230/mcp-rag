"""MCP server exposing the semantic RAG engine as tools.

Any MCP client (Claude Desktop, an IDE agent, etc.) can connect over stdio and
call these tools to search and question the knowledge base:

  * search_documents(query, top_k, method) — return the most relevant passages.
  * answer_question(question)              — a grounded answer with citations.
  * list_sources()                         — the documents in the index.
  * get_stats()                            — index/backends summary.

Run:  python -m mcprag.server          (stdio transport)
Register it in an MCP client with the config in ``mcp.json``.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .config import get_config
from .rag import RAGEngine

mcp = FastMCP("nimbus-rag")

# Build the engine once at startup (indexes the corpus).
_engine: RAGEngine | None = None


def engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine.from_corpus(cfg=get_config())
    return _engine


@mcp.tool()
def search_documents(query: str, top_k: int = 4, method: str = "hybrid") -> list[dict]:
    """Search the knowledge base for passages relevant to a query.

    Args:
        query: natural-language search query.
        top_k: number of passages to return.
        method: retrieval strategy — "semantic", "lexical", or "hybrid".
    """
    hits = engine().retrieve(query, top_k=top_k, method=method)
    return [{
        "source": h.chunk.source,
        "title": h.chunk.title,
        "chunk_id": h.chunk.chunk_id,
        "score": round(h.score, 4),
        "text": h.chunk.text,
    } for h in hits]


@mcp.tool()
def answer_question(question: str, top_k: int = 4) -> dict:
    """Answer a question grounded in the knowledge base, with citations.

    Args:
        question: the user's question.
        top_k: how many passages to ground the answer in.
    """
    ans = engine().answer(question, top_k=top_k)
    return {
        "answer": ans.answer,
        "citations": [{"marker": c.marker, "source": c.source, "title": c.title}
                      for c in ans.citations],
        "generator": ans.generator,
    }


@mcp.tool()
def list_sources() -> list[dict]:
    """List the documents available in the knowledge base."""
    return engine().sources()


@mcp.tool()
def get_stats() -> dict:
    """Return index size and the active embedding/generation backends."""
    return engine().stats()


def main() -> None:
    mcp.run()  # stdio transport by default


if __name__ == "__main__":
    main()
