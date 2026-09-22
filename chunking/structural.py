# Splits every page-level chunk on paragraph boundaries (blank lines)
# instead of arbitrary character counts, so chunks respect the text's
# natural structure.

from ingestion.db import get_connection


def fetch_page_chunks(cursor):
    """Returns all original page-level rows: (doc_name, page_number, content)."""
    cursor.execute(
        "SELECT doc_name, page_number, content FROM chunks WHERE strategy = 'page'"
    )
    return cursor.fetchall()


def split_structural(text):
    """
    Splits text into paragraph-based chunks, using blank lines as boundaries.
    Empty or whitespace-only pieces are dropped.
    """
    raw_pieces = text.split("\n\n")
    chunks = []
    for i in raw_pieces:
        cleaned = i.strip()
        if cleaned:
            chunks.append(cleaned)
    return chunks


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    pages = fetch_page_chunks(cursor)
    total_inserted = 0

    for doc_name, page_number, content in pages:
        pieces = split_structural(content)
        for piece in pieces:
            cursor.execute(
                "INSERT INTO chunks (doc_name, page_number, content, strategy) VALUES (%s, %s, %s, %s)",
                (doc_name, page_number, piece, 'structural')
            )
            total_inserted += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {total_inserted} structural chunks from {len(pages)} pages.")