import os
import asyncio
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import ContentItem, ContentChunk
from app.schemas.schemas import ContentSourceType, ContentStatus
from app.services.youtube_downloader import YouTubeDownloader
from app.services.transcription.transcriber import get_transcriber
from app.services.chunking.ai_chunker import AIChunker
from app.services.storage.adapter import get_storage_adapter
from app.services.pdf_processor import PDFProcessor
from app.services.pptx_processor import PPTXProcessor
from app.config import settings

# Use the centralized logger configuration
logger = logging.getLogger("ContentProcessor")

class ContentProcessor:
    def __init__(self):
        logger.info("🔧 Initializing ContentProcessor services...")
        self.storage = get_storage_adapter()
        self.transcriber = get_transcriber()
        self.chunker = AIChunker()
        self.youtube_downloader = YouTubeDownloader()
        self.pdf_processor = PDFProcessor()
        self.pptx_processor = PPTXProcessor()
        logger.info("✅ Services initialized.")

    async def process_content_task(self, content_id: int):
        logger.info(f"🔄 [Task Start] Processing content_id={content_id}")
        db = SessionLocal()
        try:
            content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
            if not content:
                logger.error(f"❌ Content {content_id} not found in DB.")
                return
            
            # 1. Update Status
            content.status = ContentStatus.PROCESSING.value
            db.commit()
            logger.info(f"📝 Status updated to PROCESSING for '{content.title}'")

            # 2. Get Transcript
            logger.info(f"audio_process: Starting transcript generation for type={content.source_type}")
            transcript = await self._get_transcript(content, db)
            
            if not transcript:
                raise Exception("Transcript generation returned empty result.")
            
            content.transcript_text = transcript
            db.commit()
            logger.info(f"✅ Transcript saved. Length: {len(transcript)} chars.")

            # 3. Generate AI Chunks
            duration = content.duration_seconds if content.duration_seconds else 600
            logger.info(f"🧠 Invoking AI Chunker for '{content.title}' (Duration: {duration}s)")
            
            # Match AIChunker.generate_chunks signature (transcript, title, duration)
            chunks_data = await self.chunker.generate_chunks(
                transcript=transcript,
                title=content.title or "Untitled",
                duration=duration
            )

            if not chunks_data:
                raise Exception("AI Chunker returned no chunks.")
            
            logger.info(f"📦 Received {len(chunks_data)} chunks from AI. Saving to DB...")

            # 4. Save Chunks
            for idx, data in enumerate(chunks_data):
                chunk = ContentChunk(
                    content_item_id=content.id,
                    sequence_number=idx + 1,
                    title=data.get('title', f"Part {idx + 1}"),
                    summary=data.get('summary', ''),
                    text_content=data.get('content', ''),
                    duration_seconds=data.get('duration', 180),
                    key_concepts=data.get('key_concepts', []),
                    quiz_questions=data.get('quiz_questions', []),
                    difficulty_level=data.get('difficulty', 'medium')
                )
                db.add(chunk)
            
            # 5. Complete
            content.status = ContentStatus.COMPLETED.value
            content.processed_at = datetime.utcnow()
            db.commit()
            logger.info(f"🎉 [Task Complete] Content {content_id} processed successfully.")

        except Exception as e:
            logger.error(f"❌ [Task Failed] Error processing {content_id}: {e}", exc_info=True)
            content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
            if content:
                content.status = ContentStatus.FAILED.value
                content.error_message = str(e)
                db.commit()
        finally:
            db.close()
            logger.info(f"🔒 DB Session closed for task {content_id}")

    async def _get_transcript(self, content: ContentItem, db: Session) -> Optional[str]:
        if content.source_type == ContentSourceType.YOUTUBE.value:
            return await self._process_youtube(content, db)
        elif content.source_type == ContentSourceType.PDF.value:
            return await self._process_pdf(content)
        elif content.source_type == ContentSourceType.PPTX.value:
            return await self._process_pptx(content)
        else:
            raise ValueError(f"Unknown source type: {content.source_type}")

    async def _process_youtube(self, content: ContentItem, db: Session) -> Optional[str]:
        download_dir = f"{settings.UPLOAD_DIR}/{content.user_id}/{content.id}"
        os.makedirs(download_dir, exist_ok=True)
        
        logger.info(f"📥 Downloading YouTube video: {content.source_url}")
        audio_path = await self.youtube_downloader.download_audio(content.source_url, download_dir)
        
        if not audio_path:
            raise Exception("YouTube download failed. This may be due to: 1) Outdated yt-dlp (run 'pip install --upgrade yt-dlp'), 2) YouTube blocking the request, or 3) Video restrictions. Try updating yt-dlp first.")
            
        # Get Info
        info = await self.youtube_downloader.get_video_info(content.source_url)
        if info:
            content.duration_seconds = info.get('duration', 0)
            if not content.title or "Untitled" in content.title:
                content.title = info.get('title', content.title)
            db.commit()
            logger.info(f"ℹ️ Video Info Updated: {content.title} ({content.duration_seconds}s)")

        logger.info("mic: Transcribing audio file...")
        return await self.transcriber.transcribe_audio(audio_path)

    async def _process_pdf(self, content: ContentItem) -> Optional[str]:
        logger.info(f"📄 Extracting text from PDF: {content.file_path}")
        with open(content.file_path, 'rb') as f:
            return self.pdf_processor.extract_text(f.read())

    async def _process_pptx(self, content: ContentItem) -> Optional[str]:
        logger.info(f"📊 Extracting text from PPTX: {content.file_path}")
        with open(content.file_path, 'rb') as f:
            return self.pptx_processor.extract_text(f.read())

processor = ContentProcessor()