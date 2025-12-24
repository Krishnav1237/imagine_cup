from typing import List, Dict
from app.services.chunking.chunk_schema import ChunkCard


def compile_video_chunks(
    vlm_segments: List[Dict],
    document_title: str
) -> List[ChunkCard]:
    """
    Converts VLM semantic segments into ChunkCards.
    Assumes VLM already performed semantic grouping.
    """

    chunks: List[ChunkCard] = []

    for seg in vlm_segments:
        chunks.append({
            "title": seg["title"],
            "summary": seg["summary"],
            "bullets": seg["bullets"],
            "focus_words": seg.get("focus_words", []),
            "source": {
                "file": seg.get("file"),
                "page": None,
                "slide": None,
                "timestamp": seg.get("timestamp"),
            }
        })

    return chunks
