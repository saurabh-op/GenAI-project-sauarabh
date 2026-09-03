import os
from dotenv import load_dotenv
from google import genai 
from google.genai import types

load_dotenv()

client=genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_embeddings(texts):
    embeddings=[]
    for text in texts:
        result=client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=768
            )
        )

        embeddings.append(result.embeddings[0].values)
    return embeddings