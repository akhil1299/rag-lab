# Measures baseline recall@5: for each hand-written question, does a
# simple keyword search find the correct page in its top 5 results?
# This is the crudest possible retrieval on purpose — Phase 3 replaces
# it with real vector embeddings and hybrid search.

import json
from ingestion.db import get_connection

QUESTIONS_PATH = "eval/questions.json"


def load_questions():
    """Reads the hand-built eval set from disk."""
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def naive_search(cursor, question_text, k=5):
    """
    Runs a Postgres full-text search for question_text and returns
    the top k (doc_name, page_number) results, best match first.
    """
    sql = """
        SELECT doc_name, page_number
        FROM chunks
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', %s)
        ORDER BY ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) DESC
        LIMIT %s;
    """
    cursor.execute(sql, (question_text, question_text, k))
    return cursor.fetchall()


if __name__ == "__main__":
    questions = load_questions()
    conn = get_connection()
    cursor = conn.cursor()

    hits = 0

    for q in questions:
        results = naive_search(cursor, q["question"])
        expected = (q["expected_doc"], q["expected_page"])
        if expected in results:
            hits += 1

    recall_at_5 = hits / len(questions)
    print(f"recall@5: {recall_at_5:.2f} ({hits}/{len(questions)})")

    cursor.close()
    conn.close()