"""
PowerPoint processing service.
Extracts text content from PPTX presentations.
"""
import io
import logging
from typing import Optional, List, Dict
from pptx import Presentation

logger = logging.getLogger("PPTXProcessor")

class PPTXProcessor:
    """PowerPoint presentation processor"""
    
    def extract_text(self, file_data: bytes) -> Optional[str]:
        logger.info("📊 Starting PPTX text extraction...")
        try:
            prs = Presentation(io.BytesIO(file_data))
            all_text = []
            for slide_num, slide in enumerate(prs.slides, 1):
                slide_text = self._extract_slide_text(slide)
                if slide_text:
                    all_text.append(f"\n--- Slide {slide_num} ---\n")
                    all_text.append(slide_text)
            result = '\n'.join(all_text)
            logger.info(f"✅ Extracted {len(result)} characters from PPTX.")
            return result
        except Exception as e:
            logger.error(f"❌ Error extracting PPTX: {e}")
            return None
    
    def _extract_slide_text(self, slide) -> str:
        """Extract text from all shapes in a slide"""
        text_parts = []
        for shape in slide.shapes:
            # text frames (paragraphs/bullets)
            try:
                if hasattr(shape, "text") and shape.text:
                    text_parts.append(shape.text)
            except Exception:
                continue
            # tables
            if shape.shape_type == 19:  # TABLE
                try:
                    text_parts.append(self._extract_table_text(shape.table))
                except Exception:
                    continue
        return '\n'.join([p.strip() for p in text_parts if p and p.strip()])
    
    def _extract_table_text(self, table) -> str:
        """Extract text from a table"""
        rows = []
        for r in table.rows:
            cells = [c.text.strip() for c in r.cells if c.text and c.text.strip()]
            if cells:
                rows.append(' | '.join(cells))
        return '\n'.join(rows)
    
    def get_slide_count(self, file_data: bytes) -> int:
        """
        Get number of slides in presentation.
        """
        try:
            prs = Presentation(io.BytesIO(file_data))
            return len(prs.slides)
        except Exception as e:
            logger.error(f"❌ Error counting slides: {e}")
            return 0
    
    def get_structured_content(self, file_data: bytes, file_name: str) -> List[Dict[str, object]]:
        """
        Return a list of structured units extracted from the PPTX.
        Each unit: { "text": str, "file": file_name, "slide": int }
        Slides longer than ~250 words are split by paragraph/sentence preserving bullets.
        """
        logger.info("📊 Extracting structured PPTX content (slide-by-slide)...")
        units: List[Dict[str, object]] = []
        try:
            prs = Presentation(io.BytesIO(file_data))
            for slide_num, slide in enumerate(prs.slides, 1):
                text = self._extract_slide_text(slide)
                if not text:
                    continue
                # Normalize whitespace
                text = text.replace('\r\n', '\n').strip()
                # If slide is large split it into sub-units preserving bullet/paragraph boundaries
                units_from_slide = self._split_slide_to_units(text, max_words=250)
                for u in units_from_slide:
                    units.append({"text": u.strip(), "file": file_name, "slide": slide_num})
            logger.info(f"✅ Structured slide content returned with {len(units)} units.")
            return units
        except Exception as e:
            logger.error(f"❌ Error extracting structured PPTX content: {e}")
            # Fallback: return whole text per slide
            raw = self.extract_text(file_data) or ""
            if raw:
                # split on slide markers
                parts = []
                cur = []
                current_slide = None
                for line in raw.splitlines():
                    m = None
                    if line.startswith("--- Slide "):
                        if cur and current_slide is not None:
                            parts.append({"text":"\n".join(cur),"slide":current_slide})
                        cur = []
                        try:
                            current_slide = int(line.split()[-1].strip().strip('-'))
                        except Exception:
                            current_slide = None
                    else:
                        cur.append(line)
                if cur and current_slide is not None:
                    parts.append({"text":"\n".join(cur),"slide":current_slide})
                return [{"text":p["text"], "file":file_name, "slide":p["slide"]} for p in parts] if parts else []
            return []
    
    def _split_slide_to_units(self, slide_text: str, max_words: int = 250) -> List[str]:
        """
        Split slide text into smaller units when necessary. Preserve bullet groups and short headings.
        """
        import re
        lines = [ln.strip() for ln in slide_text.split('\n') if ln.strip()]
        # group bullets (lines that start with '-', '•', or are short)
        paragraphs = []
        cur = []
        for ln in lines:
            if re.match(r'^[-•\u2022\d\.\)]\s*', ln):
                if cur:
                    paragraphs.append(" ".join(cur))
                    cur = []
                paragraphs.append(ln)
            else:
                cur.append(ln)
        if cur:
            paragraphs.append(" ".join(cur))
        # Now ensure units are under max_words by grouping adjacent paragraphs
        units = []
        cur = ""
        cur_w = 0
        for p in paragraphs:
            w = len(re.findall(r'\w+', p))
            if cur_w + w > max_words and cur:
                units.append(cur.strip())
                cur = p
                cur_w = w
            else:
                cur = f"{cur} {p}".strip()
                cur_w += w
        if cur:
            units.append(cur.strip())
        # Filter out tiny items
        return [u for u in units if len(u.split()) > 6]