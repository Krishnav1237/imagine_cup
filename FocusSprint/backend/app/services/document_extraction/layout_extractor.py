from pathlib import Path
from typing import List, Dict

from .pdf_layout import extract_pdf_layout
from .pptx_layout import extract_pptx_layout


def extract_layout_units(file_path: str) -> List[Dict]:
    """
    Returns raw layout-aware blocks.
    NO semantic cleanup.
    """

    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        return extract_pdf_layout(file_path)

    if path.suffix.lower() == ".pptx":
        return extract_pptx_layout(
            file_path=str(path),
            file_name=path.name,
        )

    raise RuntimeError(f"Unsupported document format: {path.suffix}")
