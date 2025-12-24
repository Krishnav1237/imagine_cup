"""
RAG (Retrieval-Augmented Generation) services.

This package provides:
- Embedding generation
- Vector indexing (FAISS)
- Top-k semantic retrieval for documents
"""

from .embedder import embed_texts
from .vector_store import DocumentVectorStore
from .retriever import retrieve_relevant_units
from .budget_selector import select_groups_by_char_budget

__all__ = [
    "embed_texts",
    "DocumentVectorStore",
    "retrieve_relevant_units",
]
