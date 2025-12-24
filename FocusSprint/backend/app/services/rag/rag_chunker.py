import json
import logging
import httpx

from .embedder import Embedder
from .vector_store import VectorStore
from .prompts import SYSTEM_PROMPT, CHUNK_PROMPT
from app.config import settings

logger = logging.getLogger("DocumentRAG")

class DocumentRAGChunker:
    def __init__(self):
        self.embedder = Embedder()
        self.store = VectorStore(dim=384)

    def index_units(self, structured_units: list[dict]):
        texts = []

        for u in structured_units:
            text = u.get("text")
            if text and text.strip():
                texts.append(text.strip())

        if not texts:
            raise RuntimeError("No text found for RAG indexing")

        embeddings = self.embedder.embed(texts)
        self.store.add(embeddings, texts)

        logger.info(f"📚 Indexed {len(texts)} document units for RAG")

    async def generate_chunks(self, document_title: str) -> list[dict]:
        queries = [
            f"Core concepts in {document_title}",
            f"Key mechanisms and processes",
            f"Important definitions and principles",
            f"Practical or applied insights",
        ]

        chunks: list[dict] = []

        async with httpx.AsyncClient(timeout=120) as client:
            for query in queries:
                logger.info(f"🔍 RAG query: {query}")

                query_emb = self.embedder.embed([query])
                context_blocks = self.store.search(query_emb, top_k=6)

                if not context_blocks:
                    continue

                prompt = (
                    SYSTEM_PROMPT
                    + "\n\n"
                    + CHUNK_PROMPT.format(
                        context="\n\n".join(context_blocks)
                    )
                )

                resp = await client.post(
                    settings.OLLAMA_URL,
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                    },
                )
                resp.raise_for_status()

                raw = resp.json().get("response", "")
                data = json.loads(raw)

                if "chunks" in data:
                    chunks.extend(data["chunks"])

        logger.info(f"✅ Generated {len(chunks)} chunks via Document RAG")
        return chunks
