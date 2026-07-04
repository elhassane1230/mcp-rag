.PHONY: help install demo eval server test lint clean

PY := PYTHONPATH=src python3

help:
	@echo "mcp-rag — tasks"
	@echo "  make install   Install core dependencies"
	@echo "  make demo      Ask the RAG a question (CLI)"
	@echo "  make eval      Retrieval ablation (lexical/semantic/hybrid)"
	@echo "  make server    Run the MCP server (stdio)"
	@echo "  make test      Run tests"
	@echo "  make lint      ruff"

install:
	pip install -r requirements.txt && pip install -e .
demo:
	$(PY) scripts/demo_query.py "How do I rotate my API key without downtime?"
eval:
	$(PY) scripts/run_eval.py
server:
	$(PY) -m mcprag.server
test:
	$(PY) -m pytest tests/ -q
lint:
	ruff check src tests scripts
clean:
	rm -rf reports/*.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
