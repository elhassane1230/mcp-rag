"""mcprag — a semantic RAG engine exposed over the Model Context Protocol (MCP).

Pipeline: ingest documents → chunk → embed → index → hybrid retrieval
(semantic + lexical, fused) → grounded answer synthesis with citations.
The whole engine is exposed as MCP tools so any MCP client (e.g. Claude Desktop)
can query the knowledge base.
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
