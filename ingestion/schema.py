from ingestion.db import get_connection

def create_chunks_table():
    """
    Creates the chunks table if it doesn't already exist.
    Safe to run more than once — IF NOT EXISTS means no error and no duplicate table.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            doc_name TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding vector(1536)
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("chunks table created (or already existed).")


if __name__ == "__main__":
    # TODO: call create_chunks_table() yourself
    chunks = create_chunks_table()
    
    pass


