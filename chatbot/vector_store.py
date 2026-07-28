"""
vector_store.py

Creates, saves, loads and searches the vector database
using scikit-learn NearestNeighbors.
"""

from pathlib import Path

import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors


# ============================
# Paths
# ============================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "knowledge_base" / "processed"

EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"

INDEX_PATH = PROCESSED_DIR / "nearest_neighbors.pkl"


# ============================
# Vector Store
# ============================

class VectorStore:

    def __init__(self):

        self.index = None

    # ------------------------------------

    def create_index(self):

        """
        Create a NearestNeighbors index.
        """

        embeddings = np.load(
            EMBEDDINGS_PATH
        ).astype("float32")

        self.index = NearestNeighbors(

            n_neighbors=5,

            metric="cosine",

            algorithm="brute"

        )

        self.index.fit(
            embeddings
        )

        joblib.dump(

            self.index,

            INDEX_PATH

        )

        print()

        print("=" * 60)

        print("NearestNeighbors index created successfully.")

        print(f"Indexed {len(embeddings)} document chunks.")

        print(f"Saved To : {INDEX_PATH}")

        print("=" * 60)

    # ------------------------------------

    def load_index(self):

        """
        Load the saved NearestNeighbors model.
        """

        if not INDEX_PATH.exists():

            raise FileNotFoundError(

                f"Index not found: {INDEX_PATH}"

            )

        self.index = joblib.load(

            INDEX_PATH

        )

    # ------------------------------------

    def search(

        self,

        query_embedding,

        top_k=5

    ):

        """
        Search the vector database.
        """

        if self.index is None:

            self.load_index()

        distances, indices = self.index.kneighbors(

            query_embedding,

            n_neighbors=top_k

        )

        return distances, indices


# ============================
# Test
# ============================

if __name__ == "__main__":

    store = VectorStore()

    store.create_index()