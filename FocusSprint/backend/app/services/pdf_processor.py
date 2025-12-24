"""
PDF processing service.
PURE extraction only.
NO cleaning. NO filtering. NO semantics.
"""

import io
import logging
from typing import Optional
import pdfplumber
import PyPDF2

logger = logging.getLogger("PDFProcessor")


class PDFProcessor:
    """
    Raw PDF text extractor.
    Output is intentionally unfiltered.
    """

    def extract_text(self, file_data: bytes) -> Optional[str]:
        logger.info("📄 Extracting raw PDF text")

        text = self._extract_with_pdfplumber(file_data)

        if not text or len(text.strip()) < 50:
            logger.warning("⚠️ pdfplumber low output, falling back to PyPDF2")
            text = self._extract_with_pypdf2(file_data)

        if not text:
            logger.warning("⚠️ No text extracted from PDF")

        logger.info(f"✅ Raw PDF text length: {len(text) if text else 0}")
        return text

    def _extract_with_pdfplumber(self, file_data: bytes) -> Optional[str]:
        try:
            pages = []
            with pdfplumber.open(io.BytesIO(file_data)) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    txt = page.extract_text()
                    if txt:
                        pages.append(f"\n--- Page {i} ---\n{txt}")
            return "\n".join(pages)
        except Exception as e:
            logger.exception("❌ pdfplumber extraction failed")
            return None

    def _extract_with_pypdf2(self, file_data: bytes) -> Optional[str]:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_data))
            pages = []
            for i, page in enumerate(reader.pages, start=1):
                txt = page.extract_text()
                if txt:
                    pages.append(f"\n--- Page {i} ---\n{txt}")
            return "\n".join(pages)
        except Exception as e:
            logger.exception("❌ PyPDF2 extraction failed")
            return None
