import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger("RAG.Embedder")

# ─────────────────────────────────────────────
# Singleton model (loaded once per process)
# ─────────────────────────────────────────────

_model: SentenceTransformer | None = None


def _load_model() -> SentenceTransformer:
    """
    Lazily load the embedding model once.
    """
    global _model

    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("🔌 Initializing SentenceTransformer | device=%s", device)

        _model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device=device,
        )

    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    RAG entry point.
    Used by document pipeline for embeddings.
    """
    if not texts:
        return np.empty((0, 384), dtype=np.float32)

    model = _load_model()

    return model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
