"""
AI-powered content chunking using Azure OpenAI.
Generates optimal learning chunks with titles, concepts, and quizzes.
Falls back to offline logic if Azure is not configured or fails.
"""
import json
import logging
import re
from typing import List, Dict, Any, Optional, Union
import asyncio

from app.config import settings

logger = logging.getLogger("AIChunker")


class AIChunker:
    """AI-powered content chunker using Azure OpenAI or offline fallback"""

    def __init__(self):
        self.client = None
        self.deployment_name = None

        # safely get settings (handle if config.py isn't updated yet)
        api_key = getattr(settings, "AZURE_OPENAI_API_KEY", None)
        endpoint = getattr(settings, "AZURE_OPENAI_ENDPOINT", None)
        deployment = getattr(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

        if api_key and endpoint:
            try:
                import openai  # azure openai needs openai package configured for azure
                openai.api_key = api_key
                openai.api_base = endpoint
                self.client = openai
                self.deployment_name = deployment
                logger.info("✅ Azure OpenAI client configured for AIChunker.")
            except Exception as e:
                logger.warning("⚠️ Failed to initialize Azure OpenAI client, falling back to offline chunker.")
                logger.debug(str(e))
        else:
            logger.info("ℹ️ Azure not configured; AIChunker will use offline fallback chunking.")


    async def generate_chunks(
        self,
        transcript: Optional[str] = None,
        title: str = "Untitled",
        duration: Optional[int] = None,
        units: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate chunk-cards.
        If `units` provided (structured output from PDF/PPTX processors), process per-unit preserving source.
        Otherwise use transcript string as a single unit.
        """
        results: List[Dict[str, Any]] = []
        # Prefer structured units if available
        if units:
            # Process each unit (serially to avoid huge parallel calls)
            for unit in units:
                text = unit.get("text", "")
                source = {"file": unit.get("file"), "page": unit.get("page"), "slide": unit.get("slide")}
                if self.client:
                    try:
                        chunk = await self._generate_with_azure(text, title, duration, source)
                        if isinstance(chunk, list):
                            # attach source to each produced chunk (if not provided)
                            for c in chunk:
                                c.setdefault("source", source)
                            results.extend(chunk)
                            continue
                    except Exception as e:
                        logger.warning(f"Azure generation failed for unit: {e}")
                # offline fallback chunking for this unit
                fallback = self._create_fallback_chunks_unit(text, title, source)
                results.extend(fallback)
            return results
        else:
            # single transcript mode
            text = transcript or ""
            if self.client:
                try:
                    return await self._generate_with_azure(text, title, duration, {"file": None})
                except Exception as e:
                    logger.warning(f"Azure generation failed for transcript: {e}")
            return self._create_fallback_chunks(text, {"file": None})

    async def _generate_with_azure(
        self,
        chunk_text: str,
        title: str,
        duration: Optional[int],
        source: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Call Azure OpenAI to generate chunk-cards for a piece of text"""
        # Build new ADH D-optimized prompt that returns chunk cards (see spec)
        prompt = self._build_chunking_prompt(chunk_text, title, duration)
        # Use a chat completion if available
        try:
            resp = self.client.ChatCompletion.create(
                deployment_id=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer for ADHD-friendly content. Return ONLY valid JSON as specified."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1500,
            )
            # response parsing: try to extract JSON
            text = ""
            if isinstance(resp, dict):
                # openai package style
                choices = resp.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "") or choices[0].get("text", "")
            else:
                text = str(resp)
            parsed = self._parse_chunks_response(text)
            # annotate source if missing
            for p in parsed:
                p.setdefault("source", source)
            return parsed
        except Exception as e:
            logger.error(f"Azure call failed: {e}")
            raise

    def _build_chunking_prompt(self, chunk_text: str, title: str, duration: Optional[int]) -> str:
        """Build the ADH D-optimized prompt (MANDATORY PROMPT TEMPLATE)"""
        duration_info = f"The total content duration is {duration} seconds." if duration else ""
        prompt = f"""Summarize the following content into a study card.

Rules:
- DO NOT ask questions
- DO NOT create Q/A pairs
- DO NOT explain verbosely
- Use concise bullet points only
- Generate a short, clear title
- Optimize for ADHD readability
- Preserve technical accuracy

Content:
{chunk_text}

Return ONLY valid JSON in this format:
{{
  "title": string,
  "content": string[],
  "topic": string
}}"""
        return prompt

    def _parse_chunks_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Try to extract JSON array of chunk-cards from freeform response.
        Validate and normalize fields, returning list of valid chunk objects.
        """
        # Try direct load
        data = None
        try:
            data = json.loads(response)
        except Exception:
            # try to find JSON object/array substring
            m = re.search(r'(\[.*\])', response, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(1))
                except Exception:
                    data = None
        if not data or not isinstance(data, list):
            raise ValueError("Model did not return parseable JSON array.")
        results = []
        for ch in data:
            if not self._validate_chunk(ch):
                logger.debug(f"Chunk validation failed for: {ch}")
                continue
            results.append(ch)
        return results

    def _validate_chunk(self, chunk: Dict[str, Any]) -> bool:
        """Validate required fields and apply safe defaults"""
        required_fields = ["title", "content", "topic"]
        if not all(field in chunk and chunk[field] for field in required_fields):
            return False
        if not isinstance(chunk["content"], list) or not (3 <= len(chunk["content"]) <= 5):
            return False
        # If metadata provided, ensure word count not exceeding 160
        md = chunk.get("metadata", {})
        wc = md.get("wordCount")
        if wc is not None and wc > 160:
            return False
        # Ensure content bullets satisfy length heuristics (6-14 words)
        for b in chunk["content"]:
            w = len(re.findall(r'\w+', b))
            if w < 3 or w > 20:  # allow a bit of slack
                # not strictly invalid; we'll accept but note it's a bit off
                pass
        # Provide defaults if missing
        chunk.setdefault("source", {})
        if "metadata" not in chunk:
            word_count = len(re.findall(r'\w+', " ".join(chunk["content"])))
            chunk["metadata"] = {
                "wordCount": word_count,
                "estimatedReadTimeSec": max(1, int(word_count / 2.5)),
                "difficulty": "medium",
                "energyLevel": "normal"
            }
        return True

    def _create_fallback_chunks_unit(self, text: str, title: str, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Offline chunking for a single unit (page/slide). Returns list of chunk-cards."""
        # Simple sentence-based chunker followed by bulletifier
        from math import ceil
        import re

        def split_sentences(s: str):
            return [ss.strip() for ss in re.split(r'(?<=[.!?])\s+', s) if ss.strip()]

        def word_count(s: str):
            return len(re.findall(r'\w+', s))

        sentences = split_sentences(text)
        # group sentences into chunks respecting target size 80-140, hard max 160
        chunks = []
        cur = []
        cur_w = 0
        TARGET_MIN = 80
        TARGET_MAX = 140
        HARD_MAX = 160
        for s in sentences:
            s_w = word_count(s)
            # attach short sentences to cur to avoid tiny chunks
            if cur_w + s_w <= TARGET_MAX or cur_w < TARGET_MIN:
                cur.append(s)
                cur_w += s_w
                # ensure we never exceed HARD_MAX
                if cur_w > HARD_MAX:
                    # pop last sentence and push chunk
                    last = cur.pop()
                    cur_w -= s_w
                    chunks.append(" ".join(cur))
                    cur = [last]
                    cur_w = s_w
            else:
                chunks.append(" ".join(cur))
                cur = [s]
                cur_w = s_w
        if cur:
            chunks.append(" ".join(cur))
        # Now convert each chunk into a chunk-card with bullets (3-5 bullets, 6-14 words)
        cards = []
        for i, ch in enumerate(chunks):
            # bulletify
            bullets = self._bulletify(ch)
            wordcount = len(re.findall(r'\w+', ch))
            md = {
                "wordCount": wordcount,
                "estimatedReadTimeSec": max(1, int(wordcount / 2.5)),
                "difficulty": "medium",
                "energyLevel": "normal",
            }
            card = {
                "title": (title + f" — Part {i+1}")[:80],
                "content": bullets,
                "topic": title or "General",
                "source": source,
                "metadata": md
            }
            cards.append(card)
        return cards

    def _create_fallback_chunks(self, text: str, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Treat the entire transcript as one unit and call unit chunker
        return self._create_fallback_chunks_unit(text, "Transcript", source)

    def _bulletify(self, text: str) -> List[str]:
        """
        Create 3-5 concise bullets (6-14 words each) from a chunk of text.
        Heuristic approach: split sentences and merge to meet bullet counts.
        """
        import re
        sents = [s.strip().rstrip('.') for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        # Start with sentences as candidates
        # Merge until we have between 3 and 5 bullets
        while len(sents) > 5:
            # merge the two shortest adjacent items
            lengths = [len(ss.split()) for ss in sents]
            idx = min(range(len(lengths)-1), key=lambda i: lengths[i]+lengths[i+1])
            sents[idx] = sents[idx] + " " + sents[idx+1]
            del sents[idx+1]
        while len(sents) < 3 and len(sents) > 1:
            sents[-2] = sents[-2] + " " + sents[-1]
            sents.pop()
        # Ensure each bullet is 6-14 words by merging/splitting commas if needed
        bullets = []
        for s in sents[:5]:
            w = len(s.split())
            if w < 6:
                # try to merge with next if exists
                bullets.append(s)
            elif w > 14:
                # split by comma
                parts = [p.strip() for p in s.split(',') if p.strip()]
                if len(parts) >= 2:
                    for p in parts:
                        bullets.append(p)
                    continue
                else:
                    # truncate to first 14 words
                    bullets.append(" ".join(s.split()[:14]))
            else:
                bullets.append(s)
        # final cleanup: trim bullets and ensure 3-5 bullets
        bullets = [b.strip() for b in bullets if b.strip()]
        if len(bullets) < 3:
            # fallback: chunk raw text into 3 roughly equal parts
            words = text.split()
            n = max(1, len(words)//3)
            bullets = [" ".join(words[i:i+n]) for i in range(0, min(len(words), n*3), n)]
        return [b.rstrip('.') for b in bullets[:5]]