"""
similarity.py

Computes semantic similarity using FastEmbed.
"""

import numpy as np
from fastembed import TextEmbedding


class SimilarityChecker:

    def __init__(self):

        print("Loading similarity model...")

        self.model = TextEmbedding()

        print("Similarity model loaded successfully.")

    # -----------------------------------------

    def _embed(self, text):

        embedding = list(
            self.model.embed([text])
        )[0]

        embedding = np.array(
            embedding,
            dtype="float32"
        )

        embedding = embedding / np.linalg.norm(
            embedding
        )

        return embedding

    # -----------------------------------------

    def similarity_score(self, text1, text2):

        emb1 = self._embed(text1)

        emb2 = self._embed(text2)

        score = np.dot(
            emb1,
            emb2
        )

        return float(score)

    # -----------------------------------------

    def is_similar(
        self,
        text1,
        text2,
        threshold=0.85
    ):

        score = self.similarity_score(
            text1,
            text2
        )

        return score >= threshold