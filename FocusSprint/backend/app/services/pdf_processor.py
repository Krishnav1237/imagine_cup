"""
PDF processing service.
Extracts text content from PDF documents.
"""
import io
import logging
from typing import Optional
import PyPDF2
import pdfplumber

logger = logging.getLogger("PDFProcessor")

class PDFProcessor:
    """PDF document processor"""
    
    def extract_text(self, file_data: bytes) -> Optional[str]:
        """
        Extract text from PDF file.
        """
        logger.info("📄 Starting PDF text extraction...")
        # Try pdfplumber first (better formatting)
        text = self._extract_with_pdfplumber(file_data)
        
        if not text or len(text.strip()) < 100:
            logger.info("⚠️ pdfplumber yielded low text count. Falling back to PyPDF2.")
            # Fallback to PyPDF2
            text = self._extract_with_pypdf2(file_data)
        
        logger.info(f"✅ Extracted {len(text) if text else 0} characters from PDF.")
        return text
    
    def _extract_with_pdfplumber(self, file_data: bytes) -> Optional[str]:
        """Extract text using pdfplumber (preserves layout better)"""
        try:
            all_text = []
            
            with pdfplumber.open(io.BytesIO(file_data)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    
                    if text:
                        # Add page separator
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