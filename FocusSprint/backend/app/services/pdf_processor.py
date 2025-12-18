"""
PDF processing service.
Extracts text content from PDF documents.
"""
import io
import logging
import re
from typing import Optional, List, Dict
import PyPDF2
import pdfplumber

from app.services.filters.academic_noise import (
    remove_academic_noise,
    filter_bullets,
    is_academic_metadata_line
)

logger = logging.getLogger("PDFProcessor")


class PDFProcessor:
    """PDF document processor"""
    
    def extract_text(self, file_data: bytes) -> Optional[str]:
        """
        Extract text from PDF file and remove academic noise.
        """
        logger.info("📄 Starting PDF text extraction...")
        # Try pdfplumber first (better formatting)
        text = self._extract_with_pdfplumber(file_data)
        
        if not text or len(text.strip()) < 100:
            logger.info("⚠️ pdfplumber yielded low text count. Falling back to PyPDF2.")
            # Fallback to PyPDF2
            text = self._extract_with_pypdf2(file_data)
        
        # Remove academic noise immediately
        if text:
            text = remove_academic_noise(text)
        
        logger.info(f"✅ Extracted {len(text) if text else 0} characters from PDF (noise removed).")
        return text
    
    def _extract_with_pdfplumber(self, file_data: bytes) -> Optional[str]:
        """Extract text using pdfplumber (preserves layout better)"""
        try:
            all_text = []
            
            with pdfplumber.open(io.BytesIO(file_data)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    
                    if text:
                        all_text.append(f"\n--- Page {page_num} ---\n")
                        all_text.append(text)
            
            return '\n'.join(all_text)
        
        except Exception as e:
            logger.error(f"❌ Error extracting with pdfplumber: {e}")
            return None
    
    def _extract_with_pypdf2(self, file_data: bytes) -> Optional[str]:
        """Extract text using PyPDF2 (fallback)"""
        try:
            all_text = []
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                
                if text:
                    all_text.append(f"\n--- Page {page_num} ---\n")
                    all_text.append(text)
            
            return '\n'.join(all_text)
        
        except Exception as e:
            logger.error(f"❌ Error extracting with PyPDF2: {e}")
            return None
    
    def get_metadata(self, file_data: bytes) -> dict:
        """
        Extract PDF metadata.
        """
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
            metadata = pdf_reader.metadata
            
            return {
                'title': metadata.get('/Title', ''),
                'author': metadata.get('/Author', ''),
                'subject': metadata.get('/Subject', ''),
                'pages': len(pdf_reader.pages),
                'creator': metadata.get('/Creator', ''),
                'producer': metadata.get('/Producer', ''),
            }
        
        except Exception as e:
            logger.error(f"❌ Error extracting metadata: {e}")
            return {}

    def get_structured_content(self, file_data: bytes, file_name: str) -> List[Dict]:
        """
        Return structured units: each unit is a slide with title + bullets.
        Removes all academic noise before returning.
        
        Returns:
            List[Dict] with keys: title, bullets, page, file
        """
        logger.info("📄 Extracting structured PDF content (page-by-page, noise-filtered)...")
        units: List[Dict] = []
        try:
            with pdfplumber.open(io.BytesIO(file_data)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # Normalize whitespace
                    text = re.sub(r'\r\n|\r', '\n', text).strip()
                    
                    # Strip academic noise FIRST
                    text = remove_academic_noise(text)
                    if not text:
                        continue
                    
                    # Extract title and bullets
                    title, bullets = self._parse_slide_structure(text)
                    
                    # Filter bullets to remove any remaining metadata
                    bullets = filter_bullets(bullets)
                    
                    # Skip empty slides
                    if title or bullets:
                        units.append({
                            "title": title or f"Slide {page_num}",
                            "bullets": bullets,
                            "page": page_num,
                            "file": file_name
                        })
            
            logger.info(f"✅ Extracted {len(units)} knowledge-focused units from PDF.")
            return units
        except Exception as e:
            logger.error(f"❌ Error extracting structured content: {e}")
            return []

    def _parse_slide_structure(self, text: str) -> tuple:
        """
        Parse slide into title and bullets.
        
        Returns:
            (title: str, bullets: List[str])
        """
        lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        
        if not lines:
            return "", []
        
        # First line is usually the title, unless it's metadata
        title = ""
        start_idx = 0
        
        if lines and not is_academic_metadata_line(lines[0]) and len(lines[0]) < 100:
            title = lines[0]
            start_idx = 1
        
        # Extract bullets (lines starting with -, •, *, or numbers)
        bullets = []
        bullet_pattern = re.compile(r'^[-•*]\s+|^\d+\.\s+')
        
        for line in lines[start_idx:]:
            # Skip metadata lines
            if is_academic_metadata_line(line):
                continue
            
            # Clean bullet formatting
            line = re.sub(bullet_pattern, '', line).strip()
            if line and len(line) > 5:  # Filter out noise
                bullets.append(line)
        
        # If no bullets found, treat remaining lines as bullets
        if not bullets and start_idx < len(lines):
            bullets = [ln for ln in lines[start_idx:] 
                      if not is_academic_metadata_line(ln) and len(ln) > 5]
        
        return title, bullets[:10]  # Limit to 10 bullets per slide