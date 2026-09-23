# Vector search: for each question, embed it and find the 5 chunks
# whose embeddings are closest by cosine distance. Tests whether real
# semantic search beats the 0.30 full-text baseline from Phase 1.

from ingestion.db import get_connection
from eval.evaluate import load_questions
from retrieval.embed import embed_text


def vector_search(cursor, question_text, k=5):
    """
    Embeds question_text, then finds the k closest chunks by cosine
    distance (pgvector's <=> operator), restricted to strategy='page'.
    """
    question_vector = embed_text(question_text)

    cursor.execute("""
        SELECT doc_name, page_number
        FROM chunks
        WHERE strategy = 'page'
        ORDER BY embedding <=> %s
        LIMIT %s;
    """, (str(question_vector), k))

    return cursor.fetchall()


if __name__ == "__main__":
    questions = load_questions()
    conn = get_connection()
    cursor = conn.cursor()

    hits = 0

    for q in questions:
        results = vector_search(cursor, q["question"])
        expected = (q["expected_doc"], q["expected_page"])
        if expected in results:
            hits += 1

    recall_at_5 = hits / len(questions)
    print(f"vector search recall@5: {recall_at_5:.2f} ({hits}/{len(questions)})")

    cursor.close()
    conn.close()