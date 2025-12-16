"""
YouTube video downloader using yt-dlp
Downloads audio for transcription
"""
import os
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import yt_dlp

from app.config import settings
from app.services.storage.adapter import get_storage_adapter


class YouTubeDownloader:
    """YouTube video downloader"""
    
    def __init__(self):
        self.storage = get_storage_adapter()
        self.temp_dir = Path(settings.UPLOAD_DIR) / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_audio(
        self,
        url: str,
        destination_folder: str
    ) -> Optional[str]:
        """
        Download audio from YouTube video
        
        Args:
            url: YouTube video URL
            destination_folder: Destination folder in storage
        
        Returns:
            Path to downloaded audio file
        """
        try:
            # Generate temporary filename
            temp_file = self.temp_dir / f"{hash(url)}.mp3"
            
            # yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(temp_file.with_suffix('')),
                'quiet': True,
                'no_warnings': True,
            }
            
            # Download in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._download_with_ytdlp,
                url,
                ydl_opts
            )
            
            # Move to permanent storage
            final_path = f"{destination_folder}/audio.mp3"
            
            if temp_file.exists():
                with open(temp_file, 'rb') as f:
                    await self.storage.save_file(f, final_path, 'audio/mpeg')
                
                # Clean up temp file
                temp_file.unlink()
                
                return final_path
            
            return None
        
        except Exception as e:
            print(f"Error downloading YouTube audio: {e}")
            return None
    
    def _download_with_ytdlp(self, url: str, opts: dict):
        """Download using yt-dlp (synchronous)"""
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    
    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get video information without downloading
        
        Args:
            url: YouTube video URL
        
        Returns:
            Dictionary with video info (title, duration, etc.)
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None,
                self._get_info_with_ytdlp,
                url,
                ydl_opts
            )
            
            if info:
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),  # in seconds
                    'description': info.get('description'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                }
            
            return None
        
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def _get_info_with_ytdlp(self, url: str, opts: dict) -> Optional[dict]:
        """Get info using yt-dlp (synchronous)"""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"yt-dlp error: {e}")
            return None
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is a valid YouTube URL
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid YouTube URL
        """
        youtube_domains = [
            'youtube.com',
            'www.youtube.com',
            'youtu.be',
            'm.youtube.com'
        ]
        
        return any(domain in url for domain in youtube_domains)