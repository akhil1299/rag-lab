# Splits every page-level chunk into 500-character pieces that overlap
# the previous chunk by 100 characters, so a sentence cut at a boundary
# still appears whole in at least one chunk.

from ingestion.db import get_connection

CHUNK_SIZE = 500
OVERLAP = 100


def fetch_page_chunks(cursor):
    """Returns all original page-level rows: (doc_name, page_number, content)."""
    cursor.execute(
        "SELECT doc_name, page_number, content FROM chunks WHERE strategy = 'page'"
    )
    return cursor.fetchall()


def split_overlap(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """
    Splits text into overlapping fixed-size chunks.
    """
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(text), step):
        chunks.append(text[i:i+chunk_size])
    return chunks


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    pages = fetch_page_chunks(cursor)
    total_inserted = 0

    for doc_name, page_number, content in pages:
        pieces = split_overlap(content)
        for piece in pieces:
            cursor.execute(
                "INSERT INTO chunks (doc_name, page_number, content, strategy) VALUES (%s, %s, %s, %s)",
                (doc_name, page_number, piece, 'overlap')
            )
            total_inserted += 1


    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {total_inserted} overlapping chunks from {len(pages)} pages.")