import pdfplumber
from typing import List, Dict


def extract_pdf_layout(file_path: str) -> List[Dict]:
    """
    Extract raw, layout-aware text blocks from a PDF.
    No semantic cleanup, no filtering.
    """
    units: List[Dict] = []

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            units.append({
                "text": text.strip(),
                "file": file_path,
                "page": page_num,
                "slide": None
            })

    return units
