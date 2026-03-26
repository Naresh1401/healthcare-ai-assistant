"""
Medical knowledge data loader.
Loads synthetic medical documents, chunks them, embeds with OpenAI embeddings,
and stores in ChromaDB for RAG retrieval.
"""

import os
import glob

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge"))
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data", "chromadb"))
COLLECTION_NAME = "medical_knowledge"


def load_documents(knowledge_dir: str = KNOWLEDGE_DIR) -> list:
    """Load all .txt files from the knowledge directory."""
    documents = []
    txt_files = glob.glob(os.path.join(knowledge_dir, "*.txt"))

    if not txt_files:
        raise FileNotFoundError(
            f"No .txt files found in {knowledge_dir}. "
            "Run `python -m src.knowledge.sample_guidelines` first."
        )

    for filepath in txt_files:
        loader = TextLoader(filepath, encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = os.path.basename(filepath)
            doc.metadata["category"] = _categorize_document(os.path.basename(filepath))
        documents.extend(docs)

    print(f"Loaded {len(documents)} documents from {len(txt_files)} files")
    return documents


def _categorize_document(filename: str) -> str:
    """Assign a category based on filename."""
    categories = {
        "diabetes": "Endocrinology",
        "hypertension": "Cardiovascular",
        "cardiac": "Cardiology",
        "drug_interaction": "Pharmacology",
        "symptom": "Diagnostics",
    }
    for key, category in categories.items():
        if key in filename.lower():
            return category
    return "General"


def chunk_documents(documents: list, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """Split documents into chunks using RecursiveCharacterTextSplitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
    return chunks


def create_vector_store(chunks: list, persist_dir: str = CHROMA_PERSIST_DIR) -> Chroma:
    """Embed chunks and store in ChromaDB."""
    os.makedirs(persist_dir, exist_ok=True)

    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=persist_dir,
    )

    print(f"Created vector store with {len(chunks)} embeddings at {persist_dir}")
    return vector_store


def get_vector_store(persist_dir: str = CHROMA_PERSIST_DIR) -> Chroma:
    """Load existing ChromaDB vector store."""
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    )
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )


def ingest_medical_knowledge():
    """Full ingestion pipeline: load → chunk → embed → store."""
    print("=" * 60)
    print("Medical Knowledge Ingestion Pipeline")
    print("=" * 60)

    documents = load_documents()
    chunks = chunk_documents(documents)
    vector_store = create_vector_store(chunks)

    # Verify with a test query
    results = vector_store.similarity_search("diabetes treatment", k=3)
    print(f"\nVerification - test query returned {len(results)} results")
    for i, doc in enumerate(results):
        print(f"  [{i+1}] {doc.metadata.get('source', 'unknown')} (score: {doc.metadata.get('category', 'N/A')})")

    print("\nIngestion complete.")
    return vector_store


if __name__ == "__main__":
    ingest_medical_knowledge()
