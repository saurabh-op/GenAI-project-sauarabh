import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

embeddings=GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_keys=os.getenv("GEMINI_API_KEY"),
    output_dimensionality=768
)