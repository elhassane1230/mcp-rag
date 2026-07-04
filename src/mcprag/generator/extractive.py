"""Extractive answer synthesis (offline, no LLM).

Selects the retrieved sentences most relevant to the question (lexical overlap +
retrieval rank) and stitches them into a short, cited answer. It never invents
content — every sentence comes verbatim from a retrieved chunk and carries a
citation marker — which makes it a safe, deterministic default and a clean
baseline for the answer stage.
"""
from __future__ import annotations

import re

from ..schemas import Answer, Citation, RetrievedChunk

_SENT = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[a-z0-9]+")


def _words(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def _sentences(text: str) -> list[str]:
    # Flatten markdown, drop headings, split into sentences.
    flat = re.sub(r"[#*`]", "", text).replace("\n", " ")
    return [s.strip() for s in _SENT.split(flat) if len(s.strip()) > 25]


class ExtractiveGenerator:
    name = "extractive"

    def generate(self, question: str, retrieved: list[RetrievedChunk],
                 max_sentences: int = 3) -> Answer:
        q_words = _words(question)
        # Assign each source chunk a citation marker in retrieval order.
        citations: list[Citation] = []
        marker_by_chunk: dict[str, str] = {}
        for i, rc in enumerate(retrieved, start=1):
            marker = f"[{i}]"
            marker_by_chunk[rc.chunk.chunk_id] = marker
            citations.append(Citation(marker=marker, source=rc.chunk.source,
                                      title=rc.chunk.title,
                                      chunk_id=rc.chunk.chunk_id))

        # Score candidate sentences by query overlap, boosted by chunk rank.
        scored = []
        for rank, rc in enumerate(retrieved):
            boost = 1.0 / (1 + rank)
            for sent in _sentences(rc.chunk.text):
                overlap = len(q_words & _words(sent))
                if overlap == 0:
                    continue
                score = overlap * (1 + boost)
                scored.append((score, sent, marker_by_chunk[rc.chunk.chunk_id]))

        scored.sort(key=lambda t: -t[0])
        chosen, seen = [], set()
        for _, sent, marker in scored:
            key = sent.lower()
            if key in seen:
                continue
            seen.add(key)
            chosen.append(f"{sent} {marker}")
            if len(chosen) >= max_sentences:
                break

        if chosen:
            answer_text = " ".join(chosen)
        else:
            # No lexical overlap — fall back to the top chunk's opening.
            top = retrieved[0]
            first = _sentences(top.chunk.text)[:1]
            answer_text = ((first[0] if first else top.chunk.text[:200])
                           + f" {marker_by_chunk[top.chunk.chunk_id]}")

        # Only keep citations actually referenced in the answer.
        used = {m for m in marker_by_chunk.values() if m in answer_text}
        citations = [c for c in citations if c.marker in used]
        return Answer(question=question, answer=answer_text,
                      citations=citations, retrieved=retrieved,
                      generator=self.name)
