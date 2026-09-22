# Splits every page-level chunk into sentence-grouped chunks, targeting
# ~500 characters per chunk. Sentences are never cut in half — this
# replaces an earlier attempt that tried splitting on "\n\n" (blank
# lines), which failed because pypdf's extract_text() only produces
# single newlines, never double ones.

from ingestion.db import get_connection


def fetch_page_chunks(cursor):
    """Returns all original page-level rows: (doc_name, page_number, content)."""
    cursor.execute(
        "SELECT doc_name, page_number, content FROM chunks WHERE strategy = 'page'"
    )
    return cursor.fetchall()


def split_structural(text, target_size=500):
    """
    Splits text into sentences, then groups consecutive sentences
    together until each chunk reaches roughly target_size characters.
    Never cuts a sentence in half.
    """
    sentences = text.split(". ")
    chunks = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current) + len(sentence) <= target_size:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "

    if current.strip():
        chunks.append(current.strip())

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