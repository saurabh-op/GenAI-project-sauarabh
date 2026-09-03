import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client=genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_review(retrieved_chunks:list):
    evidence=""

    for i,chunk in enumerate(retrieved_chunks,start=1):
        evidence+=(
            f"\n---Evidence{i}|Page {chunk['page']}---\n"
            f"{chunk['content']}\n"
        )

        prompt = f"""
You are an expert academic research paper reviewer.

Review the research paper using ONLY the retrieved evidence.

Do not invent facts.
If evidence is insufficient, say:
"Insufficient evidence in the retrieved sections."

Return ONLY valid JSON.

Use exactly this structure:

{{
  "research_problem": {{
    "assessment": "",
    "strengths": [],
    "weaknesses": [],
    "evidence": []
  }},
  "literature_gap": {{
    "assessment": "",
    "strengths": [],
    "weaknesses": [],
    "evidence": []
  }},
  "methodology": {{
    "assessment": "",
    "strengths": [],
    "weaknesses": [],
    "evidence": []
  }},
  "experimental_design": {{
    "assessment": "",
    "strengths": [],
    "weaknesses": [],
    "evidence": []
  }},
  "results_discussion": {{
    "assessment": "",
    "strengths": [],
    "weaknesses": [],
    "evidence": []
  }},
  "novelty_contribution": {{
    "assessment": "",
    "strengths": [],
    "weaknesses": [],
    "evidence": []
  }},
  "limitations": {{
    "assessment": "",
    "strengths": [],
    "weaknesses": [],
    "evidence": []
  }},
  "overall_assessment": {{
    "assessment": "",
    "strengths": [],
    "weaknesses": [],
    "evidence": []
  }}
}}

Each evidence item must contain:

{{
  "page": 1,
  "text": "short supporting excerpt"
}}

Retrieved evidence:
{evidence}
"""
    response=client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text

        