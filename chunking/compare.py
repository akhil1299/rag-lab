# Compares recall@5 across the three chunking strategies built in this
# phase (fixed, overlap, structural), using the same 20 questions and
# same full-text search method as eval/evaluate.py — the only variable
# changing between runs is which strategy's chunks are being searched.

from ingestion.db import get_connection
from eval.evaluate import load_questions

STRATEGIES = ["fixed", "overlap", "structural"]


def search_by_strategy(cursor, question_text, strategy, k=5):
    """
    Same full-text search as naive_search, but restricted to chunks
    belonging to one chunking strategy.
    """
    sql = """
        SELECT doc_name, page_number
        FROM chunks
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', %s)
        AND strategy = %s
        ORDER BY ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) DESC
        LIMIT %s;
    """
    cursor.execute(sql, (question_text, strategy, question_text, k))
    return cursor.fetchall()


if __name__ == "__main__":
    questions = load_questions()
    conn = get_connection()
    cursor = conn.cursor()

    for strategy in STRATEGIES:
        hits = 0
        for q in questions:
            results = search_by_strategy(cursor, q["question"], strategy)
            expected = (q["expected_doc"], q["expected_page"])
            if expected in results:
                hits += 1
        recall_at_5 = hits / len(questions)
        print(f"{strategy}: recall@5 = {recall_at_5:.2f} ({hits}/{len(questions)})")

    cursor.close()
    conn.close()