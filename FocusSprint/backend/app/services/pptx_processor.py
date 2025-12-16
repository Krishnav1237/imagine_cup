"""
PowerPoint processing service
Extracts text content from PPTX presentations
"""
import io
from typing import Optional, List, Dict
from pptx import Presentation


class PPTXProcessor:
    """PowerPoint presentation processor"""
    
    def extract_text(self, file_data: bytes) -> Optional[str]:
        """
        Extract text from PowerPoint file
        
        Args:
            file_data: PPTX file binary data
        
        Returns:
            Extracted text or None on error
        """
        try:
            prs = Presentation(io.BytesIO(file_data))
            all_text = []
            
            for slide_num, slide in enumerate(prs.slides, 1):
                all_text.append(f"\n{'='*50}")
                all_text.append(f"SLIDE {slide_num}")
                all_text.append('='*50 + '\n')
                
                # Extract text from shapes
                slide_text = self._extract_slide_text(slide)
                if slide_text:
                    all_text.append(slide_text)
                
                # Add notes if present
                if slide.has_notes_slide:
                    notes = slide.notes_slide.notes_text_frame.text
                    if notes.strip():
                        all_text.append(f"\n[Speaker Notes: {notes}]\n")
            
            return '\n'.join(all_text)
        
        except Exception as e:
            print(f"Error extracting from PowerPoint: {e}")
            return None
    
    def _extract_slide_text(self, slide) -> str:
        """Extract text from all shapes in a slide"""
        text_parts = []
        
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                text = shape.text.strip()
                if text:
                    # Check if it's a title or body
                    if hasattr(shape, "shape_type"):
                        if shape.shape_type == 1:  # Title placeholder
                            text_parts.append(f"# {text}")
                        else:
                            text_parts.append(text)
                    else:
                        text_parts.append(text)
            
            # Handle tables
            if shape.has_table:
                table_text = self._extract_table_text(shape.table)
                if table_text:
                    text_parts.append(table_text)
        
        return '\n'.join(text_parts)
    
    def _extract_table_text(self, table) -> str:
        """Extract text from a table"""
        rows = []
        
        for row in table.rows:
            cells = []
            for cell in row.cells:
                cells.append(cell.text.strip())
            rows.append(' | '.join(cells))
        
        return '\n'.join(rows)
    
    def get_slide_count(self, file_data: bytes) -> int:
        """
        Get number of slides in presentation
        
        Args:
            file_data: PPTX file binary data
        
        Returns:
            Number of slides
        """
        try:
            prs = Presentation(io.BytesIO(file_data))
            return len(prs.slides)
        except Exception as e:
            print(f"Error counting slides: {e}")
            return 0
    
    def get_structured_content(self, file_data: bytes) -> List[Dict[str, str]]:
        """
        Extract content in structured format
        
        Args:
            file_data: PPTX file binary data
        
        Returns:
            List of dictionaries with slide content
        """
        try:
            prs = Presentation(io.BytesIO(file_data))
            slides = []
            
            for slide_num, slide in enumerate(prs.slides, 1):
                slide_data = {
                    'slide_number': slide_num,
                    'title': '',
                    'content': '',
                    'notes': ''
                }
                
                # Try to get title
                if slide.shapes.title:
                    slide_data['title'] = slide.shapes.title.text
                
                # Get body content
                content_parts = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text:
                        if shape != slide.shapes.title:
                            content_parts.append(shape.text.strip())
                
                slide_data['content'] = '\n'.join(content_parts)
                
                # Get notes
                if slide.has_notes_slide:
                    slide_data['notes'] = slide.notes_slide.notes_text_frame.text
                
                slides.append(slide_data)
            
            return slides
        
        except Exception as e:
            print(f"Error extracting structured content: {e}")
            return []