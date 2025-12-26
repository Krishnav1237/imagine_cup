import json
import logging
import time
from typing import List, Dict

import httpx
from app.config import settings

logger = logging.getLogger("OllamaCardCompiler")

# ─────────────────────────────────────────────
# Ollama configuration
# ─────────────────────────────────────────────
OLLAMA_MODEL = settings.OLLAMA_MODEL
OLLAMA_URL = getattr(
    settings,
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)

# Conservative safety limits for llama3 8B Q4
MAX_PROMPT_CHARS = 14_000
MAX_UNIT_CHARS = 2_500

SYSTEM_PROMPT = """
You are a knowledge distillation engine.

Your responsibilities:
- Remove academic framing, course metadata, objectives, syllabus language
- Remove repetition, filler, and instructional phrasing
- Extract ONLY real, transferable knowledge
- Merge fragmented ideas into coherent concepts
- Rename titles to reflect the actual concept
- Ignore slide/page structure when it does not matter
- Never mention lectures, courses, slides, chapters, or exams

Output JSON only. No prose.
"""

# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────
def _sanitize_units_for_prompt(units: List[Dict]) -> List[Dict]:
    """Reduce layout-extracted units to LLM-safe payload."""
    safe_units: List[Dict] = []

    for u in units:
        text = u.get("text")
        if not isinstance(text, str):
            continue

        text = text.strip()
        if not text:
            continue

        safe_units.append({
            "text": text[:MAX_UNIT_CHARS],
            "page": u.get("page"),
            "slide": u.get("slide"),
        })

    return safe_units


def _recover_truncated_json(text: str) -> str:
    """
    Attempt to recover valid JSON if Ollama cut output mid-generation.
    """
    text = text.strip()

    if text.endswith("}"):
        return text

    logger.warning("⚠️ Ollama response truncated, attempting recovery")

    last_brace = text.rfind("}")
    if last_brace == -1:
        raise RuntimeError("No JSON object found in Ollama output")

    return text[: last_brace + 1]


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────
async def compile_cards(
    structured_units: List[Dict],
    document_title: str,
) -> List[Dict]:
    """Convert structured document units into learning cards via Ollama."""

    logger.info("🧠 Ollama compilation started")
    logger.info("📘 Document title: %s", document_title)
    logger.info("📦 Raw units received: %d", len(structured_units))
    logger.info("🤖 Ollama model: %s", OLLAMA_MODEL)
    logger.info("🌐 Ollama endpoint: %s", OLLAMA_URL)

    # ─────────────────────────────────────────────
    # 1. Sanitize input
    # ─────────────────────────────────────────────
    safe_units = _sanitize_units_for_prompt(structured_units)

    if not safe_units:
        raise RuntimeError("No valid text units after sanitization")

    logger.info(
        "🧹 Sanitized units | count=%d | max_unit_chars=%d",
        len(safe_units),
        MAX_UNIT_CHARS,
    )

    # ─────────────────────────────────────────────
    # 2. Build prompt
    # ─────────────────────────────────────────────
    prompt = f"""
{SYSTEM_PROMPT}

Transform the following extracted content into learning chunks.

Rules:
- Generate AT MOST 4 chunks
- One concept per chunk
- 3–6 bullets per chunk
- Each bullet ≤ 20 words
- One-line summary ≤ 20 words
- Extract 3–6 focus words
- Prefer conceptual grouping over layout grouping
- Use document title ONLY if conceptually relevant

Return ONLY valid JSON in this schema:

{{
  "chunks": [
    {{
      "title": "string",
      "summary": "string",
      "bullets": ["string"],
      "focus_words": ["string"],
      "source": {{
        "file": "string",
        "page": number|null,
        "slide": number|null
      }}
    }}
  ]
}}

INPUT:
{json.dumps({
    "document_title": document_title,
    "content": safe_units
}, ensure_ascii=False)}
"""

    if len(prompt) > MAX_PROMPT_CHARS:
        raise RuntimeError(
            f"Prompt too large ({len(prompt)} chars), exceeds limit"
        )

    logger.info(
        "🧾 Prompt stats | chars=%d | units=%d",
        len(prompt),
        len(safe_units),
    )

    # ─────────────────────────────────────────────
    # 3. Ollama request
    # ─────────────────────────────────────────────
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "num_ctx": 3072,
            "num_predict": 768,
            "temperature": 0.2,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
        },
    }

    logger.info(
        "🛡️ Ollama safety limits | ctx=%d | predict=%d | temp=%.2f",
        payload["options"]["num_ctx"],
        payload["options"]["num_predict"],
        payload["options"]["temperature"],
    )

    start_time = time.time()

    async with httpx.AsyncClient(timeout=300) as client:
        try:
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
        except Exception:
            logger.warning("⚠️ Ollama failed, retrying with stricter limits")

            payload["options"]["num_ctx"] = 2048
            payload["options"]["num_predict"] = 512

            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()

    elapsed = time.time() - start_time
    logger.info("⏱️ Ollama responded in %.2f seconds", elapsed)

    # ─────────────────────────────────────────────
    # 4. Parse response safely
    # ─────────────────────────────────────────────
    raw = resp.json()
    response_text = raw.get("response")

    if not isinstance(response_text, str):
        raise RuntimeError("Malformed Ollama response")

    logger.info(
        "📥 Ollama raw response received | chars=%d",
        len(response_text),
    )

    try:
        response_text = _recover_truncated_json(response_text)
        data = json.loads(response_text)
    except Exception as e:
        logger.error("❌ Ollama returned invalid JSON")
        logger.error("🧾 Raw output:\n%s", response_text)
        raise RuntimeError("Ollama returned invalid JSON") from e

    chunks = data.get("chunks")
    if not isinstance(chunks, list):
        raise RuntimeError("Ollama response missing 'chunks' array")

    logger.info("✅ Ollama compilation successful")
    logger.info("📊 Chunks generated: %d", len(chunks))

    for c in chunks:
        c.setdefault("generation_model", OLLAMA_MODEL)
        c.setdefault("generation_strategy", "RAG")

    return chunks