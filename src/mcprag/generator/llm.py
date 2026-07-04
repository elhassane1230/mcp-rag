"""LLM answer generation (production, lazy-imported).

Prompts an LLM with the retrieved context and strict instructions to answer
only from it and cite sources by their markers. Requires an API key.
"""
from __future__ import annotations

import os

from ..schemas import Answer, Citation, RetrievedChunk

SYSTEM = (
    "You are a precise assistant. Answer the user's question using ONLY the "
    "provided context passages. Cite the passages you use with their bracket "
    "markers like [1]. If the answer is not in the context, say you don't know."
)


def _format_context(retrieved: list[RetrievedChunk]) -> tuple[str, list[Citation]]:
    lines, citations = [], []
    for i, rc in enumerate(retrieved, start=1):
        marker = f"[{i}]"
        lines.append(f"{marker} ({rc.chunk.source} — {rc.chunk.title})\n{rc.chunk.text}")
        citations.append(Citation(marker=marker, source=rc.chunk.source,
                                  title=rc.chunk.title, chunk_id=rc.chunk.chunk_id))
    return "\n\n".join(lines), citations


class LLMGenerator:
    def __init__(self, backend: str, model: str | None = None):
        self.backend = backend
        self.name = backend
        self.model = model or _DEFAULTS[backend]

    def generate(self, question: str, retrieved: list[RetrievedChunk],
                 **_) -> Answer:
        context, citations = _format_context(retrieved)
        prompt = f"Context:\n{context}\n\nQuestion: {question}"

        if self.backend == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
            resp = client.messages.create(
                model=self.model, max_tokens=500, system=SYSTEM,
                messages=[{"role": "user", "content": prompt}])
            text = resp.content[0].text
        elif self.backend == "openai":
            from openai import OpenAI
            client = OpenAI()
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": prompt}])
            text = resp.choices[0].message.content
        else:
            raise ValueError(self.backend)

        used = {c.marker for c in citations if c.marker in text}
        return Answer(question=question, answer=text,
                      citations=[c for c in citations if c.marker in used],
                      retrieved=retrieved, generator=self.name)


_DEFAULTS = {"anthropic": "claude-sonnet-4-6", "openai": "gpt-4o-mini"}
