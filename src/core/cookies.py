"""
Cookie management for handling age-restricted videos
Manages browser cookies and cookie files for YouTube authentication.
"""

import os
import time
import yt_dlp
from typing import Dict, Any, Optional, Callable

class CookieManager:
    """Manages cookies for YouTube authentication"""
    
    SUPPORTED_BROWSERS = ["chrome", "firefox", "edge", "safari", "opera"]
    
    def __init__(self):
        """Initialize cookie manager"""
        self.use_cookies = False
        self.cookie_source = "browser"  # "browser" or "file"
        self.browser_choice = "chrome"
        self.cookie_file_path = ""
        self.log_callback: Optional[Callable] = None
    
    def set_log_callback(self, callback: Callable):
        """Set callback for log messages"""
        self.log_callback = callback
    
    def _log(self, message: str):
        """Log a message"""
        if self.log_callback:
            self.log_callback(message)
    
    def configure(self, use_cookies: bool, cookie_source: str = "browser", 
                  browser_choice: str = "chrome", cookie_file_path: str = ""):
        """
        Configure cookie settings
        
        Args:
            use_cookies: Whether to use cookies
            cookie_source: "browser" or "file"
            browser_choice: Browser to extract cookies from
            cookie_file_path: Path to cookie file
        """
        self.use_cookies = use_cookies
        self.cookie_source = cookie_source
        self.browser_choice = browser_choice
        self.cookie_file_path = cookie_file_path
    
    def get_cookie_options(self) -> Dict[str, Any]:
        """
        Get cookie-related options for yt-dlp
        
        Returns:
            Dictionary of yt-dlp cookie options
        """
        cookie_options = {}
        
        if self.use_cookies:
            if self.cookie_source == "browser":
                browser = self.browser_choice
                cookie_options['cookiesfrombrowser'] = (browser,)
                self._log(f"Using cookies from {browser} browser")
            elif self.cookie_source == "file":
                cookie_file = self.cookie_file_path
                if cookie_file and os.path.exists(cookie_file):
                    cookie_options['cookiefile'] = cookie_file
                    self._log(f"Using cookies from file: {cookie_file}")
                else:
                    self._log("Warning: Cookie file not found or not specified")
        
        return cookie_options
    
    def validate_cookie_file(self) -> bool:
        """
        Validate that the cookie file exists and is readable
        
        Returns:
            True if cookie file is valid, False otherwise
        """
        if not self.use_cookies or self.cookie_source != "file":
            return True
        
        if not self.cookie_file_path:
            return False
        
        return os.path.exists(self.cookie_file_path) and os.path.getsize(self.cookie_file_path) > 0
    
    def export_cookies_from_browser(self, output_path: str, 
                                   progress_callback: Optional[Callable] = None) -> bool:
        """
        Export cookies from browser to a file
        
        Args:
            output_path: Path to save cookie file
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            browser = self.browser_choice
            
            if progress_callback:
                progress_callback(0, f"Extracting cookies from {browser}...")
            self._log(f"Exporting cookies from {browser}...")
            
            # Create yt-dlp options for cookie extraction
            ydl_opts = {
                'cookiefile': output_path,  # Output file for cookies
                'extract_flat': True,
                'skip_download': True,
                'quiet': False,
                'no_warnings': False,
            }
            
            # Add browser-specific cookie extraction
            if browser in self.SUPPORTED_BROWSERS:
                ydl_opts['cookiesfrombrowser'] = (browser,)
            else:
                raise ValueError(f"Unsupported browser: {browser}")
            
            # Use a real YouTube URL to trigger cookie extraction
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # This will extract info and save cookies to the file
                    ydl.extract_info(test_url, download=False)
                except Exception as extract_error:
                    self._log(f"Extraction error: {str(extract_error)}")
                    raise extract_error
            
            # Give yt-dlp a moment to finish writing the cookie file
            time.sleep(0.5)
            
            # Check if the cookie file was actually created and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                if progress_callback:
                    progress_callback(100, "Cookies exported successfully!")
                self._log(f"Cookies exported to: {output_path}")
                self._log(f"Cookie file size: {os.path.getsize(output_path)} bytes")
                
                # Update configuration to use the exported file
                self.cookie_file_path = output_path
                self.cookie_source = "file"
                
                return True
            else:
                raise Exception("Cookie file was not created or is empty")
                
        except Exception as e:
            if progress_callback:
                progress_callback(0, "Cookie export failed")
            
            error_msg = str(e)
            self._log(f"Error exporting cookies: {error_msg}")
            
            return False
    
    def get_export_error_help(self, error_msg: str) -> str:
        """
        Get helpful error message for cookie export failures
        
        Args:
            error_msg: Original error message
            
        Returns:
            Helpful error message with suggestions
        """
        browser = self.browser_choice
        
        if "browser" in error_msg.lower():
            return (f"Failed to export cookies from {browser}:\n\n"
                   f"Common solutions:\n"
                   f"1. Make sure {browser} is installed\n"
                   f"2. Make sure you're logged into YouTube in {browser}\n"
                   f"3. Close {browser} completely and try again\n"
                   f"4. Try a different browser\n\n"
                   f"Error details: {error_msg}")
        else:
            return f"Failed to export cookies:\n{error_msg}"
    
    def is_browser_supported(self, browser: str) -> bool:
        """
        Check if browser is supported for cookie extraction
        
        Args:
            browser: Browser name
            
        Returns:
            True if supported, False otherwise
        """
        return browser.lower() in self.SUPPORTED_BROWSERS