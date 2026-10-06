from langgraph.graph import StateGraph,START,END

from app.agents.state import ReviewState
from app.agents.schemas import AgentReview,FinalReview
from langchain_google_genai import ChatGoogleGenerativeAI
from app.agents.schemas import AgentReview
from app.rag.langchain_retriever import ResearchPaperRetriever

def supervisor(state:ReviewState):
    print("supervisor :Coordinating review agents")
    return state

def methodology_agent(state:ReviewState):
    print("MEthofology Agent: reviewing methodology")

    retriever=ResearchPaperRetriever(
        paper_id=state["paper_id"],
        top_k=1
    )

    documents=retriever.invoke(
            "What methodology, proposed approach, model architecture, algorithms, and implementation does this research paper use?"
    )

    context="\n\n".join(
        f"[Page{doc.metadata['page']}]\n{doc.page_content}"
        for doc in documents
    )

    llm=ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0
    ).with_structured_output(AgentReview)


    prompt = f"""
Evaluate:
1. Methodology clarity
2. Technical soundness
3. Appropriateness of the proposed approach
4. Important methodological strengths
5. Important methodological weaknesses

Do not invent information.

For every paper-specific claim, mention the page number.

If evidence is insufficient, say:
"Insufficient evidence in the retrieved sections."
"""

    response = llm.invoke(prompt)

    return {
    "methodology_review": response.model_dump()
    }

def novelty_agent(state:ReviewState):
    print("Novlty agent:rviewing novelty")
    retriever=ResearchPaperRetriever(
        paper_id=state["paper_id"],
        top_k=1
    )

    documents=retriever.invoke("what existig research does this paper discuss,what research gap does it identify, and what is novel about the proposed contirbution ?")
    context="\n\n".join(
        f"[Page{doc.metadata['page']}]\n{doc.page_content}"
        for doc in documents
    )
    llm=ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0
    ).with_structured_output(AgentReview)


    prompt = f"""
Evaluate:
1. Literature/research gap
2. Novelty of the proposed approach
3. Significance of the contribution
4. Strengths of the contribution
5. Weaknesses or unclear claims

Do not invent information.

For every paper-specific claim, mention the page number.

If evidence is insufficient, say:
"Insufficient evidence in the retrieved sections."
"""
    response=llm.invoke(prompt)
    return {
       "novelty_review": response.model_dump()
    }


    
def quality_agent(state: ReviewState):
    print("quality agent: reviewing ressearch quality")
    retriever=ResearchPaperRetriever(
        paper_id=state["paper_id"],
        top_k=1
    )
    documents=retriever.invoke(
        "What experiments, datasets, evaluation metrics, results, discussion, limitations, and weaknesses are presented in this research paper?"    )

    context="\n\n".join(
        f"[Page{doc.metadata['page']}]\n{doc.page_content}"
        for doc in documents

    )

    llm=ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0
    ).with_structured_output(AgentReview)
    prompt = f"""
Evaluate:
1. Experimental design
2. Dataset and evaluation methodology
3. Results and discussion
4. Limitations
5. Overall research quality
6. Important strengths and weaknesses

Do not invent information.

For every paper-specific claim, mention the page number.

If evidence is insufficient, say:
"Insufficient evidence in the retrieved sections."
"""
    response=llm.invoke(prompt)
    return {
        "quality_review":response.model_dump()
    }


def final_reviewer(state: ReviewState):

    print("Final Reviewer: combining agent reviews")

    methodology = state.get("methodology_review", "")
    novelty = state.get("novelty_review", "")
    quality = state.get("quality_review", "")

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0
    ).with_structured_output(FinalReview)

    prompt = f"""
You are the final research paper reviewer.

You have received assessments from three specialist reviewers:

METHODOLOGY REVIEW:
{methodology}

NOVELTY REVIEW:
{novelty}

QUALITY REVIEW:
{quality}

Combine these assessments into one coherent research paper review.

Do not introduce facts that are not present in the specialist reviews.

Return ONLY valid JSON using exactly this structure:

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
  "text": "short supporting statement"
}}

If the specialist reviews do not provide enough information for a section, write:

"Insufficient evidence in the retrieved sections."
"""

    response = llm.invoke(prompt)

    return {
            "final_review": response.model_dump()
    }

workflow=StateGraph(ReviewState)

workflow.add_node("supervisor",supervisor)
workflow.add_node("methodology_agent",methodology_agent)
workflow.add_node("novelty_agent",novelty_agent)
workflow.add_node("quality_agent",quality_agent)
workflow.add_node("final_reviewer",final_reviewer)

workflow.add_edge(START,"supervisor")
workflow.add_edge("supervisor","methodology_agent")
workflow.add_edge("supervisor", "novelty_agent")
workflow.add_edge("supervisor", "quality_agent")

workflow.add_edge("methodology_agent", "final_reviewer")
workflow.add_edge("novelty_agent", "final_reviewer")
workflow.add_edge("quality_agent", "final_reviewer")

workflow.add_edge("final_reviewer", END)

review_graph = workflow.compile()