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
                # download & transcribe with optional VLM analysis
                transcript, duration = await self._process_youtube(content, db)
                
                # Try VLM-enhanced chunking if video file available
                try:
                    from app.services.video_vision_processor import video_vision_processor
                    
                    # Check if we have the video file for frame extraction
                    video_path = await self._get_video_path(content)
                    if video_path and video_vision_processor.openai_client:
                        logger.info("🎬 Using VLM for visual context analysis")
                        
                        # Extract keyframes
                        frames = await video_vision_processor.extract_keyframes(
                            video_path, 
                            interval_seconds=30,
                            max_frames=15
                        )
                        
                        if frames:
                            # Generate VLM-enhanced chunks
                            vlm_chunks = await video_vision_processor.analyze_with_vlm(
                                frames=frames,
                                transcript=transcript,
                                title=content.title or "Untitled"
                            )
                            
                            if vlm_chunks:
                                # Convert VLM chunks to standard format with visual context
                                for vc in vlm_chunks:
                                    vc['visual_context'] = vc.get('visual_context')
                                    vc['key_visual_elements'] = vc.get('key_visual_elements', [])
                                    vc['key_frame_timestamp'] = vc.get('key_frame_timestamp')
                                    vc['bullets'] = vc.get('content', [])
                                chunks_data = vlm_chunks
                                logger.info(f"✅ VLM generated {len(chunks_data)} visual-context chunks")
                            
                            # Cleanup temp frames
                            video_vision_processor.cleanup_frames(frames)
                except Exception as vlm_error:
                    logger.warning(f"⚠️ VLM processing failed, using text-only: {vlm_error}")
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
                    text_content='\n'.join(chunk_data.get('bullets', chunk_data.get('content', []))),
                    duration_seconds=int(chunk_data.get('duration_seconds', 0)),
                    key_concepts=chunk_data.get('key_concepts', []),
                    quiz_questions=[],
                    difficulty_level=chunk_data.get('complexity', 'medium'),
                    source_file=chunk_data.get('source', {}).get('file'),
                    source_page=chunk_data.get('source', {}).get('page'),
                    source_slide=chunk_data.get('source', {}).get('slide'),
                    # VLM visual context fields
                    visual_context=chunk_data.get('visual_context'),
                    key_visual_elements=chunk_data.get('key_visual_elements'),
                    key_frame_timestamp=chunk_data.get('key_frame_timestamp'),
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

    async def _process_youtube(self, content: ContentItem, db: Session) -> tuple:
        """
        Download YouTube video, transcribe audio, and return (transcript, duration_seconds).
        Also updates content with video metadata (thumbnail, duration).
        """
        logger.info(f"🎬 Processing YouTube content: {content.source_url}")
        
        try:
            # 1. Get video info first (for metadata)
            video_info = await self.youtube_downloader.get_video_info(content.source_url)
            if video_info:
                content.duration_seconds = video_info.get('duration')
                # Store thumbnail URL if available
                if not content.thumbnail_url:
                    # YouTube thumbnail pattern
                    import re
                    video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', content.source_url)
                    if video_id_match:
                        video_id = video_id_match.group(1)
                        content.thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                db.add(content)
                db.commit()
                logger.info(f"📺 Video info: duration={video_info.get('duration')}s, title={video_info.get('title')}")
            
            # 2. Download audio
            destination_folder = f"{content.user_id}/{content.id}"
            audio_path = await self.youtube_downloader.download_audio(
                content.source_url,
                destination_folder
            )
            
            if not audio_path:
                raise RuntimeError("Failed to download audio from YouTube")
            
            logger.info(f"🎵 Audio downloaded to: {audio_path}")
            
            # 3. Transcribe audio
            transcript = await self.transcriber.transcribe_audio(audio_path)
            
            if not transcript:
                raise RuntimeError("Transcription failed or returned empty")
            
            logger.info(f"📝 Transcription complete: {len(transcript)} characters")
            
            # Store transcript in content item
            content.transcript_text = transcript
            db.add(content)
            db.commit()
            
            duration = content.duration_seconds or (video_info.get('duration') if video_info else None)
            return transcript, duration
            
        except Exception as e:
            logger.error(f"❌ YouTube processing failed: {e}")
            raise RuntimeError(f"YouTube processing failed: {str(e)}") from e

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

    async def _get_video_path(self, content: ContentItem) -> Optional[str]:
        """
        Get the local video file path for VLM frame extraction.
        Returns full path if video exists locally, None otherwise.
        """
        # For YouTube, we store audio only by default
        # But if video was downloaded, it would be here
        destination_folder = f"{content.user_id}/{content.id}"
        possible_paths = [
            Path(settings.UPLOAD_DIR) / destination_folder / "video.mp4",
            Path(settings.UPLOAD_DIR) / destination_folder / "audio.mp3",  # Can extract frames from mp3's source
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        # Check if source_url is a local file
        if content.source_url and Path(content.source_url).exists():
            return content.source_url
        
        return None

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