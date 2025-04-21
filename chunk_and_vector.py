# rag_pipeline/chunk_and_vector.py

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

def load_markdown_documents_with_metadata(metadata_records):
    documents = []
    for md_path, metadata in metadata_records:
        text = md_path.read_text(encoding="utf-8")
        if not text.strip():
            continue
        doc = Document(page_content=text, metadata=metadata)
        documents.append(doc)
    return documents

def hybrid_chunking(documents, threshold=3000):
    chunks = []
    for doc in documents:
        if len(doc.page_content.strip()) <= threshold:
            chunks.append(doc)
        else:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1800, chunk_overlap=300)
            split_docs = splitter.split_documents([doc])
            for chunk in split_docs:
                chunk.metadata.update(doc.metadata)
            chunks.extend(split_docs)
    return chunks

def create_vector_database(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="scientific_rag_xml",
        persist_directory="/content/db"
    )
    return vector_db
