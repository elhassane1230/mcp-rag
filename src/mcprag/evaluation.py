"""Retrieval evaluation: how often does the correct document surface, and how
high? Metrics over a gold QA set:

  * hit@k  — fraction of questions whose gold source appears in the top-k.
  * MRR    — mean reciprocal rank of the first correct source (rewards ranking
             the right document higher).

Comparing lexical / semantic / hybrid on the same questions is the core ablation
of the project: it shows where dense semantic matching beats keyword search.
"""
from __future__ import annotations

from .rag import RAGEngine


def evaluate(engine: RAGEngine, gold: list[dict], method: str,
             k: int = 4) -> dict:
    hits = 0
    reciprocal_ranks = []
    for item in gold:
        retrieved = engine.retrieve(item["question"], top_k=k, method=method)
        sources = [r.chunk.source for r in retrieved]
        gold_src = item["gold_source"]
        if gold_src in sources:
            hits += 1
            rank = sources.index(gold_src) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)
    n = len(gold)
    return {
        "method": method,
        "hit@k": round(hits / n, 4),
        "mrr": round(sum(reciprocal_ranks) / n, 4),
        "k": k,
        "n_questions": n,
    }


def compare_methods(engine: RAGEngine, gold: list[dict], k: int = 4) -> list[dict]:
    return [evaluate(engine, gold, m, k)
            for m in ("lexical", "semantic", "hybrid")]
