from pptx import Presentation
from typing import List, Dict


def extract_pptx_layout(
    *,
    file_path: str,
    file_name: str,
) -> List[Dict]:
    """
    Layout-aware PPTX extraction.

    - Slide-based
    - Shape-preserving
    - No semantic interpretation
    """
    prs = Presentation(file_path)
    units: List[Dict] = []

    for slide_idx, slide in enumerate(prs.slides, start=1):
        parts = []

        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                text = shape.text.strip()
                if text:
                    parts.append(text)

        if not parts:
            continue

        units.append({
            "text": "\n".join(parts),
            "source": {
                "file": file_name,
                "page": None,
                "slide": slide_idx,
            }
        })

    return units
