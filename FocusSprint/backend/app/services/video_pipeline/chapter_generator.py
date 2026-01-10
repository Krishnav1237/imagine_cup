import json
import logging
import httpx
from typing import List, Dict, Any, Optional

from app.config import settings

logger = logging.getLogger("ChapterGenerator")


SYSTEM_PROMPT = """
You are a precise video chaptering engine.

You are given a transcript as a JSON array of segments. Each segment looks like:
{ "index": number, "start": float, "end": float, "text": string }

Your task:
- Group these segments into coherent chapters.
- Use ONLY the provided segment indices to define chapter boundaries.
- DO NOT invent timestamps or durations.

Return JSON ONLY in this format (no prose, no comments):
{
  "chapters": [
    {
      "index": number,          // 0-based chapter index
      "title": string,
      "summary": string,
      "start_index": number,    // 0-based transcript segment index (inclusive)
      "end_index": number       // 0-based transcript segment index (inclusive)
    }
  ]
}

Rules:
- 4–12 chapters for most videos.
- start_index and end_index must be integers within the valid index range.
- start_index <= end_index for each chapter.
- Indices should be monotonically increasing across chapters.
"""


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _extract_json_block(raw: str) -> Optional[str]:
    """
    Extract a JSON object/array from LLM prose.

    Strategy:
    - Look for the largest {...} block, then [...], and return the first
      substring that parses as JSON.
    """
    # Try object first
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = raw[start : end + 1]
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    # Then try array
    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1 and end > start:
        candidate = raw[start : end + 1]
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    return None


def _validate_transcript_monotonic(transcript_segments: List[Dict[str, Any]]) -> None:
    """
    Ensure transcript timestamps are monotonically increasing and non-overlapping.
    """
    if not transcript_segments:
        raise RuntimeError("Transcript is empty")

    prev_end = None
    for seg in transcript_segments:
        start = float(seg["start"])
        end = float(seg["end"])
        if end < start:
            raise RuntimeError("Transcript segment has negative duration")
        if prev_end is not None and start < prev_end:
            raise RuntimeError("Transcript timestamps are not monotonic")
        prev_end = end


def _build_chapters_from_indices(
    raw_chapters: Any, transcript_segments: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Convert LLM chapter definitions (by indices) into deterministic timestamped chapters.

    Enforces:
    - contiguous index ranges
    - monotonic, non-overlapping timestamps
    """
    _validate_transcript_monotonic(transcript_segments)

    if not isinstance(raw_chapters, list) or not raw_chapters:
        raise RuntimeError("LLM JSON missing non-empty 'chapters' list")

    n = len(transcript_segments)
    total_chapters = len(raw_chapters)

    normalized: List[Dict[str, Any]] = []
    current_start_index = 0

    for i, ch in enumerate(raw_chapters):
        title = str(ch.get("title") or f"Chapter {i+1}")
        summary = str(ch.get("summary") or "")

        # Best-effort parsing of indices; fall back to sequential assignment.
        try:
            start_idx_raw = int(ch.get("start_index"))
        except (TypeError, ValueError):
            start_idx_raw = current_start_index

        try:
            end_idx_raw = int(ch.get("end_index"))
        except (TypeError, ValueError):
            end_idx_raw = start_idx_raw

        # Enforce contiguous non-overlapping ranges.
        # First chapter always starts at 0; subsequent chapters pick up
        # where the previous one ended.
        if i == 0:
            start_index = 0
        else:
            start_index = current_start_index

        # Use the model's suggested end index as an upper bound, but ensure:
        # - end_index >= start_index
        # - enough room remains for subsequent chapters
        end_index = max(start_index, min(end_idx_raw, n - 1))

        remaining_chapters = total_chapters - i - 1
        max_end_for_this = n - 1 - remaining_chapters
        if end_index > max_end_for_this:
            end_index = max_end_for_this

        # Last chapter always extends to the final segment.
        if i == total_chapters - 1:
            end_index = n - 1

        if start_index > end_index:
            # This should not happen with the above guards, but be explicit.
            start_index = end_index

        chapter = {
            "index": i,
            "title": title,
            "summary": summary,
            "start_index": start_index,
            "end_index": end_index,
            "start": float(transcript_segments[start_index]["start"]),
            "end": float(transcript_segments[end_index]["end"]),
        }
        normalized.append(chapter)

        current_start_index = end_index + 1
        if current_start_index >= n:
            # No segments left; truncate any remaining chapters.
            break

    if not normalized:
        raise RuntimeError("No valid chapters produced from indices")

    return normalized


# ─────────────────────────────────────────────
# Main API
# ─────────────────────────────────────────────
async def generate_video_chapters(
    transcript_segments: List[Dict],
) -> Dict:
    # Attach explicit indices so the LLM can reference segments deterministically.
    indexed_segments = [
        {
            "index": i,
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": seg.get("text", ""),
        }
        for i, seg in enumerate(transcript_segments)
    ]

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\nTranscript segments (JSON):\n{json.dumps(indexed_segments, ensure_ascii=False)}",
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(settings.OLLAMA_URL, json=payload)
        resp.raise_for_status()

    raw = resp.json().get("response")
    if not raw:
        raise RuntimeError("LLM returned empty response")

    # 1️⃣ Try direct JSON
    try:
        obj = json.loads(raw)
    except Exception:
        logger.warning("LLM returned non-JSON, attempting JSON block extraction")
        json_str = _extract_json_block(raw)
        if not json_str:
            raise RuntimeError("LLM output did not contain a valid JSON block")
        try:
            obj = json.loads(json_str)
        except Exception as e:
            raise RuntimeError("Failed to parse JSON from extracted block") from e

    chapters_raw = obj.get("chapters")
    chapters = _build_chapters_from_indices(chapters_raw, transcript_segments)

    return {"chapters": chapters}
