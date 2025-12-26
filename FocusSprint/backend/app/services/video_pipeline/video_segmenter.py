from typing import List, Dict
from app.services.vlm.scene_segmenter import segment_scenes


def segment_video(video_path: str) -> List[Dict]:
    """
    Returns time-based segments for semantic analysis.
    """
    return segment_scenes(video_path)
