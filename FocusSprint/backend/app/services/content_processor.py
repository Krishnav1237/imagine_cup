import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import ContentItem, ContentChunk, VideoChapter
from app.schemas.schemas import ContentSourceType, ContentStatus
from app.config import settings

# ─────────────────────────────────────────────
# Storage & media
# ─────────────────────────────────────────────
from app.services.storage.adapter import get_storage_adapter
from app.services.youtube_downloader import YouTubeDownloader

# ─────────────────────────────────────────────
# Transcription (timestamps guaranteed)
# ─────────────────────────────────────────────
from app.services.transcription.transcriber import (
    get_transcriber,
    get_youtube_transcript_with_timestamps,
)

# ─────────────────────────────────────────────
# LLM chapterization (NO VLM)
# ─────────────────────────────────────────────
from app.services.video_pipeline.chapter_generator import generate_video_chapters
from app.services.video_pipeline.video_rag_chunker import generate_video_chunks


# ─────────────────────────────────────────────
# Document pipeline
# ─────────────────────────────────────────────
from app.services.document_extraction.layout_extractor import extract_layout_units
from app.services.chunking.ollama_card_compiler import compile_cards


logger = logging.getLogger("ContentProcessor")

# WebSocket broadcast helper
async def broadcast_status(user_id: int, content_id: int, status: str, stage: str = None):
    """Broadcast content status update via WebSocket."""
    try:
        from app.api.v1.websocket import get_ws_manager
        manager = get_ws_manager()
        await manager.broadcast_content_update(user_id, content_id, status, stage)
    except Exception as e:
        logger.warning(f"WebSocket broadcast failed (non-fatal): {e}")


class ContentProcessor:
    """
    Central orchestration layer.

    Responsibilities:
    - Fetch raw content
    - Route to correct pipeline (document / video)
    - Persist normalized chunk cards
    """

    def __init__(self):
        logger.info("🔧 Initializing ContentProcessor")

        self.storage = get_storage_adapter()
        self.transcriber = get_transcriber()
        self.youtube_downloader = YouTubeDownloader()

        logger.info("✅ ContentProcessor initialized")

    # ─────────────────────────────────────────────
    # Public entrypoint
    # ─────────────────────────────────────────────

    async def process_content_task(self, content_id: int) -> None:
        logger.info(f"🔄 [START] Processing content_id={content_id}")
        start_ts = datetime.now(timezone.utc)
        db: Session = SessionLocal()

        try:
            content = (
                db.query(ContentItem)
                .filter(ContentItem.id == content_id)
                .first()
            )

            if not content:
                logger.error("❌ Content not found")
                return

            logger.info(
                "📄 Content loaded | id=%s | type=%s",
                content.id,
                content.source_type,
            )

            # ─────────────────────────────────────────────
            # Mark processing start
            # ─────────────────────────────────────────────
            content.status = ContentStatus.PROCESSING
            content.stage = "INITIALIZING"
            content.error_message = None
            content.processed_at = datetime.now(timezone.utc)
            db.commit()

            await broadcast_status(
                content.user_id,
                content.id,
                "processing",
                "INITIALIZING",
            )

            # ─────────────────────────────────────────────
            # DOCUMENT PIPELINE (UNCHANGED)
            # ─────────────────────────────────────────────
            if content.source_type in {
                ContentSourceType.PDF,
                ContentSourceType.PPTX,
            }:
                content.stage = "DOCUMENT_PIPELINE"
                db.commit()

                await broadcast_status(
                    content.user_id,
                    content.id,
                    "processing",
                    "DOCUMENT_PIPELINE",
                )

                chunks = await self._process_document(content)

                if not chunks:
                    raise RuntimeError("No document chunks generated")

                content.stage = "PERSISTING_CHUNKS"
                db.commit()
                self._persist_chunks(db, content, chunks)

            # ─────────────────────────────────────────────
            # VIDEO PIPELINE – YOUTUBE (authoritative path)
            # ─────────────────────────────────────────────
            elif content.source_type == ContentSourceType.YOUTUBE:
                content.stage = "VIDEO_PIPELINE"
                db.commit()

                await broadcast_status(
                    content.user_id,
                    content.id,
                    "processing",
                    "VIDEO_PIPELINE",
                )

                # ── Step 1: Transcript
                # If a file was uploaded, ignore the URL and transcribe the file.
                # Otherwise, use YouTube's native captions via the transcript API.
                transcript_segments = None

                # 1️⃣ Prefer uploaded file if present
                if content.file_path:
                    logger.info("🎧 Using uploaded video file for transcription")
                    transcript_segments = await self.transcriber.transcribe_audio_with_timestamps(
                        content.file_path
                    )

                # 2️⃣ Try YouTube captions
                if not transcript_segments:
                    try:
                        logger.info("📺 Attempting YouTube native transcript")
                        transcript_segments = get_youtube_transcript_with_timestamps(
                            content.source_url
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ YouTube transcript unavailable: {e}")

                # 3️⃣ FINAL fallback — download audio + Whisper
                if not transcript_segments:
                    logger.info("⬇️ Downloading audio for Whisper fallback")

                    audio_path = await self.youtube_downloader.download_audio(
                        content.source_url,
                        f"{content.user_id}/{content.id}",
                    )

                    if not audio_path:
                        logger.error(
                            "❌ YouTube audio download failed — cannot run Whisper fallback"
                        )
                    else:
                        transcript_segments = await self.transcriber.transcribe_audio_with_timestamps(
                            audio_path
                        )

                # 4️⃣ Hard fail only if Whisper also failed
                if not transcript_segments:
                    raise RuntimeError("Transcript generation failed (YouTube + Whisper)")
                
                # ── Step 2: Chapterization (deterministic from transcript indices)

                logger.info("🧠 Performing RAG-based video chunking")

                chapters = await generate_video_chunks(transcript_segments)

                if not chapters:
                    raise RuntimeError("No video chunks generated")

                # ── Step 3: Persist chapters with deterministic timestamps
                db.query(VideoChapter).filter(
                    VideoChapter.content_id == content.id
                ).delete()

                for ch in chapters:
                    db.add(
                        VideoChapter(
                            content_id=content.id,   # ✅ correct & authoritative
                            chapter_index=ch["index"],
                            title=ch["title"],
                            start_seconds=int(ch["start"]),
                            end_seconds=int(ch["end"]),
                            summary=ch["summary"],
                        )
                    )

                db.commit()

            # ─────────────────────────────────────────────
            # VIDEO PIPELINE – Generic video (non‑YouTube)
            # ─────────────────────────────────────────────
            elif content.source_type == ContentSourceType.VIDEO:
                content.stage = "VIDEO_PIPELINE"
                db.commit()

                await broadcast_status(
                    content.user_id,
                    content.id,
                    "processing",
                    "VIDEO_PIPELINE",
                )

                # ── Step 1: Transcript
                # - If we have a source_url, treat it as a remote video URL and
                #   use the downloader (e.g., Loom, Vimeo, direct MP4 links).
                # - If we only have an uploaded file, transcribe it directly
                #   via Whisper using the stored file path.
                if content.source_url:
                    audio_path = await self.youtube_downloader.download_audio(
                        content.source_url,
                        f"{content.user_id}/{content.id}",
                    )

                    if not audio_path:
                        raise RuntimeError(
                            "YouTube audio download failed — cannot transcribe video"
                        )

                    transcript_segments = await self.transcriber.transcribe_audio_with_timestamps(
                        audio_path
                    )

                else:
                    file_path = self._resolve_file_path(content)
                    transcript_segments = await self.transcriber.transcribe_audio_with_timestamps(
                        file_path
                    )

                if not transcript_segments:
                    raise RuntimeError("Transcript generation failed")

                # ── Step 2: Chapterization
                chapters_json = await generate_video_chapters(transcript_segments)

                chapters = chapters_json.get("chapters")
                if not chapters:
                    raise RuntimeError("LLM returned no chapters")

                # ── Step 3: Persist chapters
                db.query(VideoChapter).filter(
                    VideoChapter.content_id == content.id
                ).delete()

                for ch in chapters:
                    db.add(
                        VideoChapter(
                            content_id=content.id,   # ✅ correct & authoritative
                            chapter_index=ch["index"],
                            title=ch["title"],
                            start_seconds=int(ch["start"]),
                            end_seconds=int(ch["end"]),
                            summary=ch["summary"],
                        )
                    )

                db.commit()

            else:
                raise RuntimeError(f"Unsupported source type: {content.source_type}")

            # ─────────────────────────────────────────────
            # Mark completion
            # ─────────────────────────────────────────────
            content.status = ContentStatus.COMPLETED
            content.stage = None
            content.processed_at = datetime.now(timezone.utc)
            content.error_message = None
            db.commit()

            await broadcast_status(
                content.user_id,
                content.id,
                "completed",
                None,
            )

            elapsed = (datetime.now(timezone.utc) - start_ts).total_seconds()
            logger.info("⏱️ Total processing time: %.2fs", elapsed)
            logger.info("✅ [DONE] Content %s processed successfully", content.id)

        except Exception as e:
            logger.exception("❌ Processing failed")

            try:
                content.status = ContentStatus.FAILED
                content.stage = None
                content.error_message = str(e)
                content.processed_at = datetime.now(timezone.utc)
                db.commit()

                await broadcast_status(
                    content.user_id,
                    content.id,
                    "failed",
                    None,
                )
            except Exception:
                logger.exception("❌ Failed to mark content FAILED")

        finally:
            db.close()

    def new_method(self):
        return datetime.now(timezone.utc)

    # ─────────────────────────────────────────────
    # Document pipeline
    # ─────────────────────────────────────────────
    async def _process_document(self, content: ContentItem) -> List[dict]:
        logger.info("📄 Document pipeline started (RAG enabled)")

        # ─────────────────────────────────────────────
        # 1. Layout-aware extraction
        # ─────────────────────────────────────────────
        structured_units = self._load_or_extract_layout_units(content)

        if not structured_units:
            raise RuntimeError("No layout units extracted")

        logger.info(
            "📐 Layout extraction complete | units=%d",
            len(structured_units),
        )
        # Guard against extremely small documents
        if len(structured_units) < 2:
            logger.warning(
                "⚠️ Low unit count (%d) — document may produce weak chunks",
                len(structured_units),
            )

        file_path = self._resolve_file_path(content)
        filename = Path(file_path).name

        # ─────────────────────────────────────────────
        # 2. Semantic retrieval (RAG)
        #    (embedding + FAISS handled internally)
        # ─────────────────────────────────────────────
        logger.info("🧠 Performing semantic retrieval (RAG)")

        from app.services.rag import (
            retrieve_relevant_units,
            select_groups_by_char_budget,
        )

        retrieved_groups = retrieve_relevant_units(
            structured_units=structured_units,
            top_k=12,        # loose recall
            max_groups=40,   # hard guardrail
        )

        if not retrieved_groups:
            raise RuntimeError("RAG retrieval returned no groups")

        logger.info(
            "📦 Retrieved semantic groups | count=%d",
            len(retrieved_groups),
        )
        logger.debug(
            "🔎 RAG sample group preview (first 200 chars): %s",
            retrieved_groups[0]["text"][:200] if retrieved_groups else "N/A",
        )

        # ─────────────────────────────────────────────
        # 3. Dynamic budget-based selection
        # ─────────────────────────────────────────────
        logger.info("🧠 Applying dynamic context budget")

        budgeted_groups = select_groups_by_char_budget(
            groups=retrieved_groups,
            max_context_chars=10_000,
            max_group_chars=2_500,
        )

        if not budgeted_groups:
            raise RuntimeError("All groups exceeded context budget")

        logger.info(
            "🧩 Budgeted groups selected | groups=%d | chars=%d",
            len(budgeted_groups),
            sum(len(g["text"]) for g in budgeted_groups),
        )

        # ─────────────────────────────────────────────
        # 4. LLM chunk synthesis
        # ─────────────────────────────────────────────
        logger.info("✍️ Compiling learning chunks via LLM")
        logger.info(
            "🧠 LLM input summary | groups=%d | total_chars=%d",
            len(budgeted_groups),
            sum(len(g["text"]) for g in budgeted_groups),
        )

        chunks = await compile_cards(
            structured_units=budgeted_groups,
            document_title=content.title or filename,
        )

        if not chunks:
            raise RuntimeError("LLM returned no chunks")

        logger.info(
            "🧾 Document chunks compiled successfully | chunks=%d",
            len(chunks),
        )

        return chunks

    # ─────────────────────────────────────────────
    # Video pipeline (visual-first)
    # ─────────────────────────────────────────────


    # ─────────────────────────────────────────────
    # Persistence
    # ─────────────────────────────────────────────
    def _persist_chunks(
        self, db: Session, content: ContentItem, chunks: List[dict]
    ) -> None:
        logger.info("💾 Persisting chunks")

        for idx, chunk in enumerate(chunks):
            db.add(
                ContentChunk(
                    content_item_id=content.id,
                    sequence_number=idx + 1,
                    title=chunk["title"],
                    summary=chunk["summary"],
                    text_content="\n".join(chunk["bullets"]),
                    key_concepts=chunk.get("focus_words", []),
                    source_file=chunk.get("source", {}).get("file"),
                    source_page=chunk.get("source", {}).get("page"),
                    source_slide=chunk.get("source", {}).get("slide"),
                    card_json=json.dumps(chunk, ensure_ascii=False),
                )
            )
        logger.debug(
            "📦 Prepared %d chunks for persistence (content_id=%s)",
            len(chunks),
            content.id,
        )

        db.commit()
        logger.info("✅ All chunks saved")

    # ─────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────
    def _resolve_file_bytes(self, content: ContentItem) -> Tuple[bytes, str]:
        logger.debug("🔍 Resolving file bytes")

        candidates = (
            "storage_path",
            "storage_key",
            "file_path",
            "upload_path",
            "local_path",
            "storage_url",
            "origin_url",
            "download_url",
            "s3_key",
        )

        for attr in candidates:
            val = getattr(content, attr, None)
            if not val:
                continue

            try:
                if isinstance(val, str) and val.startswith(("http://", "https://")):
                    logger.info(f"🌐 Fetching file from URL field: {attr}")
                    r = requests.get(val, timeout=15)
                    r.raise_for_status()
                    return r.content, attr

                logger.info(f"📂 Loading file from storage field: {attr}")
                return self.storage.get_bytes(val), attr

            except Exception as e:
                logger.debug(f"❌ Failed resolving {attr}: {e}")

        logger.error("🚫 No valid storage source resolved")
        raise RuntimeError("No valid storage source found")


    def _resolve_file_path(self, content: ContentItem) -> str:
        """
        Resolves the actual filesystem path for the content item.
        """
        if not content.file_path:
            raise RuntimeError(f"ContentItem {content.id} does not have a file_path.")
        return content.file_path


    def _safe_filename(self, content: ContentItem) -> str:
        return (
            getattr(content, "file_name", None)
            or Path(getattr(content, "file_path", "")).name
            or content.title
            or "untitled"
        )

    def _load_or_extract_layout_units(
        self, content: ContentItem
    ) -> List[dict]:
        """
        Extract layout-aware structural units from a document.
        Operates strictly on filesystem path.
        """
        logger.info("📐 Extracting layout-aware units")

        file_path = self._resolve_file_path(content)
        logger.info(f"📁 Using file path for layout extraction: {file_path}")

        units = extract_layout_units(file_path)

        if not units:
            logger.error("❌ No layout units extracted")
            raise RuntimeError("No layout units extracted")

        logger.info(f"✅ Extracted {len(units)} layout units")
        return units


# Shared singleton
processor = ContentProcessor()
