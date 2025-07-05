"""
Cross-platform utility functions
Handles platform-specific operations like opening files and folders.
"""

import os
import sys
import subprocess
import platform
from typing import Optional

class PlatformUtils:
    """Cross-platform utility functions"""
    
    @staticmethod
    def get_platform() -> str:
        """
        Get current platform name
        
        Returns:
            Platform name ('windows', 'macos', 'linux', 'unknown')
        """
        system = platform.system().lower()
        
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        elif system == "linux":
            return "linux"
        else:
            return "unknown"
    
    @staticmethod
    def open_folder(folder_path: str) -> bool:
        """
        Open folder in system file manager
        
        Args:
            folder_path: Path to folder to open
            
        Returns:
            True if opened successfully, False otherwise
        """
        if not os.path.exists(folder_path):
            return False
        
        try:
            system = PlatformUtils.get_platform()
            
            if system == "windows":
                os.startfile(folder_path)
            elif system == "macos":
                subprocess.run(["open", folder_path], check=True)
            elif system == "linux":
                subprocess.run(["xdg-open", folder_path], check=True)
            else:
                # Try xdg-open as fallback for other Unix-like systems
                subprocess.run(["xdg-open", folder_path], check=True)
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def open_file(file_path: str) -> bool:
        """
        Open file with default application
        
        Args:
            file_path: Path to file to open
            
        Returns:
            True if opened successfully, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            system = PlatformUtils.get_platform()
            
            if system == "windows":
                os.startfile(file_path)
            elif system == "macos":
                subprocess.run(["open", file_path], check=True)
            elif system == "linux":
                subprocess.run(["xdg-open", file_path], check=True)
            else:
                subprocess.run(["xdg-open", file_path], check=True)
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def get_default_download_folder() -> str:
        """
        Get default download folder for current platform
        
        Returns:
            Path to default download folder
        """
        system = PlatformUtils.get_platform()
        
        if system == "windows":
            # Try to get Downloads folder from user profile
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(downloads):
                return downloads
        elif system == "macos":
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(downloads):
                return downloads
        elif system == "linux":
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(downloads):
                return downloads
        
        # Fallback to current directory
        return "./downloads"
    
    @staticmethod
    def get_resource_path(relative_path: str) -> str:
        """
        Get absolute path to resource, works for PyInstaller bundles
        
        Args:
            relative_path: Relative path to resource
            
        Returns:
            Absolute path to resource
        """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except AttributeError:
            # Running in normal Python environment
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    @staticmethod
    def is_frozen() -> bool:
        """
        Check if running as PyInstaller executable
        
        Returns:
            True if running as executable, False if running as script
        """
        return getattr(sys, 'frozen', False)
    
    @staticmethod
    def get_app_data_folder() -> str:
        """
        Get application data folder for current platform
        
        Returns:
            Path to application data folder
        """
        system = PlatformUtils.get_platform()
        app_name = "YouTubeDownloader"
        
        if system == "windows":
            appdata = os.environ.get("APPDATA")
            if appdata:
                return os.path.join(appdata, app_name)
        elif system == "macos":
            home = os.path.expanduser("~")
            return os.path.join(home, "Library", "Application Support", app_name)
        elif system == "linux":
            home = os.path.expanduser("~")
            # Try XDG_CONFIG_HOME first, fallback to ~/.config
            config_home = os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config"))
            return os.path.join(config_home, app_name)
        
        # Fallback to current directory
        return "."
    
    @staticmethod
    def ensure_app_data_folder() -> str:
        """
        Ensure application data folder exists and return path
        
        Returns:
            Path to application data folder
        """
        folder = PlatformUtils.get_app_data_folder()
        
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError:
            # Fallback to current directory if we can't create app data folder
            folder = "."
        
        return folder
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Get safe filename by removing/replacing invalid characters
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename for current platform
        """
        # Characters that are invalid in Windows filenames
        invalid_chars = '<>:"/\\|?*'
        
        # Replace invalid characters with underscore
        safe_name = filename
        for char in invalid_chars:
            safe_name = safe_name.replace(char, "_")
        
        # Remove leading/trailing dots and spaces
        safe_name = safe_name.strip(". ")
        
        # Ensure filename is not empty
        if not safe_name:
            safe_name = "download"
        
        # Truncate if too long (Windows has 255 character limit)
        max_length = 200  # Leave some room for extensions
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length]
        
        return safe_name
    
    @staticmethod
    def get_terminal_command() -> Optional[str]:
        """
        Get command to open terminal on current platform
        
        Returns:
            Terminal command if available, None otherwise
        """
        system = PlatformUtils.get_platform()
        
        if system == "windows":
            return "cmd"
        elif system == "macos":
            return "Terminal"
        elif system == "linux":
            # Try common terminal applications
            terminals = ["gnome-terminal", "konsole", "xterm", "x-terminal-emulator"]
            for terminal in terminals:
                try:
                    subprocess.run(["which", terminal], 
                                 capture_output=True, check=True)
                    return terminal
                except subprocess.CalledProcessError:
                    continue
        
        return None