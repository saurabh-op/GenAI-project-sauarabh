from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.rag.langchain_retriever import ResearchPaperRetriever

llm=ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0
)

prompt = ChatPromptTemplate.from_template("""
You are an expert academic research paper reviewer.

Use ONLY the provided research paper context.

Do not invent facts.
If the context does not contain enough evidence, say:
"Insufficient evidence in the retrieved sections."

Always mention the page number when making a paper-specific claim.

Research question:
{question}

Research paper context:
{context}

Provide an evidence-based assessment.
""")

def create_rag_chain(paper_id:str):
    retriever=ResearchPaperRetriever(
        paper_id=paper_id,
        top_k=5
    )

    def run(question: str):
        documents=retriever.invoke(question)
        context="\n\n".join(
            f"[Page{doc.metadata['page']}]\n{doc.page_content}"
            for doc in documents
        )
        message=prompt.invoke({
            "question":question,
            "context":context
         })
        response=llm.invoke(message)

        return{
            "answer":response.content,
            "sources":[
                {
                    "page":doc.metadata["page"],
                    "content":doc.page_content
                }
                for doc in documents
            ]
        }
    return run
        