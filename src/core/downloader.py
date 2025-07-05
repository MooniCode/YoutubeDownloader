"""
Core download functionality using yt-dlp
Handles video downloads, progress tracking, and format selection.
"""

import os
import yt_dlp
from typing import Dict, Any, Callable, Optional
from .cookies import CookieManager

class DownloadEngine:
    """Core download engine using yt-dlp"""
    
    def __init__(self, cookie_manager: CookieManager):
        """
        Initialize download engine
        
        Args:
            cookie_manager: Cookie management instance
        """
        self.cookie_manager = cookie_manager
        self.progress_callback: Optional[Callable] = None
        self.log_callback: Optional[Callable] = None
        
    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_log_callback(self, callback: Callable):
        """Set callback for log messages"""
        self.log_callback = callback
    
    def _log(self, message: str):
        """Log a message"""
        if self.log_callback:
            self.log_callback(message)
    
    def _progress_hook(self, d: Dict[str, Any]):
        """Progress hook for yt-dlp"""
        if not self.progress_callback:
            return
            
        if d['status'] == 'downloading':
            # Calculate percentage
            if 'total_bytes' in d:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            elif 'total_bytes_estimate' in d:
                percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
            else:
                percent = 0
            
            # Format downloaded size
            downloaded_mb = d['downloaded_bytes'] / (1024 * 1024)
            
            if 'total_bytes' in d:
                total_mb = d['total_bytes'] / (1024 * 1024)
                status_text = f"Downloading: {percent:.1f}% ({downloaded_mb:.1f}MB / {total_mb:.1f}MB)"
            elif 'total_bytes_estimate' in d:
                total_mb = d['total_bytes_estimate'] / (1024 * 1024)
                status_text = f"Downloading: {percent:.1f}% ({downloaded_mb:.1f}MB / ~{total_mb:.1f}MB)"
            else:
                status_text = f"Downloading: {downloaded_mb:.1f}MB"
            
            # Add speed if available
            if 'speed' in d and d['speed']:
                speed_mb = d['speed'] / (1024 * 1024)
                status_text += f" - {speed_mb:.1f} MB/s"
            
            self.progress_callback(percent, status_text)
            
        elif d['status'] == 'finished':
            self.progress_callback(100, "Download finished - Processing...")
            self._log(f"Downloaded: {d['filename']}")
            
        elif d['status'] == 'error':
            self.progress_callback(0, "Download failed")
    
    def get_format_string(self, quality: str) -> str:
        """
        Get yt-dlp format string for specified quality
        
        Args:
            quality: Quality setting ('best', '1080p', '720p', 'audio')
            
        Returns:
            Format string for yt-dlp
        """
        if quality == "best":
            return 'bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[acodec^=mp4a][ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif quality == "1080p":
            return 'bestvideo[height<=1080][vcodec^=avc1][ext=mp4]+bestaudio[acodec^=mp4a][ext=m4a]/bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
        elif quality == "720p":
            return 'bestvideo[height<=720][vcodec^=avc1][ext=mp4]+bestaudio[acodec^=mp4a][ext=m4a]/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
        elif quality == "audio":
            return 'bestaudio[acodec^=mp4a]/bestaudio/best'
        else:
            return 'best'
    
    def extract_info(self, url: str) -> Dict[str, Any]:
        """
        Extract video information without downloading
        
        Args:
            url: YouTube URL
            
        Returns:
            Video information dictionary
            
        Raises:
            yt_dlp.DownloadError: If extraction fails
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        # Add cookie options
        cookie_opts = self.cookie_manager.get_cookie_options()
        ydl_opts.update(cookie_opts)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    
    def download(self, url: str, output_path: str, quality: str = "1080p") -> bool:
        """
        Download video from URL
        
        Args:
            url: YouTube URL
            output_path: Directory to save video
            quality: Quality setting
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)
            
            format_string = self.get_format_string(quality)
            
            ydl_opts = {
                'format': format_string,
                'outtmpl': f'{output_path}/%(title)s.%(ext)s',
                'merge_output_format': 'mp4' if quality != "audio" else None,
                'progress_hooks': [self._progress_hook],
                'postprocessors': [],
            }
            
            # Add cookie options
            cookie_opts = self.cookie_manager.get_cookie_options()
            ydl_opts.update(cookie_opts)
            
            # Add video post-processor to ensure H.264 codec for video downloads
            if quality != "audio":
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                })
            
            # Add audio postprocessor for audio-only downloads
            if quality == "audio":
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                })
            
            # Update progress
            if self.progress_callback:
                self.progress_callback(0, "Extracting video information...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self._log("Extracting video information...")
                
                # Log cookie usage
                if self.cookie_manager.use_cookies:
                    if self.cookie_manager.cookie_source == "browser":
                        self._log(f"Attempting to use cookies from {self.cookie_manager.browser_choice} browser...")
                    else:
                        self._log("Attempting to use cookies from file...")
                
                # Extract info first
                info = ydl.extract_info(url, download=False)
                
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 'Unknown')
                age_limit = info.get('age_limit', 0)
                
                self._log(f"Title: {title}")
                if duration != 'Unknown':
                    minutes, seconds = divmod(duration, 60)
                    self._log(f"Duration: {int(minutes)}:{int(seconds):02d}")
                
                if age_limit > 0:
                    self._log(f"Age restriction detected: {age_limit}+")
                    if not self.cookie_manager.use_cookies:
                        self._log("Warning: This video is age-restricted. Consider enabling cookies for better success rate.")
                
                # Start download
                if self.progress_callback:
                    self.progress_callback(0, "Starting download...")
                self._log("Starting download...")
                
                ydl.download([url])
                
                # Success
                if self.progress_callback:
                    self.progress_callback(100, "Completed successfully!")
                self._log("Download completed successfully!")
                if quality != "audio":
                    self._log("Video saved in H.264 format for maximum compatibility!")
                
                return True
                
        except yt_dlp.DownloadError as e:
            error_msg = str(e)
            if self.progress_callback:
                self.progress_callback(0, "Download failed")
            self._log(f"Download Error: {error_msg}")
            
            # Check if this might be an age-restriction issue
            if "age" in error_msg.lower() or "sign in" in error_msg.lower() or "verify" in error_msg.lower():
                if not self.cookie_manager.use_cookies:
                    self._log("\n" + "="*50)
                    self._log("SUGGESTION: This appears to be an age-restricted video.")
                    self._log("Try enabling 'Use cookies for age-restricted videos' above.")
                    self._log("This will use your browser's login session to bypass the restriction.")
                    self._log("="*50)
                else:
                    self._log("\n" + "="*50)
                    self._log("Cookie authentication failed. This could be due to:")
                    self._log("1. You're not logged into YouTube in your browser")
                    self._log("2. Your browser cookies are outdated")
                    self._log("3. The selected browser doesn't have YouTube cookies")
                    self._log("Try logging into YouTube in your browser and retry.")
                    self._log("="*50)
            
            return False
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(0, "Error occurred")
            self._log(f"Error: {str(e)}")
            return False