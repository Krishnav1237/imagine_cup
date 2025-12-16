"""
Content processing service
Handles YouTube download, transcription, and AI chunking
"""
import os
import asyncio
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import ContentItem, ContentChunk
from app.schemas.schemas import ContentSourceType, ContentStatus
from app.services.youtube_downloader import YouTubeDownloader
from app.services.transcription.transcriber import get_transcriber
from app.services.chunking.ai_chunker import AIChunker
from app.services.storage.adapter import get_storage_adapter
from app.config import settings


class ContentProcessor:
    """Main content processing orchestrator"""
    
    def __init__(self, db: Session):
        self.db = db
        self.storage = get_storage_adapter()
        self.transcriber = get_transcriber()
        self.chunker = AIChunker()
        self.youtube_downloader = YouTubeDownloader()
    
    async def process_content(self, content_id: int):
        """
        Main processing pipeline for content
        1. Download/Extract content
        2. Transcribe audio
        3. Generate AI chunks
        4. Save to database
        """
        content = self.db.query(ContentItem).filter(
            ContentItem.id == content_id
        ).first()
        
        if not content:
            print(f"Content {content_id} not found")
            return
        
        try:
            content.status = ContentStatus.PROCESSING.value
            self.db.commit()
            
            # Step 1: Get transcript
            print(f"📝 Processing content {content_id}: {content.title}")
            transcript = await self._get_transcript(content)
            
            if not transcript:
                raise Exception("Failed to generate transcript")
            
            # Save transcript
            content.transcript_text = transcript
            self.db.commit()
            
            # Step 2: Generate chunks with AI
            print(f"🤖 Generating AI chunks for content {content_id}")
            chunks = await self.chunker.generate_chunks(
                transcript,
                content.title,
                content.duration_seconds
            )
            
            if not chunks:
                raise Exception("Failed to generate chunks")
            
            # Step 3: Save chunks to database
            print(f"💾 Saving {len(chunks)} chunks to database")
            for idx, chunk_data in enumerate(chunks):
                chunk = ContentChunk(
                    content_item_id=content.id,
                    sequence_number=idx + 1,
                    title=chunk_data.get('title', f"Chunk {idx + 1}"),
                    summary=chunk_data.get('summary'),
                    text_content=chunk_data.get('content', ''),
                    duration_seconds=chunk_data.get('duration', 180),
                    key_concepts=chunk_data.get('key_concepts', []),
                    quiz_questions=chunk_data.get('quiz_questions', []),
                    difficulty_level=chunk_data.get('difficulty', 'medium')
                )
                self.db.add(chunk)
            
            # Mark as completed
            content.status = ContentStatus.COMPLETED.value
            content.processed_at = datetime.utcnow()
            self.db.commit()
            
            print(f"✅ Successfully processed content {content_id}")
        
        except Exception as e:
            print(f"❌ Error processing content {content_id}: {e}")
            content.status = ContentStatus.FAILED.value
            content.error_message = str(e)
            self.db.commit()
    
    async def _get_transcript(self, content: ContentItem) -> Optional[str]:
        """Get transcript based on content type"""
        
        if content.source_type == ContentSourceType.YOUTUBE.value:
            return await self._process_youtube(content)
        
        elif content.source_type == ContentSourceType.PDF.value:
            return await self._process_pdf(content)
        
        elif content.source_type == ContentSourceType.PPTX.value:
            return await self._process_pptx(content)
        
        return None
    
    async def _process_youtube(self, content: ContentItem) -> Optional[str]:
        """Process YouTube video"""
        try:
            # Download audio
            print(f"📥 Downloading YouTube video: {content.source_url}")
            audio_path = await self.youtube_downloader.download_audio(
                content.source_url,
                f"content/{content.user_id}/{content.id}"
            )
            
            if not audio_path:
                raise Exception("Failed to download YouTube audio")
            
            # Get video info
            info = await self.youtube_downloader.get_video_info(content.source_url)
            if info:
                content.duration_seconds = info.get('duration')
                if not content.title or content.title.startswith('Untitled'):
                    content.title = info.get('title', content.title)
                self.db.commit()
            
            # Transcribe audio
            print(f"🎤 Transcribing audio from YouTube video")
            transcript = await self.transcriber.transcribe_audio(audio_path)
            
            return transcript
        
        except Exception as e:
            print(f"Error processing YouTube video: {e}")
            raise
    
    async def _process_pdf(self, content: ContentItem) -> Optional[str]:
        """Process PDF document"""
        try:
            from app.services.pdf_processor import PDFProcessor
            
            print(f"📄 Processing PDF: {content.file_path}")
            processor = PDFProcessor()
            
            # Get file from storage
            file_data = await self.storage.get_file(content.file_path)
            
            # Extract text
            text = processor.extract_text(file_data)
            
            return text
        
        except Exception as e:
            print(f"Error processing PDF: {e}")
            raise
    
    async def _process_pptx(self, content: ContentItem) -> Optional[str]:
        """Process PowerPoint presentation"""
        try:
            from app.services.pptx_processor import PPTXProcessor
            
            print(f"📊 Processing PowerPoint: {content.file_path}")
            processor = PPTXProcessor()
            
            # Get file from storage
            file_data = await self.storage.get_file(content.file_path)
            
            # Extract text
            text = processor.extract_text(file_data)
            
            return text
        
        except Exception as e:
            print(f"Error processing PowerPoint: {e}")
            raise