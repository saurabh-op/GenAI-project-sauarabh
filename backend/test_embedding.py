import os 
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
text = "This paper proposes a novel deep learning approach for sentiment analysis."

result=client.models.embed_content(
    model="gemini-embedding-001",
    contents=text,
    config=types.EmbedContentConfig(
        output_dimensionality=768
    )
)

embedding=result.embeddings[0].values

print("Embedding generated!")
print("Dimensions:", len(embedding))
print("First 5 values:", embedding[:5])