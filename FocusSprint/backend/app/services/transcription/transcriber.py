"""
Transcription service interface and implementations.
Supports both Whisper (local) and Azure Speech Services.
"""
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path

from app.config import settings

logger = logging.getLogger("Transcriber")

class Transcriber(ABC):
    """Abstract transcriber interface"""
    
    @abstractmethod
    async def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file to text.
        """
        pass

class WhisperTranscriber(Transcriber):
    """OpenAI Whisper transcriber (local)"""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load Whisper model."""
        try:
            import whisper
            # Use 'base' model for balance of speed and accuracy
            logger.info("⏳ Loading Whisper model 'base'...")
            self.model = whisper.load_model("base")
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"⚠️ Warning: Could not load Whisper model: {e}")
    
    async def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using Whisper"""
        if not self.model:
            logger.error("Whisper model not loaded")
            return None
        
        try:
            # Get actual file path from storage
            from app.services.storage.adapter import get_storage_adapter
            storage = get_storage_adapter()
            
            # For local storage, construct full path
            if settings.is_local:
                full_path = Path(settings.UPLOAD_DIR) / audio_path
                if not full_path.exists():
                    logger.error(f"Audio file not found: {full_path}")
                    return None
                
                audio_file = str(full_path)
            else:
                # For cloud storage, download temporarily
                temp_path = Path("/tmp") / Path(audio_path).name
                file_data = await storage.get_file(audio_path)
                
                with open(temp_path, 'wb') as f:
                    f.write(file_data)
                
                audio_file = str(temp_path)
            
            logger.info(f"🎙️ Starting local transcription for {audio_file}")
            
            # Run transcription in executor (CPU intensive)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                audio_file
            )
            
            # Clean up temp file if created
            if not settings.is_local and Path(audio_file).exists():
                Path(audio_file).unlink()
            
            logger.info("✅ Transcription complete")
            return result.get('text') if result else None
        
        except Exception as e:
            logger.error(f"❌ Error transcribing with Whisper: {e}")
            return None
    
    def _transcribe_sync(self, audio_file: str) -> dict:
        """Synchronous transcription"""
        return self.model.transcribe(audio_file)

class AzureSpeechTranscriber(Transcriber):
    """Azure Speech Services transcriber"""
    
    def __init__(self):
        if not settings.AZURE_SPEECH_KEY or not settings.AZURE_SPEECH_REGION:
            raise ValueError("Azure Speech credentials not configured")
        
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            self.speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_SPEECH_REGION
            )
            self.speech_config.speech_recognition_language = "en-US"
            logger.info("✅ Azure Speech Services configured")
        except ImportError:
            raise ImportError("Azure Speech SDK not installed")
    
    async def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using Azure Speech Services"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Get audio file
            from app.services.storage.adapter import get_storage_adapter
            storage = get_storage_adapter()
            
            if settings.is_local:
                full_path = Path(settings.UPLOAD_DIR) / audio_path
                audio_file = str(full_path)
            else:
                # Download from blob storage
                temp_path = Path("/tmp") / Path(audio_path).name
                file_data = await storage.get_file(audio_path)
                
                with open(temp_path, 'wb') as f:
                    f.write(file_data)
                
                audio_file = str(temp_path)
            
            # Create audio config
            audio_config = speechsdk.AudioConfig(filename=audio_file)
            
            # Create recognizer
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            logger.info(f"🎙️ Starting Azure transcription for {audio_file}")
            
            # Perform recognition
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._recognize_sync,
                speech_recognizer
            )
            
            # Clean up temp file
            if not settings.is_local and Path(audio_file).exists():
                Path(audio_file).unlink()
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error transcribing with Azure Speech: {e}")
            return None
    
    def _recognize_sync(self, recognizer) -> Optional[str]:
        """Synchronous recognition"""
        import azure.cognitiveservices.speech as speechsdk
        
        all_text = []
        done = False
        
        def stop_cb(evt):
            nonlocal done
            done = True
        
        def recognized_cb(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                all_text.append(evt.result.text)
        
        recognizer.recognized.connect(recognized_cb)
        recognizer.session_stopped.connect(stop_cb)
        recognizer.canceled.connect(stop_cb)
        
        recognizer.start_continuous_recognition()
        
        # Wait for completion
        import time
        while not done:
            time.sleep(0.5)
        
        recognizer.stop_continuous_recognition()
        
        return ' '.join(all_text) if all_text else None

def get_transcriber() -> Transcriber:
    """
    Factory function to get appropriate transcriber based on deployment mode.
    """
    if settings.is_local:
        return WhisperTranscriber()
    else:
        if settings.AZURE_SPEECH_KEY:
            return AzureSpeechTranscriber()
        else:
            return WhisperTranscriber()