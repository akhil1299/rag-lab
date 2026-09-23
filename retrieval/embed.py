# One-time script: embeds every 'page'-strategy chunk using OpenAI's
# embedding API and stores the resulting vector in the embedding column.
# Only 'page' chunks are embedded (not fixed/overlap/structural) to keep
# chunk size constant while comparing retrieval methods in Phase 3.

import os
from dotenv import load_dotenv
from openai import OpenAI
from ingestion.db import get_connection

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def fetch_unembedded_page_chunks(cursor):
    """Returns (id, content) for every page-strategy chunk."""
    cursor.execute(
        "SELECT id, content FROM chunks WHERE strategy = 'page'"
    )
    return cursor.fetchall()


def embed_text(text):
    """
    Calls OpenAI's embedding API and returns the vector as a list of floats.
    """
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    rows = fetch_unembedded_page_chunks(cursor)
    total_embedded = 0

    for id, content in rows:
        vector = embed_text(content)
        cursor.execute("""
        UPDATE chunks SET embedding = %s WHERE id = %s""", (str(vector), id)
        )
        total_embedded += 1

        



    conn.commit()
    cursor.close()
    conn.close()
    print(f"Embedded {total_embedded} chunks.")