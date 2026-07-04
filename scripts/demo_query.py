"""Interactive CLI demo of the RAG engine (no MCP client needed).

    python scripts/demo_query.py "How do I rotate my API key?"
    python scripts/demo_query.py           # enters an interactive loop
"""
from __future__ import annotations

import sys

from mcprag.rag import RAGEngine


def show(engine, question: str) -> None:
    ans = engine.answer(question)
    print(f"\nQ: {question}")
    print(f"A: {ans.answer}")
    if ans.citations:
        print("Sources:")
        for c in ans.citations:
            print(f"   {c.marker} {c.source} — {c.title}")


def main():
    engine = RAGEngine.from_corpus()
    print("Nimbus RAG demo —", engine.stats())
    if len(sys.argv) > 1:
        show(engine, " ".join(sys.argv[1:]))
        return
    print("Ask a question (empty line to quit):")
    while True:
        try:
            q = input("\n> ").strip()
        except EOFError:
            break
        if not q:
            break
        show(engine, q)


if __name__ == "__main__":
    main()
