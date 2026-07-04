# Results & methodology

Reproduce: `make eval` (writes `reports/eval_results.json`).

## Setup
- Corpus: 8 fictional "Nimbus" documents → 36 chunks (section-aware, overlapping).
- Embeddings: local LSA (TF-IDF 1–2 grams → Truncated SVD), L2-normalised.
- Gold set: 17 questions (`eval/qa_gold.json`), deliberately paraphrased away
  from the documents' wording so the correct answer requires *meaning* matching,
  not keyword matching.
- Metrics: `hit@k` (correct source in top-k) and MRR (reciprocal rank of the
  first correct source).

## Retrieval ablation (top_k = 4)

| Method | hit@4 | MRR |
|--------|:-----:|:---:|
| Lexical (BM25) | 0.941 | 0.873 |
| Semantic (LSA) | 0.941 | 0.912 |
| Hybrid (RRF) | 0.941 | 0.941 |

**Reading it.** On a small, clean corpus every method finds the right document
for 16/17 questions (hit@4 = 0.941). The differentiator is *ranking quality*:
MRR rises from 0.873 (lexical) to 0.912 (semantic) to 0.941 (hybrid). Hybrid
fusion places the correct document first most often — it inherits semantic's
paraphrase handling and BM25's exact-term precision.

## Semantic wins — worked examples
Queries with no keyword overlap with their answer, retrieved correctly:
- "go over my included usage" → billing *overage* section.
- "change my credentials without downtime" → *key rotation* section.
- "confirm a webhook really came from you" → *signature verification* section.
- "right-to-be-forgotten request" → *GDPR erasure* section.

## Honesty notes
- The local LSA backend is classical semantic matching; a dense neural encoder
  would widen the semantic-vs-lexical gap, especially on larger/noisier corpora.
  The pluggable design lets you verify this by setting `MCPRAG_EMBEDDING_BACKEND`.
- hit@k saturates on 8 documents; the metric becomes more discriminating as the
  corpus grows. MRR already separates the methods here.
- The extractive generator is evaluated for *grounding/citation correctness*
  (tests), not fluency; the LLM backends produce more natural prose.
