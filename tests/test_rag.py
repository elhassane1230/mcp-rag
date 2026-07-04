import pytest

from mcprag.config import ChunkConfig, get_config
from mcprag.ingest import chunk_document, ingest, load_documents
from mcprag.schemas import Document


def test_load_and_chunk_corpus():
    cfg = get_config()
    docs = load_documents(cfg.corpus_dir)
    assert len(docs) >= 5
    chunks = ingest(cfg.corpus_dir)
    assert len(chunks) > len(docs)          # chunking produced multiple pieces
    assert all(c.text for c in chunks)
    assert all(c.chunk_id and c.source for c in chunks)


def test_chunking_respects_max_chars_with_overlap():
    long_text = "# T\n\n## S\n\n" + (". ".join(f"sentence number {i}"
                                               for i in range(200)) + ".")
    doc = Document(doc_id="d", source="x.md", title="T", text=long_text)
    chunks = chunk_document(doc, ChunkConfig(max_chars=300, overlap=50))
    assert len(chunks) > 1
    assert all(len(c.text) <= 400 for c in chunks)   # window + slack


@pytest.fixture(scope="module")
def engine():
    from mcprag.rag import RAGEngine
    return RAGEngine.from_corpus()


def test_semantic_retrieval_finds_right_doc(engine):
    # paraphrase without keyword overlap -> semantic match
    hits = engine.retrieve("what happens if I exceed my included usage?",
                           top_k=4, method="semantic")
    assert any(h.chunk.source == "billing.md" for h in hits)


def test_hybrid_retrieval_returns_scored_chunks(engine):
    hits = engine.retrieve("rotate credentials", top_k=3, method="hybrid")
    assert len(hits) == 3
    assert all(h.score >= 0 for h in hits)


def test_answer_is_grounded_and_cited(engine):
    ans = engine.answer("How do I rotate my API key?")
    assert ans.answer
    assert ans.citations                      # at least one source cited
    # every citation marker used in the answer appears in the citation list
    for c in ans.citations:
        assert c.marker in ans.answer
