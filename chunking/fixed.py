# Splits every page-level chunk into fixed-size, 500-character pieces
# with no overlap and no regard for sentence/paragraph boundaries.
# This is Phase 2's naive baseline chunking strategy.

from ingestion.db import get_connection

CHUNK_SIZE = 500


def fetch_page_chunks(cursor):
    """Returns all original page-level rows: (doc_name, page_number, content)."""
    cursor.execute(
        "SELECT doc_name, page_number, content FROM chunks WHERE strategy = 'page'"
    )
    return cursor.fetchall()


def split_fixed(text, chunk_size=CHUNK_SIZE):
    """
    Splits text into a list of fixed-size character chunks.
    """
    chunks = [] #empty array to collect the pieces
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    pages = fetch_page_chunks(cursor)
    total_inserted = 0

    # TODO: loop over pages, split each page's content, insert each
    # piece as a new row with strategy='fixed'. See guidance below.
    for doc_name, page_number, content in pages:
        pieces = split_fixed(content)
        for piece in pieces:
            cursor.execute(
                "INSERT INTO chunks (doc_name, page_number, content, strategy) VALUES (%s, %s, %s, %s)",
                (doc_name, page_number, piece, 'fixed')
            )
            total_inserted += 1



    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {total_inserted} fixed-size chunks from {len(pages)} pages.")