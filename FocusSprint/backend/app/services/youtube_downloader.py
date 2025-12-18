"""
Universal video downloader for YouTube and non-YouTube sources.
Downloads audio for transcription with enhanced error handling.
"""
import logging
import asyncio
import subprocess
import requests
import os
from typing import Optional, Dict, Any
from pathlib import Path
import yt_dlp

from app.config import settings
from app.services.storage.adapter import get_storage_adapter

logger = logging.getLogger("YouTubeDownloader")

class YouTubeDownloader:
    """Universal video downloader for YouTube and other sources"""
    
    def __init__(self):
        self.storage = get_storage_adapter()
        self.temp_dir = Path(settings.UPLOAD_DIR) / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Browser headers for non-YouTube sources
        self.browser_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        }
    
    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube link"""
        youtube_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com']
        return any(domain in url for domain in youtube_domains)
    
    def _clean_youtube_url(self, url: str) -> str:
        """
        Clean YouTube URL by removing playlist and other parameters.
        Extracts just the video ID to avoid playlist processing.
        """
        import re
        
        # Handle youtu.be short URLs
        if 'youtu.be' in url:
            # Extract video ID from youtu.be/VIDEO_ID
            match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
            if match:
                return f"https://www.youtube.com/watch?v={match.group(1)}"
        
        # For youtube.com URLs, extract just the video ID
        match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
        if match:
            video_id = match.group(1)
            # Return clean URL without playlist or other parameters
            return f"https://www.youtube.com/watch?v={video_id}"
        
        # If no video ID found, return original URL
        return url
    
    async def download_audio(
        self,
        url: str,
        destination_folder: str
    ) -> Optional[str]:
        """
        Download audio from YouTube or non-YouTube video.
        Handles both sources with appropriate strategies.
        """
        try:
            logger.info(f"📥 Starting audio download for URL: {url}")
            
            # Clean YouTube URLs to remove playlist parameters
            if self._is_youtube_url(url):
                clean_url = self._clean_youtube_url(url)
                logger.info(f"🧹 Cleaned URL: {clean_url}")
                return await self._download_youtube_audio(clean_url, destination_folder)
            else:
                return await self._download_generic_audio(url, destination_folder)
        
        except Exception as e:
            logger.error(f"❌ Error downloading audio: {e}")
            return None
    
    async def _download_youtube_audio(self, url: str, destination_folder: str) -> Optional[str]:
        try:
            temp_file = self.temp_dir / f"{hash(url)}.%(ext)s"

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(temp_file),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                # mimic your working script
                'user_agent': self.browser_headers['User-Agent'],
                'referer': 'https://www.youtube.com/',
                'nocheckcertificate': True,
                'retries': 3,
                'fragment_retries': 3,
            }

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._download_with_ytdlp,
                url,
                ydl_opts
            )

            # yt-dlp will output .mp3 after postprocessing
            temp_audio = self.temp_dir / f"{hash(url)}.mp3"

            if not temp_audio.exists():
                logger.error("❌ yt-dlp did not produce audio file")
                return None

            final_path = f"{destination_folder}/audio.mp3"
            with open(temp_audio, 'rb') as f:
                await self.storage.save_file(f, final_path, 'audio/mpeg')

            temp_audio.unlink(missing_ok=True)

            logger.info(f"✅ YouTube audio saved to {final_path}")
            return final_path

        except Exception as e:
            logger.error(f"❌ Error downloading YouTube audio: {e}")
            return None

    
    async def _download_generic_audio(self, url: str, destination_folder: str) -> Optional[str]:
        """Download audio from non-YouTube sources"""
        try:
            logger.info(f"📥 Downloading audio from non-YouTube source: {url}")
            
            # Determine file extension
            file_extension = os.path.splitext(url.split('?')[0])[1] or '.mp4'
            temp_file = self.temp_dir / f"{hash(url)}{file_extension}"
            temp_audio = self.temp_dir / f"{hash(url)}.mp3"
            
            # Try yt-dlp first for better web video handling
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'outtmpl': str(temp_file.with_suffix('')),
                    'user_agent': self.browser_headers['User-Agent'],
                    'nocheckcertificate': True,
                    'http_headers': self.browser_headers,
                    'retries': 3,
                }
                
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    self._download_with_ytdlp,
                    url,
                    ydl_opts
                )
                
                if temp_file.exists():
                    logger.info(f"✅ File downloaded with yt-dlp: {temp_file}")
                else:
                    raise Exception("yt-dlp download failed, trying requests")
            
            except Exception as yt_dlp_error:
                logger.warning(f"⚠️ yt-dlp failed: {yt_dlp_error}, falling back to requests")
                
                # Fallback to requests method
                response = requests.get(url, stream=True, headers=self.browser_headers, verify=False, timeout=30)
                response.raise_for_status()
                
                with open(temp_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                logger.info(f"✅ File downloaded with requests: {temp_file}")
            
            # Convert to MP3 if needed
            if temp_file.exists():
                if file_extension.lower() != '.mp3':
                    logger.info(f"🔄 Converting {file_extension} to MP3...")
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None,
                        self._convert_to_mp3,
                        str(temp_file),
                        str(temp_audio)
                    )
                    if temp_audio.exists():
                        temp_file = temp_audio
                    else:
                        logger.warning(f"⚠️ Conversion failed, using original file")
                
                # Save to storage
                final_path = f"{destination_folder}/audio.mp3"
                with open(temp_file, 'rb') as f:
                    await self.storage.save_file(f, final_path, 'audio/mpeg')
                
                # Clean up temp files
                try:
                    temp_file.unlink()
                    if temp_audio.exists():
                        temp_audio.unlink()
                except:
                    pass
                
                logger.info(f"✅ Generic audio saved to {final_path}")
                return final_path
            
            logger.error("❌ Audio file download failed")
            return None
        
        except Exception as e:
            logger.error(f"❌ Error downloading generic audio: {e}")
            return None
    
    def _download_with_ytdlp(self, url: str, opts: dict):
        """Download using yt-dlp (synchronous)"""
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    
    def _convert_to_mp3(self, input_file: str, output_file: str):
        """Convert video/audio to MP3 using ffmpeg"""
        try:
            command = [
                "ffmpeg",
                "-i", input_file,
                "-q:a", "9",  # Quality
                "-n",  # Don't overwrite
                output_file
            ]
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"✅ Converted to MP3: {output_file}")
        except Exception as e:
            logger.error(f"❌ FFmpeg conversion error: {e}")
    
    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get video information without downloading.
        Works for both YouTube and some non-YouTube sources.
        """
        try:
            # Clean YouTube URLs before fetching info
            if self._is_youtube_url(url):
                url = self._clean_youtube_url(url)
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                # Anti-403 options
                'user_agent': self.browser_headers['User-Agent'],
                'referer': 'https://www.youtube.com/',
                'nocheckcertificate': True,
                'http_headers': self.browser_headers,
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