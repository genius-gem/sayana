"""
retriever.py

Retrieves the most relevant knowledge chunks
from the FAISS vector database.
"""

import json
from pathlib import Path

from chatbot.embeddings import EmbeddingModel
from chatbot.vector_store import VectorStore


# ============================
# Paths
# ============================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "knowledge_base" / "processed"

CHUNKS_PATH = PROCESSED_DIR / "chunks.json"


# ============================
# Retriever
# ============================

class Retriever:

    def __init__(self):

        self.embedding_model = EmbeddingModel()

        self.vector_store = VectorStore()

        self.vector_store.load_index()

        with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
            self.chunks = json.load(file)

    def retrieve(self, query, top_k=5):

        """
        Retrieve the most relevant chunks.
        """

        query_embedding = self.embedding_model.embed_query(query)

        distances, indices = self.vector_store.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(distances[0], indices[0]):

            if index == -1:
                continue

            chunk = self.chunks[index].copy()

            chunk["score"] = float(score)

            results.append(chunk)

        return results


# ============================
# Test
# ============================

if __name__ == "__main__":

    retriever = Retriever()

    results = retriever.retrieve(
        "Can breastfeeding mothers use Sayana Press?"
    )

    for result in results:

        print("=" * 60)

        print("Title:", result["title"])

        print("Category:", result["category"])

        print("Score:", result["score"])

        print(result["content"])