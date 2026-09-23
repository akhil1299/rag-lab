# RAG Lab

A production-grade RAG pipeline built and measured phase by phase using 3 real SEC 10-K filings (Apple, Starbucks, JPMorgan Chase) as source data.

Every claim below is backed by an eval set of 20 hand-written questions, each mapped to the exact doc and page that answers it.

## Results

| Stage                             | recall@5 |
|------------------------------------|----------|
| baseline (page-level chunks)       | 0.30     |
| fixed (500 chars)                  | 0.10     |
| overlap (500 chars, 100 overlap)   | 0.10     |
| structural (sentence-grouped)      | 0.15     |

## What's here so far

- `ingestion/db.py` --> Supabase/Postgres connection
- `ingestion/schema.py` --> creates the `chunks` table (id, doc_name, page_number, content, embedding, strategy)
- `ingestion/load_pdfs.py` --> reads the 3 10-Ks page-by-page, inserts 701 chunks (strategy='page')
- `eval/questions.json` --> 20 hand-verified questions against the three filings
- `eval/evaluate.py` --> measures recall@5 using Postgres full-text search
- `chunking/fixed.py` --> splits pages into fixed 500-character chunks
- `chunking/overlap.py` --> same, with 100-character overlap between chunks
- `chunking/structural.py` --> groups sentences into ~500-character chunks, never cutting a sentence in half
- `chunking/compare.py` --> re-runs recall@5 for each chunking strategy, side by side
- `retrieval/embed.py` --> embeds all 701 page-level chunks using OpenAI's text-embedding-3-small (1536-dim vectors)
- `retrieval/negation_test.py` --> measures cosine similarity between a statement and its negation

## Baseline: why 0.30?

The baseline uses Postgres's built-in full-text search (`to_tsvector` /
`plainto_tsquery`), which requires literal word overlap between the question
and the chunk. Most misses come from phrasing mismatches — e.g. a question
asking about "fiscal year 2025" when the filing just says "2025" nearby,
with no literal word "fiscal" close to the number. Full-text search has no
way to know these mean the same thing.

This is the exact gap Phase 3 (vector embeddings + hybrid search) exists to close.

## What embeddings cannot do

"This account is approved for options trading" vs.
"This account is NOT approved for options trading"
→ cosine similarity: **0.88**

Opposite meaning, nearly identical vectors. Embeddings encode topical
similarity, not logical negation — this is exactly why hybrid search
and explicit source-quoting are required in compliance-sensitive
contexts, not optional nice-to-haves.

## What didn't work

- **Smaller chunks hurt full-text search recall.** All three Phase 2
  chunking strategies (fixed, overlap, structural — all targeting
  ~500 characters) scored *lower* recall@5 than the original page-level
  baseline (0.30 → 0.10-0.15). Postgres full-text search requires all
  query keywords to appear in the same chunk (`AND` logic via
  `plainto_tsquery`); smaller chunks split related keywords across
  chunk boundaries, so fewer chunks satisfy the full match. This
  suggests chunk size and retrieval method interact — a chunk size
  that helps semantic search may hurt keyword search, and vice versa.
- **Naive paragraph splitting on `\n\n` silently failed.** The first
  attempt at `structural.py` split on double newlines, assuming pypdf's
  `extract_text()` preserves blank lines between paragraphs. It doesn't
  — extraction collapses everything to single `\n`, so the function
  returned exactly one "chunk" per page (701 chunks from 701 pages,
  identical to the raw page-level baseline). Diagnosed with `repr()` on
  a real extracted page, then switched to sentence-boundary grouping
  instead.

## Running it

```powershell
python -m ingestion.schema      # creates the chunks table
python -m ingestion.load_pdfs   # loads the 3 10-Ks (701 chunks)
python -m eval.evaluate         # prints baseline recall@5
python -m chunking.fixed        # inserts fixed-size chunks
python -m chunking.overlap      # inserts overlapping chunks
python -m chunking.structural   # inserts structural (sentence-grouped) chunks
python -m chunking.compare      # prints recall@5 per chunking strategy
python -m retrieval.embed       # embeds all 701 page-level chunks
python -m retrieval.negation_test  # prints cosine similarity for negation test
```