import os
from pathlib import Path
import yt_dlp
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)

class VideoDownloader:
    def __init__(self):
        # Setup media directory
        self.media_root = Path(settings.MEDIA_ROOT)
        self.videos_dir = self.media_root / 'videos'
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"VideoDownloader initialized. Videos directory: {self.videos_dir}")

    def get_safe_filename(self, title):
        """Convert video title to safe filename."""
        # Replace invalid characters with underscores using regex
        safe_title = re.sub(r'[^\w\s-]', '_', title)
        # Replace multiple spaces or underscores with single underscore
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        # Trim the title to a reasonable length
        safe_title = safe_title[:50].strip('_')
        
        # Ensure filename is unique
        base_name = safe_title
        counter = 1
        final_name = f"{base_name}.mp4"
        
        while (self.videos_dir / final_name).exists():
            final_name = f"{base_name}_{counter}.mp4"
            counter += 1
        
        logger.info(f"Generated safe filename: {final_name}")
        return final_name

    def download_video(self, url):
        """Download YouTube video and return video information."""
        logger.info(f"Starting download for URL: {url}")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Prefer MP4 format
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'nocheckcertificate': True,
            'ignoreerrors': False
        }

        try:
            # First extract video information
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("Extracting video info...")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    logger.error("Could not extract video information")
                    return {
                        'success': False,
                        'error': 'Could not extract video information'
                    }

                video_title = info.get('title', 'untitled')
                filename = self.get_safe_filename(video_title)
                filepath = self.videos_dir / filename

                logger.info(f"Video title: {video_title}")
                logger.info(f"Target filepath: {filepath}")

                # Update options with final output template
                ydl_opts.update({
                    'outtmpl': str(filepath),
                })

            # Then download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("Starting video download...")
                ydl.download([url])

            if filepath.exists():
                logger.info(f"Video file exists at: {filepath}")
                return {
                    'success': True,
                    'filename': filename,
                    'title': video_title,
                    'filepath': str(filepath),
                    'url': f"/media/videos/{filename}"
                }
            else:
                logger.error("Download appeared to succeed but file not found")
                return {
                    'success': False,
                    'error': 'Download completed but file not found'
                }

        except Exception as e:
            logger.exception("Error during video download")
            return {
                'success': False,
                'error': str(e)
            }

    def clean_old_videos(self, max_age_days=7):
        """Clean up old videos to prevent disk space issues."""
        try:
            current_time = time.time()
            for video_file in self.videos_dir.glob('*.mp4'):
                file_age_days = (current_time - video_file.stat().st_mtime) / (24 * 3600)
                if file_age_days > max_age_days:
                    video_file.unlink()
                    logger.info(f"Deleted old video: {video_file}")
        except Exception as e:
            logger.error(f"Error cleaning old videos: {e}")
