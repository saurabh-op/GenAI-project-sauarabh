from langchain_core.documents import Document

from app.rag.retrieval import retrieve_chunks

class ResearchPaperRetriever:
    def __init__(self,paper_id:str,top_k:int=5):
        self.paper_id=paper_id
        self.top_k=top_k
    def invoke(self,query:str):
        chunks=retrieve_chunks(
            query=query,
            paper_id=self.paper_id,
            top_k=self.top_k
        )

        return [Document(
            page_content=chunk["content"],
            metadata={
                "page":chunk["page"],
                "distance":chunk["distance"],
                "paper_id":self.paper_id

            }
        )
        for chunk in chunks]