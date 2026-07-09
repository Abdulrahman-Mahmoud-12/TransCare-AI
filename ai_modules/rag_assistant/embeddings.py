import os
from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_model():
    """
    Loads a local sentence-transformers embedding model. Runs entirely on-device
    (CPU is fine for this project's scale) — no API key, no rate limits, no
    network dependency at query time.

    Model default: sentence-transformers/all-MiniLM-L6-v2
      - 384-dim vectors, ~80MB download (cached after first run)
      - Fast and solid quality for short retail text (product names,
        categories, offer descriptions)

    Override via EMBEDDING_MODEL in .env if you want a different
    sentence-transformers model (e.g. a multilingual one for Arabic + English
    product names — see note below).
    """
    embedding_model_name = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    return HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )