"""
vector_store.py

Creates, saves, loads and searches the FAISS vector database.
"""

from pathlib import Path

import faiss
import numpy as np


# ============================
# Paths
# ============================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "knowledge_base" / "processed"

EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
INDEX_PATH = PROCESSED_DIR / "faiss.index"


# ============================
# Vector Store
# ============================

class VectorStore:
    def __init__(self):
        self.index = None

    def create_index(self):
        """
        Create a FAISS index from embeddings.
        """
        embeddings = np.load(EMBEDDINGS_PATH).astype("float32")

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(embeddings)

        faiss.write_index(self.index, str(INDEX_PATH))

        print(f"✅ FAISS index created successfully.")
        print(f"Indexed {len(embeddings)} document chunks.")

    def load_index(self):
        """
        Load an existing FAISS index.
        """
        if not INDEX_PATH.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {INDEX_PATH}"
            )

        self.index = faiss.read_index(str(INDEX_PATH))

    def search(self, query_embedding, top_k=5):
        """
        Search the vector database.

        Parameters
        ----------
        query_embedding : numpy.ndarray
        top_k : int

        Returns
        -------
        distances, indices
        """

        if self.index is None:
            self.load_index()

        query_embedding = query_embedding.astype("float32")

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )

        return distances, indices


# ============================
# Test
# ============================

if __name__ == "__main__":

    store = VectorStore()

    store.create_index()