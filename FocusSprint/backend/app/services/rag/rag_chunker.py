"""
Document RAG Chunker with Ollama LLM integration.
Includes availability checking and graceful fallback.
"""
import json
import logging
import httpx
from typing import List, Dict, Any, Optional

from .embedder import Embedder
from .vector_store import VectorStore
from .prompts import SYSTEM_PROMPT, CHUNK_PROMPT
from app.config import settings

logger = logging.getLogger("DocumentRAG")


class DocumentRAGChunker:
    """RAG-based document chunker with LLM synthesis."""
    
    def __init__(self):
        self.embedder = Embedder()
        self.store = VectorStore(dim=384)
        self._ollama_available: Optional[bool] = None
    
    async def check_ollama_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        if self._ollama_available is not None:
            return self._ollama_available
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Check Ollama health endpoint
                base_url = settings.OLLAMA_URL.replace("/api/generate", "")
                resp = await client.get(f"{base_url}/api/tags")
                self._ollama_available = resp.status_code == 200
                
                if self._ollama_available:
                    logger.info("✅ Ollama is available")
                else:
                    logger.warning(f"⚠️ Ollama returned status {resp.status_code}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
            self._ollama_available = False
        
        return self._ollama_available

    def index_units(self, structured_units: List[Dict]):
        """Index document units for semantic retrieval."""
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

    async def generate_chunks(self, document_title: str) -> List[Dict[str, Any]]:
        """
        Generate learning chunks from indexed document.
        Uses Ollama LLM if available, falls back to simple chunking otherwise.
        """
        # Check Ollama availability
        ollama_ok = await self.check_ollama_available()
        
        if not ollama_ok:
            logger.warning("⚠️ Ollama unavailable, using fallback chunking")
            return await self._fallback_chunking(document_title)
        
        return await self._llm_chunking(document_title)
    
    async def _llm_chunking(self, document_title: str) -> List[Dict[str, Any]]:
        """Generate chunks using Ollama LLM for semantic synthesis."""
        queries = [
            f"Core concepts in {document_title}",
            f"Key mechanisms and processes",
            f"Important definitions and principles",
            f"Practical or applied insights",
        ]

        chunks: List[Dict] = []

        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
            for query in queries:
                logger.info(f"🔍 RAG query: {query}")

                try:
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
                    
                    # Try to parse JSON response
                    try:
                        data = json.loads(raw)
                        if "chunks" in data:
                            chunks.extend(data["chunks"])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse LLM response as JSON for query: {query}")
                        continue
                        
                except httpx.TimeoutException:
                    logger.warning(f"Ollama timeout for query: {query}")
                    continue
                except Exception as e:
                    logger.error(f"LLM chunking error: {e}")
                    continue

        if not chunks:
            logger.warning("LLM generated no chunks, falling back")
            return await self._fallback_chunking(document_title)
            
        logger.info(f"✅ Generated {len(chunks)} chunks via Document RAG")
        return chunks
    
    async def _fallback_chunking(self, document_title: str) -> List[Dict[str, Any]]:
        """
        Fallback chunking when Ollama is unavailable.
        Uses semantic retrieval but creates simple structured chunks.
        """
        logger.info("📦 Using fallback chunking (no LLM)")
        
        # Use semantic queries to retrieve relevant content
        queries = [
            f"Main topic of {document_title}",
            "Key concepts",
            "Important details",
        ]
        
        chunks: List[Dict] = []
        seen_content = set()
        
        for idx, query in enumerate(queries, 1):
            try:
                query_emb = self.embedder.embed([query])
                context_blocks = self.store.search(query_emb, top_k=4)
                
                for block in context_blocks:
                    # Avoid duplicates
                    block_hash = hash(block[:100])
                    if block_hash in seen_content:
                        continue
                    seen_content.add(block_hash)
                    
                    # Create simple chunk from retrieved block
                    chunk = {
                        "title": f"Section {len(chunks) + 1}: {document_title}",
                        "summary": block[:200] + "..." if len(block) > 200 else block,
                        "bullets": self._extract_bullets(block),
                        "focus_words": self._extract_keywords(block),
                        "generation_strategy": "FALLBACK",
                    }
                    chunks.append(chunk)
                    
                    # Limit chunks
                    if len(chunks) >= 10:
                        break
                        
            except Exception as e:
                logger.warning(f"Fallback chunking error for query '{query}': {e}")
                continue
        
        if not chunks:
            # Absolute fallback: create one chunk from any content
            chunks.append({
                "title": document_title,
                "summary": "Content from uploaded document",
                "bullets": ["Document uploaded successfully", "Processing completed"],
                "focus_words": ["learning", "content"],
                "generation_strategy": "FALLBACK",
            })
        
        logger.info(f"📦 Fallback chunking produced {len(chunks)} chunks")
        return chunks
    
    def _extract_bullets(self, text: str, max_bullets: int = 5) -> List[str]:
        """Extract bullet points from text."""
        sentences = text.replace('\n', ' ').split('.')
        bullets = []
        
        for s in sentences:
            s = s.strip()
            if len(s) > 20 and len(s) < 200:
                bullets.append(s + ".")
                if len(bullets) >= max_bullets:
                    break
        
        return bullets if bullets else ["Key information from document"]
    
    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract simple keywords from text."""
        # Simple keyword extraction - words that appear capitalized or are longer
        words = text.split()
        keywords = []
        
        for word in words:
            clean = ''.join(c for c in word if c.isalnum())
            if len(clean) > 5 and clean[0].isupper():
                if clean.lower() not in [k.lower() for k in keywords]:
                    keywords.append(clean)
                    if len(keywords) >= max_keywords:
                        break
        
        return keywords if keywords else ["document", "learning", "content"]
