"""
Transcription service interface and implementations.
Supports timestamped transcription for video chaptering.
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from pathlib import Path
import re

from app.config import settings

logger = logging.getLogger("Transcriber")

# ==========================================================
# Abstract interface
# ==========================================================
class Transcriber(ABC):
    """Abstract transcriber interface"""

    @abstractmethod
    async def transcribe_audio(self, audio_path: str) -> Optional[str]:
        pass

    @abstractmethod
    async def transcribe_audio_with_timestamps(
        self, audio_path: str
    ) -> Optional[List[Dict]]:
        pass


# ==========================================================
# Whisper (local, preferred)
# ==========================================================
class WhisperTranscriber(Transcriber):
    """Local Whisper transcriber"""

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            import whisper
            logger.info("⏳ Loading Whisper model (base)")
            self.model = whisper.load_model("base")
            logger.info("✅ Whisper model loaded")
        except Exception as e:
            logger.error(f"❌ Whisper load failed: {e}")

    async def transcribe_audio(self, audio_path: str) -> Optional[str]:
        segments = await self.transcribe_audio_with_timestamps(audio_path)
        if not segments:
            return None
        return " ".join(seg["text"] for seg in segments)

    async def transcribe_audio_with_timestamps(
        self, audio_path: str
    ) -> Optional[List[Dict]]:
        if not self.model:
            return None

        audio_file = await self._resolve_audio_path(audio_path)

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.model.transcribe,
                audio_file,
            )

            return [
                {
                    "start": float(seg["start"]),
                    "end": float(seg["end"]),
                    "text": seg["text"].strip(),
                }
                for seg in result.get("segments", [])
            ]

        except Exception as e:
            logger.error(f"❌ Whisper transcription failed: {e}")
            return None

    async def _resolve_audio_path(self, audio_path: str) -> str:
        """
        Resolve an audio path to a local filesystem path.

        Supports:
        - Absolute paths (for directly uploaded audio/video files)
        - Relative storage paths (e.g. \"user_id/content_id/audio.mp3\")
        """
        p = Path(audio_path)
        if p.is_absolute() and p.exists():
            # Direct absolute path (e.g. uploaded video file on local disk)
            return str(p)

        if settings.is_local:
            path = Path(settings.UPLOAD_DIR) / audio_path
            if not path.exists():
                raise FileNotFoundError(path)
            return str(path)

        from app.services.storage.adapter import get_storage_adapter
        storage = get_storage_adapter()
        tmp = Path("/tmp") / Path(audio_path).name
        tmp.write_bytes(await storage.get_file(audio_path))
        return str(tmp)


# ==========================================================
# Azure Speech (fallback, NO timestamps)
# ==========================================================
class AzureSpeechTranscriber(Transcriber):
    def __init__(self):
        if not settings.AZURE_SPEECH_KEY:
            raise RuntimeError("Azure Speech not configured")

        import azure.cognitiveservices.speech as speechsdk

        self.speechsdk = speechsdk
        self.config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SPEECH_REGION,
        )

    async def transcribe_audio(self, audio_path: str) -> Optional[str]:
        segments = await self.transcribe_audio_with_timestamps(audio_path)
        if not segments:
            return None
        return " ".join(seg["text"] for seg in segments)

    async def transcribe_audio_with_timestamps(
        self, audio_path: str
    ) -> Optional[List[Dict]]:
        text = await self._transcribe_plain(audio_path)
        if not text:
            return None
        return [{"start": None, "end": None, "text": text}]

    async def _transcribe_plain(self, audio_path: str) -> Optional[str]:
        from app.services.storage.adapter import get_storage_adapter

        storage = get_storage_adapter()
        tmp = Path("/tmp") / Path(audio_path).name
        tmp.write_bytes(await storage.get_file(audio_path))

        audio_cfg = self.speechsdk.AudioConfig(filename=str(tmp))
        recognizer = self.speechsdk.SpeechRecognizer(
            speech_config=self.config,
            audio_config=audio_cfg,
        )

        done = False
        text_chunks = []

        def recognized(evt):
            if evt.result.text:
                text_chunks.append(evt.result.text)

        def stop(_):
            nonlocal done
            done = True

        recognizer.recognized.connect(recognized)
        recognizer.session_stopped.connect(stop)
        recognizer.canceled.connect(stop)

        recognizer.start_continuous_recognition()
        while not done:
            await asyncio.sleep(0.5)
        recognizer.stop_continuous_recognition()

        return " ".join(text_chunks)


# ==========================================================
# YouTube transcript (native timestamps)
# ==========================================================
def get_youtube_transcript_with_timestamps(youtube_url: str) -> List[Dict]:
    """
    Fully version-independent YouTube transcript loader.

    Handles:
    - module-level APIs
    - class-based APIs
    - old + new youtube-transcript-api releases
    """

    import re
    import youtube_transcript_api as yta

    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", youtube_url)
    if not match:
        raise ValueError("Invalid YouTube URL")

    video_id = match.group(1)
    preferred_languages = ["en", "en-US", "en-GB"]

    transcript_data = None
    last_error = None

    # --------------------------------------------------
    # PATH 1 — list_transcripts (module-level)
    # --------------------------------------------------
    if hasattr(yta, "list_transcripts"):
        try:
            transcript_list = yta.list_transcripts(video_id)

            try:
                transcript = transcript_list.find_manually_created_transcript(
                    preferred_languages
                )
            except Exception:
                transcript = transcript_list.find_generated_transcript(
                    preferred_languages
                )

            transcript_data = transcript.fetch()
        except Exception as e:
            last_error = e

    # --------------------------------------------------
    # PATH 2 — get_transcript (module-level)
    # --------------------------------------------------
    if transcript_data is None and hasattr(yta, "get_transcript"):
        for lang in preferred_languages:
            try:
                transcript_data = yta.get_transcript(
                    video_id, languages=[lang]
                )
                break
            except Exception as e:
                last_error = e

        if transcript_data is None:
            try:
                transcript_data = yta.get_transcript(video_id)
            except Exception as e:
                last_error = e

    # --------------------------------------------------
    # FAIL HARD IF NOTHING WORKED
    # --------------------------------------------------
    if not transcript_data:
        raise RuntimeError(
            f"No transcript available for YouTube video {video_id}"
        ) from last_error

    # --------------------------------------------------
    # Normalize output
    # --------------------------------------------------
    segments: List[Dict] = []
    for entry in transcript_data:
        start = float(entry.get("start", 0))
        duration = float(entry.get("duration", 0))
        segments.append({
            "start": start,
            "end": start + duration,
            "text": entry.get("text", "").strip(),
        })

    if not segments:
        raise RuntimeError("Transcript parsing produced zero segments")

    logger.info("📺 YouTube transcript loaded | segments=%d", len(segments))
    return segments

# ==========================================================
# Factory
# ==========================================================
def get_transcriber() -> Transcriber:
    if settings.is_local:
        return WhisperTranscriber()
    if settings.AZURE_SPEECH_KEY:
        return AzureSpeechTranscriber()
    return WhisperTranscriber()
