from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_and_chunk_pdf(file_path: str):
    reader = PdfReader(file_path)

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            documents.append({
                "text": text,
                "page": page_number
            })

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = []

    for document in documents:
        split_texts = splitter.split_text(document["text"])

        for text in split_texts:
            chunks.append({
                "text": text,
                "page": document["page"]
            })

    return chunks