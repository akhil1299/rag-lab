# BM25 keyword search: a smarter, weighted keyword-matching method than
# Postgres full-text search. Rewards rare, distinctive words more than
# common ones. This is the keyword half of Phase 3's hybrid search.

from rank_bm25 import BM25Okapi
from ingestion.db import get_connection
from eval.evaluate import load_questions


def fetch_page_chunks(cursor):
    """Returns all page-level rows: (doc_name, page_number, content)."""
    cursor.execute(
        "SELECT doc_name, page_number, content FROM chunks WHERE strategy = 'page'"
    )
    return cursor.fetchall()


def tokenize(text):
    """
    Splits text into a list of lowercase words for BM25 to compare.
    """
    return text.lower().split()




def bm25_search(bm25, corpus_metadata, question_text, k=5):
    """
    Scores question_text against every chunk in the BM25 index, and
    returns the top k (doc_name, page_number) results, best match first.
    TODO: write this yourself — see guidance below.
    """
    # TODO
    tokenized_question = tokenize(question_text)
    scores = bm25.get_scores(tokenized_question)
    scored_chunks = list(zip(scores, corpus_metadata))
    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    top_k = scored_chunks[:k]
    return [metadata for score, metadata in top_k]    


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    rows = fetch_page_chunks(cursor)
    corpus_metadata = [(doc_name, page_number) for doc_name, page_number, content in rows]
    tokenized_corpus = [tokenize(content) for _, _, content in rows]
    bm25 = BM25Okapi(tokenized_corpus)

    questions = load_questions()
    hits = 0

    for q in questions:
        results = bm25_search(bm25, corpus_metadata, q["question"])
        expected = (q["expected_doc"], q["expected_page"])
        if expected in results:
            hits += 1

    recall_at_5 = hits / len(questions)
    print(f"BM25 recall@5: {recall_at_5:.2f} ({hits}/{len(questions)})")

    cursor.close()
    conn.close()