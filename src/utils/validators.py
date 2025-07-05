"""
Input validation utilities
Validates URLs, file paths, and other user inputs.
"""

import re
import os
from urllib.parse import urlparse
from typing import Tuple, Optional

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class URLValidator:
    """Validates YouTube URLs"""
    
    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
    ]
    
    PLAYLIST_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*list=([a-zA-Z0-9_-]+)',
    ]
    
    @classmethod
    def is_valid_youtube_url(cls, url: str) -> bool:
        """
        Check if URL is a valid YouTube URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        # Check against all patterns
        for pattern in cls.YOUTUBE_PATTERNS + cls.PLAYLIST_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def is_playlist_url(cls, url: str) -> bool:
        """
        Check if URL is a YouTube playlist URL
        
        Args:
            url: URL to check
            
        Returns:
            True if playlist URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        for pattern in cls.PLAYLIST_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID if found, None otherwise
        """
        if not url or not isinstance(url, str):
            return None
        
        url = url.strip()
        
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.match(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """
        Validate YouTube URL and return result with message
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not url or not isinstance(url, str):
            return False, "Please enter a URL"
        
        url = url.strip()
        
        if not url:
            return False, "Please enter a URL"
        
        if not cls.is_valid_youtube_url(url):
            return False, "Please enter a valid YouTube URL"
        
        if cls.is_playlist_url(url):
            return False, "Playlist URLs are not supported yet"
        
        return True, "Valid YouTube URL"

class PathValidator:
    """Validates file and directory paths"""
    
    @staticmethod
    def is_valid_directory(path: str) -> bool:
        """
        Check if path is a valid directory
        
        Args:
            path: Directory path to validate
            
        Returns:
            True if valid directory, False otherwise
        """
        if not path or not isinstance(path, str):
            return False
        
        path = path.strip()
        
        if not path:
            return False
        
        try:
            # Check if path exists and is a directory
            return os.path.exists(path) and os.path.isdir(path)
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def is_valid_file_path(path: str) -> bool:
        """
        Check if path is a valid file path
        
        Args:
            path: File path to validate
            
        Returns:
            True if valid file path, False otherwise
        """
        if not path or not isinstance(path, str):
            return False
        
        path = path.strip()
        
        if not path:
            return False
        
        try:
            # Check if path exists and is a file
            return os.path.exists(path) and os.path.isfile(path)
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def can_create_directory(path: str) -> bool:
        """
        Check if directory can be created at path
        
        Args:
            path: Directory path to check
            
        Returns:
            True if directory can be created, False otherwise
        """
        if not path or not isinstance(path, str):
            return False
        
        path = path.strip()
        
        if not path:
            return False
        
        try:
            # If directory already exists, check if it's writable
            if os.path.exists(path):
                return os.path.isdir(path) and os.access(path, os.W_OK)
            
            # Check if parent directory exists and is writable
            parent_dir = os.path.dirname(path)
            if parent_dir:
                return os.path.exists(parent_dir) and os.access(parent_dir, os.W_OK)
            
            return True
            
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def validate_output_directory(path: str) -> Tuple[bool, str]:
        """
        Validate output directory path
        
        Args:
            path: Directory path to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not path or not isinstance(path, str):
            return False, "Please enter a directory path"
        
        path = path.strip()
        
        if not path:
            return False, "Please enter a directory path"
        
        # Check if directory exists
        if PathValidator.is_valid_directory(path):
            # Check if writable
            if os.access(path, os.W_OK):
                return True, "Valid output directory"
            else:
                return False, "Directory is not writable"
        
        # Check if we can create the directory
        if PathValidator.can_create_directory(path):
            return True, "Directory will be created"
        
        return False, "Cannot create directory at this path"
    
    @staticmethod
    def validate_cookie_file(path: str) -> Tuple[bool, str]:
        """
        Validate cookie file path
        
        Args:
            path: Cookie file path to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not path or not isinstance(path, str):
            return False, "Please select a cookie file"
        
        path = path.strip()
        
        if not path:
            return False, "Please select a cookie file"
        
        if not PathValidator.is_valid_file_path(path):
            return False, "Cookie file does not exist"
        
        # Check if file has content
        try:
            if os.path.getsize(path) == 0:
                return False, "Cookie file is empty"
        except OSError:
            return False, "Cannot read cookie file"
        
        return True, "Valid cookie file"

class QualityValidator:
    """Validates quality settings"""
    
    VALID_QUALITIES = ["best", "1080p", "720p", "audio"]
    
    @classmethod
    def is_valid_quality(cls, quality: str) -> bool:
        """
        Check if quality setting is valid
        
        Args:
            quality: Quality setting to validate
            
        Returns:
            True if valid, False otherwise
        """
        return quality in cls.VALID_QUALITIES
    
    @classmethod
    def validate_quality(cls, quality: str) -> Tuple[bool, str]:
        """
        Validate quality setting
        
        Args:
            quality: Quality setting to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not quality:
            return False, "Please select a quality"
        
        if not cls.is_valid_quality(quality):
            return False, f"Invalid quality. Must be one of: {', '.join(cls.VALID_QUALITIES)}"
        
        return True, "Valid quality setting"