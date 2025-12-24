from typing import List, Optional, TypedDict


class SourceRef(TypedDict):
    file: Optional[str]
    page: Optional[int]
    slide: Optional[int]
    timestamp: Optional[float]


class ChunkCard(TypedDict):
    title: str
    summary: str
    bullets: List[str]
    focus_words: List[str]
    source: SourceRef
