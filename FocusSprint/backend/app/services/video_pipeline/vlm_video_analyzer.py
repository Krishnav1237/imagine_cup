from typing import List, Dict
from app.services.vlm.local_vlm_processor import analyze_frames
from app.services.vlm.frame_sampler import sample_frames


async def analyze_video_segments(
    video_path: str,
    segments: List[Dict]
) -> List[Dict]:
    analyzed_segments = []

    for seg in segments:
        frames = sample_frames(
            video_path=video_path,
            start=seg["start"],
            end=seg["end"]
        )

        semantic = await analyze_frames(frames)

        analyzed_segments.append({
            "title": semantic["title"],
            "summary": semantic["summary"],
            "bullets": semantic["bullets"],
            "focus_words": semantic.get("focus_words", []),
            "timestamp": seg["start"]
        })

    return analyzed_segments
