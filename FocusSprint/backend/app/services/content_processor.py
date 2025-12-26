import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Tuple

import requests
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import ContentItem, ContentChunk
from app.schemas.schemas import ContentSourceType, ContentStatus
from app.config import settings

from app.services.storage.adapter import get_storage_adapter
from app.services.transcription.transcriber import get_transcriber
from app.services.youtube_downloader import YouTubeDownloader

# ─────────────────────────────────────────────
# New hybrid pipeline services
# ─────────────────────────────────────────────
from app.services.chunking.ollama_card_compiler import compile_cards

from app.services.video_pipeline.video_downloader import download_video
from app.services.vlm.scene_segmenter import segment_scenes
from app.services.vlm.frame_sampler import sample_frames
from app.services.document_extraction.layout_extractor import extract_layout_units
from app.services.video_pipeline.vlm_video_analyzer import analyze_video_segments
from app.services.chunking.video_chunk_compiler import compile_video_chunks


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
                f"📄 Content loaded | id={content.id} | type={content.source_type}"
            )

            # ─────────────────────────────────────────────
            # Mark processing start
            # ─────────────────────────────────────────────
            content.status = ContentStatus.PROCESSING
            content.stage = "INITIALIZING"
            logger.info(
                "📊 Processing metadata | source_type=%s | user_id=%s",
                content.source_type,
                content.user_id,
            )
            content.processed_at = datetime.now(timezone.utc)
            content.error_message = None
            db.commit()
            
            # Broadcast status via WebSocket
            await broadcast_status(content.user_id, content.id, "processing", "INITIALIZING")

            chunks: List[dict]

            # ─────────────────────────────────────────────
            # Route by content type
            # ─────────────────────────────────────────────
            if content.source_type in {
                ContentSourceType.PDF,
                ContentSourceType.PPTX,
            }:
                content.stage = "DOCUMENT_PIPELINE"
                db.commit()
                await broadcast_status(content.user_id, content.id, "processing", "DOCUMENT_PIPELINE")

                chunks = await self._process_document(content)

            elif content.source_type == ContentSourceType.YOUTUBE:
                content.stage = "VIDEO_PIPELINE"
                db.commit()
                await broadcast_status(content.user_id, content.id, "processing", "VIDEO_PIPELINE")

                chunks = await self._process_video(content, db)

            else:
                raise RuntimeError(
                    f"Unsupported source type: {content.source_type}"
                )

            # ─────────────────────────────────────────────
            # Validate output
            # ─────────────────────────────────────────────
            if not chunks:
                raise RuntimeError("No chunks generated")

            # ─────────────────────────────────────────────
            # Persist chunks
            # ─────────────────────────────────────────────
            content.stage = "PERSISTING_CHUNKS"
            db.commit()

            self._persist_chunks(db, content, chunks)

            # ─────────────────────────────────────────────
            # Mark completion
            # ─────────────────────────────────────────────
            content.status = ContentStatus.COMPLETED
            content.stage = None
            content.processed_at = datetime.now(timezone.utc)
            content.error_message = None
            db.commit()
            
            # Broadcast completion via WebSocket
            await broadcast_status(content.user_id, content.id, "completed", None)
            
            elapsed = (datetime.now(timezone.utc) - start_ts).total_seconds()
            logger.info("⏱️ Total processing time: %.2fs", elapsed)

            logger.info(
                f"✅ [DONE] Content {content.id} processed → {len(chunks)} chunks"
            )

        except Exception as e:
            logger.exception("❌ Processing failed")

            try:
                content.status = ContentStatus.FAILED
                content.stage = None
                content.error_message = str(e)
                content.processed_at = self.new_method()
                db.commit()
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
    async def _process_video(
        self, content: ContentItem, db: Session
    ) -> List[dict]:
        logger.info("🎬 Video pipeline started")

        video_path: Optional[str] = None
        audio_path: Optional[str] = None
        transcript: Optional[str] = None

        try:
            # ─────────────────────────────────────────
            # 1. Download full video (temporary storage)
            # ─────────────────────────────────────────
            video_path = await download_video(
                url=content.source_url,
                output_dir=f"uploads/{content.user_id}/{content.id}/video"
            )

            logger.info(f"📥 Video downloaded → {video_path}")

            # ─────────────────────────────────────────
            # 2. Optional transcription (auxiliary signal)
            # ─────────────────────────────────────────
            try:
                audio_path = await self.youtube_downloader.download_audio(
                    content.source_url,
                    f"{content.user_id}/{content.id}",
                )

                logger.info(f"🎵 Audio extracted → {audio_path}")

                transcript = await self.transcriber.transcribe_audio(audio_path)

                if transcript:
                    content.transcript_text = transcript
                    db.commit()
                    logger.info(
                        f"📝 Transcript generated ({len(transcript)} characters)"
                    )
                else:
                    logger.warning("⚠️ Transcription returned empty text")

            except Exception as e:
                logger.warning(
                    f"⚠️ Transcription skipped (non-fatal): {e}"
                )

            # ─────────────────────────────────────────
            # 3. Context-aware visual segmentation
            # ─────────────────────────────────────────
            segments = await segment_scenes(video_path)

            if not segments:
                raise RuntimeError("No video segments detected")

            logger.info(
                f"🧩 Video segmented into {len(segments)} visual sub-topics"
            )
            if len(segments) > 50:
                logger.warning(
                    "⚠️ High segment count (%d) — video may be over-segmented",
                    len(segments),
                )

            # ─────────────────────────────────────────
            # 4. Frame sampling per segment
            # ─────────────────────────────────────────
            frames_by_segment = await sample_frames(
                video_path=video_path,
                segments=segments,
            )

            logger.info(
                f"🖼️ Frames sampled for {len(frames_by_segment)} segments"
            )

            # ─────────────────────────────────────────
            # 5. On-device VLM semantic analysis
            # ─────────────────────────────────────────
            vlm_results = await analyze_video_segments(
                frames_by_segment=frames_by_segment,
                transcript=transcript,  # auxiliary signal
                title=content.title or "Untitled Video",
            )

            if not vlm_results:
                raise RuntimeError("VLM returned no semantic results")

            logger.info(
                f"👁️ VLM analyzed {len(vlm_results)} segments successfully"
            )

            # ─────────────────────────────────────────
            # 6. Normalize VLM output → chunk cards
            # ─────────────────────────────────────────
            chunks = compile_video_chunks(
                vlm_results=vlm_results,
                source_url=content.source_url,
            )

            if not chunks:
                raise RuntimeError("Video chunk compilation returned empty output")

            logger.info(f"🧾 Video chunks compiled: {len(chunks)}")

            return chunks

        finally:
            # ─────────────────────────────────────────
            # 7. Cleanup temporary artifacts
            # ─────────────────────────────────────────
            try:
                if video_path:
                    Path(video_path).unlink(missing_ok=True)
                    logger.info("🧹 Temporary video file removed")

                if audio_path:
                    Path(audio_path).unlink(missing_ok=True)
                    logger.info("🧹 Temporary audio file removed")

            except Exception as e:
                logger.warning(f"⚠️ Cleanup failed: {e}")


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
