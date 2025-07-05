"""
FFmpeg detection and management utilities
Handles FFmpeg availability checking and provides installation guidance.
"""

import subprocess
import shutil
import webbrowser
import os
import sys
from typing import Optional

class FFmpegManager:
    """Manages FFmpeg detection and installation guidance"""
    
    def __init__(self, installation_guide_url: Optional[str] = None):
        """
        Initialize FFmpeg manager
        
        Args:
            installation_guide_url: URL to custom installation guide
        """
        self.installation_guide_url = installation_guide_url or self._get_default_guide_url()
        self._is_available = None  # Cache the result
    
    def _get_subprocess_kwargs(self) -> dict:
        """Get subprocess kwargs that hide console windows on Windows"""
        kwargs = {
            'capture_output': True,
            'text': True,
            'timeout': 5
        }
        
        # Hide console window on Windows
        if os.name == 'nt':  # Windows
            kwargs['startupinfo'] = subprocess.STARTUPINFO()
            kwargs['startupinfo'].dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs['startupinfo'].wShowWindow = subprocess.SW_HIDE
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        return kwargs
    
    def _get_default_guide_url(self) -> str:
        """Get default FFmpeg installation guide URL"""
        # You can replace this with your custom Google Docs guide
        return "https://docs.google.com/document/d/1P9kSEdciggUlDxPvz-gbpKtTGatBlRskyylPLwpvQtI/edit?usp=sharing"
    
    def is_available(self, force_check: bool = False) -> bool:
        """
        Check if FFmpeg is available on the system
        
        Args:
            force_check: Force a new check instead of using cached result
            
        Returns:
            True if FFmpeg is available, False otherwise
        """
        if self._is_available is not None and not force_check:
            return self._is_available
        
        try:
            # Try to run ffmpeg with version flag - with hidden console
            result = subprocess.run(['ffmpeg', '-version'], **self._get_subprocess_kwargs())
            self._is_available = result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Also check if ffmpeg is available through shutil.which
            self._is_available = shutil.which('ffmpeg') is not None
        
        return self._is_available
    
    def get_version(self) -> Optional[str]:
        """
        Get FFmpeg version string
        
        Returns:
            Version string if available, None otherwise
        """
        if not self.is_available():
            return None
        
        try:
            result = subprocess.run(['ffmpeg', '-version'], **self._get_subprocess_kwargs())
            if result.returncode == 0:
                # Extract version from first line
                first_line = result.stdout.split('\n')[0]
                if 'ffmpeg version' in first_line:
                    return first_line.split(' ')[2]
        except Exception:
            pass
        
        return None
    
    def get_status_text(self) -> str:
        """
        Get status text for UI display
        
        Returns:
            Status text string
        """
        if self.is_available():
            version = self.get_version()
            if version:
                return f"✓ FFmpeg: Available (v{version})"
            else:
                return "✓ FFmpeg: Available"
        else:
            return "⚠ FFmpeg: Not Found"
    
    def get_status_color(self) -> str:
        """
        Get status color for UI display
        
        Returns:
            Color string ("green" or "red")
        """
        return "green" if self.is_available() else "red"
    
    def requires_ffmpeg(self, quality: str) -> bool:
        """
        Check if a quality setting requires FFmpeg
        
        Args:
            quality: Quality setting string
            
        Returns:
            True if FFmpeg is required, False otherwise
        """
        # Most quality settings require FFmpeg for optimal results
        return quality in ["best", "1080p", "720p", "audio"]
    
    def get_warning_message(self) -> str:
        """
        Get warning message for when FFmpeg is not available
        
        Returns:
            Warning message string
        """
        return (
            "FFmpeg is not detected on your system.\n\n"
            "FFmpeg is required for:\n"
            "• High-quality video downloads (1080p, Best Available)\n"
            "• Audio-only downloads (MP3 conversion)\n"
            "• Merging video and audio streams\n\n"
            "Some basic downloads might still work, but for full functionality, "
            "please install FFmpeg.\n\n"
            "Would you like to see installation instructions?"
        )
    
    def get_quality_warning_message(self, quality: str) -> str:
        """
        Get warning message for quality settings that require FFmpeg
        
        Args:
            quality: Quality setting
            
        Returns:
            Warning message string
        """
        return (
            f"The selected quality '{quality}' requires FFmpeg, which is not installed.\n\n"
            "You can:\n"
            "• Install FFmpeg and try again (Recommended)\n"
            "• Continue anyway (may fail or download lower quality)\n"
            "• Cancel and change quality settings\n\n"
            "Do you want to see FFmpeg installation instructions?"
        )
    
    def open_installation_guide(self) -> bool:
        """
        Open FFmpeg installation guide in browser
        
        Returns:
            True if opened successfully, False otherwise
        """
        try:
            webbrowser.open(self.installation_guide_url)
            return True
        except Exception:
            return False
    
    def recheck_availability(self) -> bool:
        """
        Force recheck of FFmpeg availability
        
        Returns:
            True if now available, False otherwise
        """
        return self.is_available(force_check=True)
    
    def get_supported_formats(self) -> list:
        """
        Get list of formats that work best with current FFmpeg status
        
        Returns:
            List of recommended format strings
        """
        if self.is_available():
            return [
                ("Best Available", "best"),
                ("1080p", "1080p"),
                ("720p", "720p"),
                ("Audio Only (MP3)", "audio")
            ]
        else:
            return [
                ("Best Available (Limited)", "best"),
                ("720p (Limited)", "720p")
            ]