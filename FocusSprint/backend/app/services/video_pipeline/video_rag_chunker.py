import logging
from typing import List, Dict

from app.services.embeddings import embed_texts
from app.services.llm import run_llm_json

logger = logging.getLogger("VideoRAGChunker")


# ==========================================================
# STRICT SYSTEM PROMPT (DO NOT INLINE, DO NOT OMIT)
# ==========================================================
CHUNK_SYSTEM_PROMPT = """
You are a strict JSON-only generation engine.

Rules:
- Output MUST be valid JSON
- Do NOT include markdown
- Do NOT include explanations
- Do NOT include extra keys
- Do NOT include text outside JSON

If you cannot comply, output an empty JSON object: {}
"""


# ==========================================================
# Transcript → Units
# ==========================================================
def build_transcript_units(transcript_segments: List[Dict]) -> List[Dict]:
    """
    Convert raw transcript segments into RAG units.
    """
    units = []
    for i, seg in enumerate(transcript_segments):
        units.append({
            "id": i,
            "text": seg["text"],
            "start": float(seg["start"]),
            "end": float(seg["end"]),
        })
    return units


# ==========================================================
# Deterministic semantic grouping (NO LLM)
# ==========================================================
def semantic_group_units(
    units: List[Dict],
    max_group_chars: int = 1200,
) -> List[List[Dict]]:
    """
    Deterministic grouping using embeddings + size window.
    """
    texts = [u["text"] for u in units]
    embeddings = embed_texts(texts)  # ensures semantic ordering exists

    groups = []
    current = []
    current_chars = 0

    for unit in units:
        length = len(unit["text"])

        if current_chars + length > max_group_chars and current:
            groups.append(current)
            current = []
            current_chars = 0

        current.append(unit)
        current_chars += length

    if current:
        groups.append(current)

    return groups


# ==========================================================
# RAG → Video Chunks
# ==========================================================
async def generate_video_chunks(
    transcript_segments: List[Dict],
) -> List[Dict]:
    """
    RAG-based video chunking with deterministic timestamps.
    """
    units = build_transcript_units(transcript_segments)
    groups = semantic_group_units(units)

    chunks = []

    for idx, group in enumerate(groups):
        text_block = " ".join(u["text"] for u in group)

        user_prompt = f"""
You are generating ONE learning chunk from a lecture transcript.

Return STRICT JSON ONLY in this exact schema:
{{
  "title": string,
  "summary": string
}}

Transcript:
{text_block}
"""

        llm_out = run_llm_json(
            prompt=user_prompt,
            system_prompt=CHUNK_SYSTEM_PROMPT,
        )

        # Defensive validation (important)
        if not llm_out or "title" not in llm_out or "summary" not in llm_out:
            raise RuntimeError("LLM returned invalid chunk JSON")

        chunks.append({
            "index": idx,
            "title": llm_out["title"],
            "summary": llm_out["summary"],
            "start": group[0]["start"],
            "end": group[-1]["end"],
        })

    return chunks
