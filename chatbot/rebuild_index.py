"""
Rebuilds the AI knowledge base.

Database
    ↓
knowledge.json
    ↓
Chunks
    ↓
Embeddings
    ↓
FAISS Index
"""

import json
from pathlib import Path

from models.knowledge import Knowledge
from chatbot.vector_store import VectorStore
from chatbot.embeddings import EmbeddingModel


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "knowledge_base"

PROCESSED_DIR = RAW_DIR / "processed"

RAW_DIR.mkdir(exist_ok=True)

PROCESSED_DIR.mkdir(exist_ok=True)

KNOWLEDGE_PATH = RAW_DIR / "knowledge.json"

CHUNKS_PATH = PROCESSED_DIR / "chunks.json"


# ==========================================================
# REBUILD INDEX
# ==========================================================

def rebuild_index():

    articles = (

        Knowledge.query

        .filter_by(is_active=True)

        .order_by(Knowledge.id.asc())

        .all()

    )

    knowledge = []

    chunks = []

    for article in articles:

        item = {

            "id": article.id,

            "title": article.title,

            "category": article.category,

            "content": article.content

        }

        knowledge.append(item)

        chunks.append(item)

    # ---------------------------------------------
    # Save knowledge.json
    # ---------------------------------------------

    with open(
        KNOWLEDGE_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            knowledge,
            file,
            indent=4,
            ensure_ascii=False
        )

    # ---------------------------------------------
    # Save chunks.json
    # ---------------------------------------------

    with open(
        CHUNKS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=4,
            ensure_ascii=False
        )

    # ---------------------------------------------
    # Create embeddings
    # ---------------------------------------------

    model = EmbeddingModel()

    embeddings = []

    for chunk in chunks:

        embedding = model.embed_document(
            chunk["content"]
        )

        embeddings.append(embedding)

    # ---------------------------------------------
    # Build FAISS index
    # ---------------------------------------------

    store = VectorStore()

    store.build_index(embeddings)

    print()

    print("=" * 60)
    print("Knowledge Base Rebuilt Successfully")
    print("=" * 60)
    print(f"Articles : {len(articles)}")
    print(f"Chunks   : {len(chunks)}")
    print(f"Vectors  : {len(embeddings)}")
    print("=" * 60)


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    from app import app

    with app.app_context():

        rebuild_index()