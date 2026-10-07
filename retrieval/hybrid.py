# Hybrid search: merges the vector-search ranking and the BM25 ranking
# into one combined ranking using Reciprocal Rank Fusion (RRF).

from rank_bm25 import BM25Okapi
from ingestion.db import get_connection
from eval.evaluate import load_questions
from retrieval.vector import vector_search
from retrieval.keyword import fetch_page_chunks, tokenize, bm25_search

RRF_K = 60          # damping constant from the original RRF paper
CANDIDATE_K = 20    # how many results to pull from EACH method before merging


def reciprocal_rank_fusion(vector_results, bm25_results, k=5):
    """
    Merges two ranked lists of (doc_name, page_number) tuples into one
    ranked list using Reciprocal Rank Fusion. Returns the top k.
    """
    scores = {}
    for ranked_list in (vector_results, bm25_results):
        for rank, page in enumerate(ranked_list, start=1):
            points = 1/(RRF_K + rank)
            if page in scores:
                scores[page] = scores[page] + points
            else:
                scores[page] = points


    scores_list = list(scores.items())
    scores_list.sort(key = lambda x: x[1], reverse=True)
    return [page for page, score in scores_list[:k]]


def hybrid_search(cursor, bm25, corpus_metadata, question_text, k=5):
    """
    Runs vector search and BM25 search for the same question, then
    merges both rankings and returns the top k (doc_name, page_number).
    """
    vector_results = vector_search(cursor, question_text, k=CANDIDATE_K)
    bm25_results = bm25_search(bm25, corpus_metadata, question_text, k=CANDIDATE_K)
    return reciprocal_rank_fusion(vector_results, bm25_results, k=k)


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
        results = hybrid_search(cursor, bm25, corpus_metadata, q["question"])
        expected = (q["expected_doc"], q["expected_page"])
        if expected in results:
            hits += 1

    recall_at_5 = hits / len(questions)
    print(f"hybrid recall@5: {recall_at_5:.2f} ({hits}/{len(questions)})")

    cursor.close()
    conn.close()