from app.rag.langchain_embeddings import embeddings

vector=embeddings.embed_query(
    "What methodlogy does this research paper used?"

)

print("EMbeddings generated")
print("dimensin:",len(vector))
print("firdt 5:",vector[:5])