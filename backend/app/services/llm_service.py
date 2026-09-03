import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client=genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_review(query:str,retrieved_chunks:list):
    evidence=""

    for i,chunk in enumerate(retrieved_chunks,start=1):
        evidence+=(
            f"\n---Evidence{i}|Page {chunk['page']}---\n"
            f"{chunk['content']}\n"
        )

    prompt = f"""
You are an AI research paper reviewer.

Answer the user's review question using ONLY the evidence
provided from the research paper.

If the evidence is insufficient, explicitly say:
"Insufficient evidence in the retrieved paper sections."

Do not invent facts or citations.

User question:
{query}

Retrieved evidence:
{evidence}

Provide:
1. Assessment
2. Evidence-based reasoning
3. Strengths
4. Weaknesses
5. Page references
"""
    response=client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text

        