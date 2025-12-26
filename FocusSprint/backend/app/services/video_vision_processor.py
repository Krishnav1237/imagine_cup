"""
Video Vision Processor - VLM-powered video analysis for ADHD-optimized learning.

Uses GPT-4 Vision or Gemini Pro Vision to analyze video frames alongside transcripts,
creating context-rich chunks that reference visual content.
"""
import asyncio
import base64
import io
import json
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import timedelta

from app.config import settings

logger = logging.getLogger("VideoVisionProcessor")


class VideoVisionProcessor:
    """
    Extracts keyframes from videos and uses VLM (Vision Language Model)
    to create chunks with visual context for ADHD-optimized learning.
    """
    
    def __init__(self):
        self.openai_client = None
        self.vision_model = None
        
        # Try to initialize OpenAI client for GPT-4V
        api_key = getattr(settings, "AZURE_OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
        endpoint = getattr(settings, "AZURE_OPENAI_ENDPOINT", None)
        
        if api_key:
            try:
                import openai
                if endpoint:
                    # Azure OpenAI
                    openai.api_key = api_key
                    openai.api_base = endpoint
                    openai.api_type = "azure"
                    openai.api_version = "2024-02-15-preview"
                    self.vision_model = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT", "gpt-4-vision-preview")
                else:
                    # Standard OpenAI
                    openai.api_key = api_key
                    self.vision_model = "gpt-4-vision-preview"
                
                self.openai_client = openai
                logger.info(f"✅ VLM initialized with model: {self.vision_model}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize VLM client: {e}")
        else:
            logger.info("ℹ️ No VLM API key configured, will use transcript-only chunking")
    
    async def extract_keyframes(
        self,
        video_path: str,
        interval_seconds: int = 30,
        max_frames: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Extract keyframes from video at regular intervals.
        
        Args:
            video_path: Path to video file
            interval_seconds: Extract a frame every N seconds
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of dicts with 'timestamp', 'frame_path', 'base64'
        """
        logger.info(f"🎬 Extracting keyframes from {video_path} (every {interval_seconds}s)")
        
        frames = []
        temp_dir = tempfile.mkdtemp(prefix="focussprint_frames_")
        
        try:
            # Get video duration using ffprobe
            duration = await self._get_video_duration(video_path)
            if not duration:
                logger.error("Could not determine video duration")
                return []
            
            # Calculate frame timestamps
            timestamps = []
            current = 0
            while current < duration and len(timestamps) < max_frames:
                timestamps.append(current)
                current += interval_seconds
            
            # Extract frames using ffmpeg
            for i, ts in enumerate(timestamps):
                output_path = os.path.join(temp_dir, f"frame_{i:04d}.jpg")
                
                # Format timestamp for ffmpeg
                time_str = str(timedelta(seconds=int(ts)))
                
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", time_str,
                    "-i", video_path,
                    "-vframes", "1",
                    "-q:v", "2",  # High quality JPEG
                    output_path
                ]
                
                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: subprocess.run(cmd, capture_output=True, timeout=30)
                    )
                    
                    if os.path.exists(output_path):
                        # Read and encode as base64
                        with open(output_path, 'rb') as f:
                            frame_base64 = base64.b64encode(f.read()).decode('utf-8')
                        
                        frames.append({
                            "timestamp": ts,
                            "timestamp_str": time_str,
                            "frame_path": output_path,
                            "base64": frame_base64,
                            "index": i
                        })
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"Frame extraction timed out at {ts}s")
                except Exception as e:
                    logger.warning(f"Failed to extract frame at {ts}s: {e}")
            
            logger.info(f"✅ Extracted {len(frames)} keyframes")
            return frames
            
        except Exception as e:
            logger.error(f"❌ Frame extraction failed: {e}")
            return []
    
    async def _get_video_duration(self, video_path: str) -> Optional[float]:
        """Get video duration in seconds using ffprobe"""
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            )
            return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"Failed to get video duration: {e}")
            return None
    
    async def analyze_with_vlm(
        self,
        frames: List[Dict[str, Any]],
        transcript: str,
        title: str = "Untitled"
    ) -> List[Dict[str, Any]]:
        """
        Analyze video frames + transcript using Vision Language Model.
        Creates chunks with visual context descriptions.
        
        Args:
            frames: List of extracted keyframes with base64 data
            transcript: Full transcript text
            title: Content title
            
        Returns:
            List of chunks with visual_context field
        """
        if not self.openai_client:
            logger.warning("VLM not available, using text-only analysis")
            return self._fallback_chunking(transcript, title)
        
        if not frames:
            logger.warning("No frames provided, using text-only analysis")
            return self._fallback_chunking(transcript, title)
        
        logger.info(f"🔍 Analyzing {len(frames)} frames with VLM...")
        
        chunks = []
        
        # Process frames in batches (to avoid token limits)
        batch_size = 4
        for i in range(0, len(frames), batch_size):
            batch_frames = frames[i:i + batch_size]
            
            # Get transcript segment for this time range
            start_time = batch_frames[0]["timestamp"]
            end_time = batch_frames[-1]["timestamp"] + 30  # Include next 30s of transcript
            
            transcript_segment = self._extract_transcript_segment(
                transcript, start_time, end_time
            )
            
            try:
                chunk = await self._analyze_batch_with_vlm(
                    batch_frames,
                    transcript_segment,
                    title,
                    start_time
                )
                if chunk:
                    chunks.append(chunk)
            except Exception as e:
                logger.warning(f"VLM analysis failed for batch {i}: {e}")
                # Fallback for this segment
                fallback = self._create_fallback_chunk(transcript_segment, title, start_time)
                if fallback:
                    chunks.append(fallback)
        
        logger.info(f"✅ Created {len(chunks)} VLM-enhanced chunks")
        return chunks
    
    async def _analyze_batch_with_vlm(
        self,
        frames: List[Dict[str, Any]],
        transcript_segment: str,
        title: str,
        start_timestamp: float
    ) -> Optional[Dict[str, Any]]:
        """Analyze a batch of frames with VLM"""
        
        # Build multimodal prompt
        messages = [
            {
                "role": "system",
                "content": """You are an expert educational content analyzer for ADHD-friendly learning.
Analyze the video frames and transcript to create a focused study chunk.

Your response MUST be valid JSON with this exact structure:
{
  "title": "Short, engaging title (max 8 words)",
  "content": ["bullet 1", "bullet 2", "bullet 3"],
  "visual_context": "Describe what's shown on screen that helps understand the content",
  "key_visual_elements": ["diagram type", "code shown", "demonstration"],
  "topic": "Main topic in 2-3 words",
  "complexity": "easy|medium|hard"
}

Rules:
- Create 3-5 concise bullet points (8-15 words each)
- Visual context should reference specific elements visible in frames
- Optimize for ADHD: clear, scannable, no fluff"""
            },
            {
                "role": "user",
                "content": []
            }
        ]
        
        # Add frames as images
        for frame in frames:
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame['base64']}",
                    "detail": "low"  # Use low detail to save tokens
                }
            })
        
        # Add transcript text
        messages[1]["content"].append({
            "type": "text",
            "text": f"""Title: {title}
Timestamp: {start_timestamp}s - {start_timestamp + 120}s

Transcript segment:
{transcript_segment[:2000]}

Analyze the frames and transcript above. Return JSON only."""
        })
        
        try:
            if hasattr(self.openai_client, 'chat'):
                # Newer OpenAI SDK
                response = self.openai_client.chat.completions.create(
                    model=self.vision_model,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.3
                )
                content = response.choices[0].message.content
            else:
                # Older SDK or Azure
                response = self.openai_client.ChatCompletion.create(
                    deployment_id=self.vision_model,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.3
                )
                content = response["choices"][0]["message"]["content"]
            
            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                chunk = json.loads(json_match.group())
                chunk["key_frame_timestamp"] = start_timestamp
                chunk["frames_analyzed"] = len(frames)
                return chunk
            else:
                logger.warning("VLM response was not valid JSON")
                return None
                
        except Exception as e:
            logger.error(f"VLM API call failed: {e}")
            raise
    
    def _extract_transcript_segment(
        self,
        transcript: str,
        start_time: float,
        end_time: float
    ) -> str:
        """
        Extract a segment of transcript based on timestamp.
        Since we don't have word-level timestamps, approximate by position.
        """
        if not transcript:
            return ""
        
        # Rough approximation: assume 150 words per minute
        words_per_second = 2.5
        words = transcript.split()
        
        start_word = int(start_time * words_per_second)
        end_word = int(end_time * words_per_second)
        
        start_word = min(start_word, len(words) - 1)
        end_word = min(end_word, len(words))
        
        return " ".join(words[start_word:end_word])
    
    def _fallback_chunking(
        self,
        transcript: str,
        title: str
    ) -> List[Dict[str, Any]]:
        """Fallback text-only chunking when VLM is not available"""
        chunks = []
        words = transcript.split()
        chunk_size = 300  # ~2 minutes of speech
        
        for i in range(0, len(words), chunk_size):
            segment = " ".join(words[i:i + chunk_size])
            chunk = self._create_fallback_chunk(segment, title, i / 2.5)
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _create_fallback_chunk(
        self,
        text: str,
        title: str,
        timestamp: float
    ) -> Optional[Dict[str, Any]]:
        """Create a basic chunk without VLM analysis"""
        if not text or len(text.split()) < 20:
            return None
        
        # Simple extraction of key sentences
        sentences = text.replace('\n', ' ').split('.')
        key_sentences = [s.strip() for s in sentences[:5] if len(s.strip()) > 20]
        
        return {
            "title": f"{title} - Part {int(timestamp / 60) + 1}",
            "content": key_sentences[:4] if key_sentences else ["Content segment"],
            "visual_context": "Visual analysis not available for this segment",
            "key_visual_elements": [],
            "topic": title,
            "complexity": "medium",
            "key_frame_timestamp": timestamp,
            "is_fallback": True
        }
    
    def cleanup_frames(self, frames: List[Dict[str, Any]]):
        """Clean up temporary frame files"""
        for frame in frames:
            try:
                if os.path.exists(frame.get("frame_path", "")):
                    os.unlink(frame["frame_path"])
            except Exception:
                pass


# Global processor instance
video_vision_processor = VideoVisionProcessor()
