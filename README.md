# RAG Lab

A production-oriented RAG pipeline, built and measured phase by phase,
using three real SEC 10-K filings (Apple, Starbucks, JPMorgan Chase) as source data.

Every claim below is backed by an eval set of 20 hand-written questions,
each mapped to the exact document and page that answers it.

## Results

| Stage                          | recall@5 |
|---------------------------------|----------|
| baseline (Postgres full-text)   | 0.30     |

## What's here so far

- `ingestion/db.py` — Supabase/Postgres connection
- `ingestion/schema.py` — creates the `chunks` table (id, doc_name, page_number, content, embedding)
- `ingestion/load_pdfs.py` — reads the three 10-Ks page-by-page, inserts 701 chunks
- `eval/questions.json` — 20 hand-verified questions against the three filings
- `eval/evaluate.py` — measures recall@5 using Postgres full-text search

## Baseline: why 0.30?

The baseline uses Postgres's built-in full-text search (`to_tsvector` /
`plainto_tsquery`), which requires literal word overlap between the question
and the chunk. Most misses come from phrasing mismatches — e.g. a question
asking about "fiscal year 2025" when the filing just says "2025" nearby,
with no literal word "fiscal" close to the number. Full-text search has no
way to know these mean the same thing.

This is the exact gap Phase 3 (vector embeddings + hybrid search) exists to close.

## Running it

```powershell
python -m ingestion.schema      # creates the chunks table
python -m ingestion.load_pdfs   # loads the 3 10-Ks (701 chunks)
python -m eval.evaluate         # prints recall@5
```

## What didn't work

*(filled in as later phases produce measured negative results)*