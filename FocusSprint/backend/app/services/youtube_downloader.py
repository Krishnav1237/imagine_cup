"""
YouTube video downloader using yt-dlp.
Downloads audio for transcription.
"""
import logging
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import yt_dlp

from app.config import settings
from app.services.storage.adapter import get_storage_adapter

logger = logging.getLogger("YouTubeDownloader")

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
        Download audio from YouTube video.
        """
        try:
            logger.info(f"📥 Starting audio download for URL: {url}")
            
            # Generate temporary filename
            temp_file = self.temp_dir / f"{hash(url)}.mp3"
            
            # Enhanced yt-dlp options to avoid 403 errors
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
                # Anti-403 options
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'nocheckcertificate': True,
                'age_limit': None,
                # Use oauth2 if available
                'username': 'oauth2',
                'password': '',
                # Retry logic
                'retries': 3,
                'fragment_retries': 3,
                'skip_unavailable_fragments': True,
                # Additional headers
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                }
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
                
                logger.info(f"✅ Audio saved to {final_path}")
                return final_path
            
            logger.error("❌ Audio file was not created by yt-dlp")
            return None
        
        except Exception as e:
            logger.error(f"❌ Error downloading YouTube audio: {e}")
            return None
    
    def _download_with_ytdlp(self, url: str, opts: dict):
        """Download using yt-dlp (synchronous)"""
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    
    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get video information without downloading.
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                # Anti-403 options
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'nocheckcertificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                }
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
            logger.error(f"❌ Error getting video info: {e}")
            return None
    
    def _get_info_with_ytdlp(self, url: str, opts: dict) -> Optional[dict]:
        """Get info using yt-dlp (synchronous)"""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            logger.error(f"yt-dlp error: {e}")
            return None
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is a valid YouTube URL.
        """
        youtube_domains = [
            'youtube.com',
            'www.youtube.com',
            'youtu.be',
            'm.youtube.com'
        ]
        
        return any(domain in url for domain in youtube_domains)