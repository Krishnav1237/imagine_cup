"""
Embedding service abstraction.
Uses Ollama embeddings API.
"""

import httpx
import logging
from typing import List

from app.config import settings

logger = logging.getLogger("Embeddings")


DEFAULT_EMBED_MODEL = getattr(
    settings,
    "OLLAMA_EMBED_MODEL",
    "nomic-embed-text"
)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Ollama.

    Supports both old and new Ollama embedding response formats.
    """
    if not texts:
        return []

    try:
        payload = {
            "model": DEFAULT_EMBED_MODEL,
            "input": texts,  # ✅ CORRECT KEY
        }

        resp = httpx.post(
            f"{settings.OLLAMA_URL}/api/embeddings",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()

        # ✅ New Ollama format
        if "data" in data:
            return [item["embedding"] for item in data["data"]]

        # ✅ Old Ollama format
        if "embedding" in data:
            return [data["embedding"]]

        raise RuntimeError(f"Unexpected embedding response: {data}")

    except Exception as e:
        logger.error(f"❌ Embedding failed: {e}")
        raise RuntimeError("Embedding generation failed") from e
