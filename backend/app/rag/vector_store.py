import os
import json
import psycopg
from dotenv import load_dotenv

load_dotenv()

def store_chunks(paper_id,chunks,embeddings):
    connection=psycopg.connect(os.getenv("DATABASE_URL"),prepare_threshold=None)
    with connection.cursor() as cursor:
        for chunk,embedding in zip(chunks,embeddings):
            cursor.execute(
                """
                INSERT INTO paper_chunks
                (paper_id, content, page_number, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    paper_id,
                    chunk["text"],
                    chunk["page"],
                    json.dumps({}),
                    embedding
                )

            )
    connection.commit()
    connection.close()