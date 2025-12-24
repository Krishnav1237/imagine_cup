import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatIP(dim)
        self.payloads: list[str] = []

    def add(self, embeddings: np.ndarray, payloads: list[str]):
        self.index.add(embeddings)
        self.payloads.extend(payloads)

    def search(self, query_embedding: np.ndarray, top_k: int = 6) -> list[str]:
        scores, indices = self.index.search(query_embedding, top_k)
        return [
            self.payloads[i]
            for i in indices[0]
            if i != -1
        ]


# ---- alias for document RAG ----
DocumentVectorStore = VectorStore
