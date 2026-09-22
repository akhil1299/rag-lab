# Reads every PDF in data/pdfs/ page-by-page and inserts one row per
# page into the chunks table. This is the crudest possible chunking
# strategy on purpose — Phase 2 is where we measure better ones.

import os
import glob
from pypdf import PdfReader
from ingestion.db import get_connection

PDF_DIR = "data/pdfs"


def load_pdfs():
    pdf_paths = glob.glob(os.path.join(PDF_DIR, "*.pdf"))

    conn = get_connection()
    cursor = conn.cursor()

    total_inserted = 0

    for pdf_path  in pdf_paths:
        doc_name = os.path.basename(pdf_path)
        reader = PdfReader(pdf_path)
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text or not text.strip():
                continue
            cursor.execute(
                "INSERT INTO chunks (doc_name, page_number, content) VALUES (%s, %s, %s)",
                (doc_name, page_number, text)
            )
            total_inserted += 1

            







    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {total_inserted} chunks from {len(pdf_paths)} PDFs.")


if __name__ == "__main__":
    load_pdfs()