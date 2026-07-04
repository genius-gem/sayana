from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SimilarityChecker:

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    # -----------------------------------------

    def similarity_score(self, text1, text2):

        embeddings = self.model.encode(
            [text1, text2],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        score = cosine_similarity(
            [embeddings[0]],
            [embeddings[1]]
        )[0][0]

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