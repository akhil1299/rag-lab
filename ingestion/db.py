import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Opens and returns a new connection to the Supabase Postgres database.
    Every other module in this repo (ingestion, retrieval, filtering) will
    call this function instead of connecting on its own.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found — check your .env file")

    conn = psycopg2.connect(database_url)
    return conn


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT VERSION();
    """)
    result = cursor.fetchone()
    print(result)
    cursor.close()
    conn.close()

