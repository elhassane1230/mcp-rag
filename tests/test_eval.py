import json
from pathlib import Path

import pytest

from mcprag.evaluation import compare_methods, evaluate
from mcprag.rag import RAGEngine

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def engine():
    return RAGEngine.from_corpus()


@pytest.fixture(scope="module")
def gold():
    return json.loads((ROOT / "eval" / "qa_gold.json").read_text())["items"]


def test_evaluate_returns_metrics(engine, gold):
    r = evaluate(engine, gold, method="hybrid", k=4)
    assert 0.0 <= r["hit@k"] <= 1.0
    assert 0.0 <= r["mrr"] <= 1.0
    assert r["n_questions"] == len(gold)


def test_retrieval_quality_is_high(engine, gold):
    # On this clean corpus the correct doc should be found for most questions.
    r = evaluate(engine, gold, method="hybrid", k=4)
    assert r["hit@k"] >= 0.8


def test_hybrid_mrr_at_least_matches_lexical(engine, gold):
    results = {r["method"]: r for r in compare_methods(engine, gold, k=4)}
    assert results["hybrid"]["mrr"] >= results["lexical"]["mrr"] - 1e-9


def test_mcp_server_exposes_tools():
    # The FastMCP app should register all four tools.
    from mcprag import server
    names = {"search_documents", "answer_question", "list_sources", "get_stats"}
    # engine builds lazily; just check the tool functions exist and are callable
    for n in names:
        assert hasattr(server, n)
        assert callable(getattr(server, n))


def test_mcp_tool_answer_question_runs():
    from mcprag import server
    out = server.answer_question("How do I rotate my API key?")
    assert "answer" in out
    assert isinstance(out["citations"], list)
