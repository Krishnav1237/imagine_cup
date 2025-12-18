import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from sqlalchemy.orm import Session
import requests

from app.core.database import SessionLocal
from app.models.models import ContentItem, ContentChunk
from app.schemas.schemas import ContentSourceType, ContentStatus
from app.services.youtube_downloader import YouTubeDownloader
from app.services.transcription.transcriber import get_transcriber
from app.services.chunking.ai_chunker import AIChunker
from app.services.chunking.utils import extract_key_concepts, generate_one_liner
from app.services.storage.adapter import get_storage_adapter
from app.services.pdf_processor import PDFProcessor
from app.services.pptx_processor import PPTXProcessor
from app.services.filters.academic_noise import contains_forbidden_terms
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
        db: Session = SessionLocal()
        try:
            content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
            if not content:
                logger.error("Content not found.")
                return

            # mark processing
            content.status = ContentStatus.PROCESSING
            content.processed_at = datetime.utcnow()
            db.add(content)
            db.commit()

            # 1) Get source bytes
            try:
                file_bytes, used_field = self._resolve_file_bytes(content)
                logger.info(f"🔎 Resolved content bytes using field: {used_field}")
            except Exception as e:
                raise RuntimeError("No valid storage path found on ContentItem or file not accessible.") from e

            units = None
            transcript = None
            duration = None

            # 2) Determine type and produce structured units
            filename = self._safe_filename(content)
            if content.source_type == ContentSourceType.PDF:
                units = self.pdf_processor.get_structured_content(file_bytes, filename)
            elif content.source_type == ContentSourceType.PPTX:
                units = self.pptx_processor.get_structured_content(file_bytes, filename)
            elif content.source_type == ContentSourceType.YOUTUBE:
                # download & transcribe
                transcript, duration = await self._process_youtube(content, db)
            else:
                # generic fallback to full text extraction
                if content.file_name and content.file_name.lower().endswith('.pdf'):
                    units = self.pdf_processor.get_structured_content(file_bytes, filename)
                elif content.file_name and content.file_name.lower().endswith('.pptx'):
                    units = self.pptx_processor.get_structured_content(file_bytes, filename)
                else:
                    # fallback: run generic text extraction then treat as single transcript
                    transcript = (self.pdf_processor.extract_text(file_bytes) or self.pptx_processor.extract_text(file_bytes) or "")

            # 3) Convert units to chunks directly (no AI chunker for structured units)
            chunks_data = []
            if units:
                chunks_data = await self._units_to_chunks(units, content.title or filename or "Untitled")
            elif transcript:
                chunks_data = await self.chunker.generate_chunks(transcript=transcript, title=content.title or filename or "Untitled", duration=duration)
            else:
                raise RuntimeError("No extractable content available to chunk.")

            if not chunks_data:
                raise RuntimeError("No chunks generated.")

            # 4) Save Chunks
            for idx, chunk_data in enumerate(chunks_data):
                chunk = ContentChunk(
                    content_item_id=content.id,
                    sequence_number=idx + 1,
                    title=chunk_data.get('title', f"Part {idx + 1}"),
                    summary=chunk_data.get('summary', ''),
                    text_content='\n'.join(chunk_data.get('bullets', [])),
                    duration_seconds=int(chunk_data.get('duration_seconds', 0)),
                    key_concepts=chunk_data.get('key_concepts', []),
                    quiz_questions=[],
                    difficulty_level='medium',
                    source_file=chunk_data.get('source', {}).get('file'),
                    source_page=chunk_data.get('source', {}).get('page'),
                    source_slide=chunk_data.get('source', {}).get('slide'),
                    card_json=json.dumps(chunk_data, ensure_ascii=False)
                )
                db.add(chunk)

            # finalize
            content.status = ContentStatus.COMPLETED
            content.processed_at = datetime.utcnow()
            db.add(content)
            db.commit()
            logger.info(
                f"✅ Content {content.id} processed into {len(chunks_data)} chunks."
            )
        except Exception as e:
            logger.exception(f"❌ Processing failed for content_id={content_id}: {e}")
            try:
                content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
                if content:
                    content.status = ContentStatus.FAILED
                    db.add(content)
                    db.commit()
            except Exception:
                logger.exception("Failed to mark content as failed.")
        finally:
            db.close()

    async def _units_to_chunks(self, units: List[dict], doc_title: str) -> List[dict]:
        """
        Convert structured units (with title + bullets) directly to chunk-cards.
        Enforces knowledge-only content, no academic noise.
        """
        chunks = []
        for unit in units:
            title = unit.get('title', 'Untitled')
            bullets = unit.get('bullets', [])
            
            # Skip if all bullets are metadata
            if not bullets or len(bullets) == 0:
                continue
            
            # Extract real key concepts (deterministic)
            key_concepts = extract_key_concepts(bullets, max_concepts=5)
            
            # Generate strict one-liner
            summary = generate_one_liner(title, bullets)
            
            # VALIDATION: Check for forbidden terms in output
            has_noise, found_terms = contains_forbidden_terms(summary)
            if has_noise:
                logger.warning(
                    f"⚠️ Summary contains noise terms {found_terms}: '{summary}'. "
                    f"Regenerating..."
                )
                # Regenerate without metadata
                summary = generate_one_liner(title, bullets[:3])
            
            # Also validate title
            has_noise_title, _ = contains_forbidden_terms(title)
            if has_noise_title:
                logger.warning(f"⚠️ Title contains noise: '{title}'. Skipping unit.")
                continue
            
            chunk = {
                'title': title,
                'bullets': bullets,
                'summary': summary,
                'key_concepts': key_concepts,
                'duration_seconds': 0,
                'source': {
                    'file': unit.get('file'),
                    'page': unit.get('page'),
                }
            }
            chunks.append(chunk)
        
        return chunks

    async def _get_transcript(self, content: ContentItem, db: Session) -> Optional[str]:
        # If pre-existing transcript stored in DB or storage, return it
        return None

    async def _process_youtube(self, content: ContentItem, db: Session) -> Optional[str]:
        # download video and transcribe using configured transcriber
        # returns (transcript, duration_seconds)
        yt_bytes = self.youtube_downloader.download(content.origin_url)
        # transcriber returns (text, duration_seconds)
        transcript, duration = await self.transcriber.transcribe_bytes(yt_bytes)
        return transcript, duration

    def _safe_filename(self, content: ContentItem) -> str:
        """
        Return a usable filename for processors.
        Falls back gracefully when original filename is unavailable.
        """
        if getattr(content, "file_name", None):
            return content.file_name

        if getattr(content, "file_path", None):
            return Path(content.file_path).name

        if getattr(content, "storage_path", None):
            return Path(content.storage_path).name

        return content.title or "untitled"

    def _resolve_file_bytes(self, content):
        """
        Try a list of likely ContentItem attributes and return (bytes, attribute_name).
        If the attribute is a URL it will try to download it.
        """
        candidates = (
            "storage_path",
            "storage_key",
            "file_path",
            "upload_path",
            "path",
            "local_path",
            "storage_url",
            "origin_url",
            "download_url",
            "s3_key"
        )
        for attr in candidates:
            val = getattr(content, attr, None)
            if not val:
                continue
            # URL candidate -> try download
            if isinstance(val, str) and (val.startswith("http://") or val.startswith("https://")):
                try:
                    r = requests.get(val, timeout=15)
                    r.raise_for_status()
                    return r.content, attr
                except Exception as e:
                    logger.debug(f"Failed to fetch URL from {attr}={val}: {e}")
                    continue
            # Local/key candidate -> use storage adapter
            try:
                b = self.storage.get_bytes(val)
                return b, attr
            except FileNotFoundError:
                logger.debug(f"Storage file not found for {attr}={val}; trying next option.")
            except Exception as e:
                logger.error(f"Error reading storage for {attr}={val}: {e}")
                raise
        # helpful debug dump before raising
        debug_map = {a: getattr(content, a, None) for a in candidates}
        logger.error(f"No storage attribute matched for content id={content.id}. Candidates: {debug_map}")
        raise RuntimeError("No storage attribute matched or file inaccessible.")


# Export a shared processor instance for imports that expect `processor`
processor = ContentProcessor()