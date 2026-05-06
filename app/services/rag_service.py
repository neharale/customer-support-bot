from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


BACKEND_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BACKEND_DIR / "chroma_db"


class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.db = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=self.embeddings
        )

    def retrieve(self, query: str, k: int = 3):
        results = self.db.similarity_search_with_score(query, k=k)

        documents = []
        scores = []

        for doc, score in results:
            documents.append(doc.page_content)
            scores.append(score)

        return documents, scores

    def calculate_confidence(self, scores: list[float]) -> float:
        if not scores:
            return 0.0

        best_score = min(scores)

        if best_score <= 0.7:
            return 0.90
        elif best_score <= 1.1:
            return 0.75
        elif best_score <= 1.6:
            return 0.60
        else:
            return 0.40