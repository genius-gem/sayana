"""
embeddings.py

Generates and manages embeddings for the Sayana Press RAG chatbot.
"""

import json
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding


# =====================================
# Paths
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "knowledge_base" / "processed"

CHUNKS_PATH = PROCESSED_DIR / "chunks.json"

EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"


# =====================================
# Embedding Model
# =====================================

class EmbeddingModel:

    def __init__(self):

        print("Loading embedding model...")

        self.model = TextEmbedding()

        print("Embedding model loaded successfully.")

    # ---------------------------------

    def embed_query(self, query):

        """
        Generate embedding for a user question.
        """

        embedding = list(
            self.model.embed([query])
        )[0]

        embedding = np.array(
            embedding,
            dtype="float32"
        )

        embedding = embedding / np.linalg.norm(
            embedding
        )

        return embedding.reshape(1, -1)

    # ---------------------------------

    def embed_documents(self, documents):

        """
        Generate embeddings for multiple documents.
        """

        embeddings = np.array(
            list(self.model.embed(documents)),
            dtype="float32"
        )

        norms = np.linalg.norm(
            embeddings,
            axis=1,
            keepdims=True
        )

        embeddings = embeddings / norms

        return embeddings

    # ---------------------------------

    def save_embeddings(self):

        """
        Read chunks.json and generate embeddings.
        """

        with open(
            CHUNKS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            chunks = json.load(file)

        documents = []

        for chunk in chunks:

            text = f"""
Category:
{chunk['category']}

Title:
{chunk['title']}

Content:
{chunk['content']}
"""

            documents.append(text)

        embeddings = self.embed_documents(
            documents
        )

        np.save(
            EMBEDDINGS_PATH,
            embeddings
        )

        print()

        print("=" * 60)

        print("Embeddings generated successfully.")

        print(f"Total Chunks : {len(chunks)}")

        print(f"Embedding Size : {embeddings.shape[1]}")

        print(f"Saved To : {EMBEDDINGS_PATH}")

        print("=" * 60)

    # ---------------------------------

    def load_embeddings(self):

        """
        Load saved embeddings.
        """

        if not EMBEDDINGS_PATH.exists():

            raise FileNotFoundError(
                "embeddings.npy not found."
            )

        return np.load(
            EMBEDDINGS_PATH
        )


# =====================================
# Test
# =====================================

if __name__ == "__main__":

    embedding_model = EmbeddingModel()

    embedding_model.save_embeddings()