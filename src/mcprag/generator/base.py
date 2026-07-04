"""Answer generators (the "G" in RAG).

A generator turns a question + retrieved chunks into a grounded ``Answer`` with
citations. Backends:

  * extractive — offline default: composes the answer from the most relevant
    retrieved sentences with inline citation markers. No API key needed, so the
    demo is fully runnable and its answers are, by construction, grounded.
  * anthropic / openai — production: prompt an LLM with the retrieved context
    and instructions to answer only from it and cite sources.
"""
from __future__ import annotations


def get_generator(backend: str):
    if backend == "extractive":
        from .extractive import ExtractiveGenerator
        return ExtractiveGenerator()
    if backend in {"anthropic", "openai"}:
        from .llm import LLMGenerator
        return LLMGenerator(backend=backend)
    raise ValueError(f"Unknown generator backend: {backend}")
