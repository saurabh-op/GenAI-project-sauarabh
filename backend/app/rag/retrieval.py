import os 
import psycopg
from dotenv import load_dotenv

from app.services.embedding_service import generate_embeddings

load_dotenv()

def retrieve_chunks(query:str,paper_id:str,top_k:int=5):
    query_embedding=generate_embeddings([query])[0]
    connection=psycopg.connect(os.getenv("DATABASE_URL"))
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                content,
                page_number,
                embedding <=> %s::vector AS distance
            FROM paper_chunks
            WHERE paper_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (
                query_embedding,
                paper_id,
                query_embedding,
                top_k
            )
        )

        rows=cursor.fetchall()

    connection.close()

    results=[]
    seen=set()

    for content , page , distance in rows:

        content_key=content.strip()

        if content_key in seen:
            continue

        seen.add(content_key)
        distance=float(distance)
        results.append({
            "content":content,
            "page":page,
            "distance":float(distance),
            "similarity":1-distance
        })

    return results