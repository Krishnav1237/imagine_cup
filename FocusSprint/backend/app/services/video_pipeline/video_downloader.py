import logging
from app.services.youtube_downloader import YouTubeDownloader

logger = logging.getLogger("VideoDownloader")

_downloader = YouTubeDownloader()


async def download_video(url: str, output_dir: str) -> str:
    """
    Wrapper around YouTubeDownloader.download_video
    """
    logger.info("🎬 Delegating video download to YouTubeDownloader")
    return await _downloader.download_video(
        link=url,
        output_dir=output_dir,
        filename="original"
    )
