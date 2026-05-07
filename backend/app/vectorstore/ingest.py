from pathlib import Path
import shutil

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


BACKEND_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = BACKEND_DIR / "knowledge_base"
CHROMA_DIR = BACKEND_DIR / "chroma_db"


def load_documents():
    documents = []

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.md"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        documents.extend(loader.load())

    return documents


def ingest_documents():
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    documents = load_documents()

    if not documents:
        raise ValueError("No documents found in knowledge_base folder.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR)
    )

    print(f"Ingested {len(chunks)} chunks into {CHROMA_DIR}")


if __name__ == "__main__":
    ingest_documents()