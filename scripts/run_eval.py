"""Run the retrieval ablation: lexical vs semantic vs hybrid.

    python scripts/run_eval.py

Writes reports/eval_results.json and prints a table.
"""
from __future__ import annotations

import json
from pathlib import Path

from mcprag.config import get_config
from mcprag.evaluation import compare_methods
from mcprag.rag import RAGEngine

ROOT = Path(__file__).resolve().parents[1]


def main():
    cfg = get_config()
    engine = RAGEngine.from_corpus(cfg=cfg)
    gold = json.loads((ROOT / "eval" / "qa_gold.json").read_text())["items"]

    results = compare_methods(engine, gold, k=cfg.retrieval.top_k)

    print(f"\nRetrieval ablation on {len(gold)} gold questions "
          f"(top_k={cfg.retrieval.top_k}, embeddings={cfg.embedding_backend}):\n")
    print(f"{'method':<12}{'hit@k':>10}{'MRR':>10}")
    print("-" * 32)
    for r in results:
        print(f"{r['method']:<12}{r['hit@k']:>10.3f}{r['mrr']:>10.3f}")

    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "eval_results.json").write_text(json.dumps({
        "config": {"embedding_backend": cfg.embedding_backend,
                   "top_k": cfg.retrieval.top_k},
        "results": results,
    }, indent=2))
    print(f"\nSaved → {out / 'eval_results.json'}")


if __name__ == "__main__":
    main()
