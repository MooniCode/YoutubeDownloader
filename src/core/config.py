"""
Configuration management for YouTube Downloader
Handles loading, saving, and validation of application settings.
"""

import json
import os
from typing import Dict, Any

class ConfigManager:
    """Manages application configuration settings"""
    
    DEFAULT_CONFIG = {
        'output_path': './downloads',
        'use_cookies': False,
        'cookie_source': 'browser',
        'browser_choice': 'chrome',
        'cookie_file_path': '',
        'last_quality': '1080p',
        'window_geometry': '900x700'
    }
    
    def __init__(self, config_file: str = "downloader_config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            Dictionary containing configuration settings
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    
                # Merge with defaults (in case new settings were added)
                self.config.update(saved_config)
                
                # Validate paths
                self._validate_paths()
                
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            self.config = self.DEFAULT_CONFIG.copy()
        
        return self.config
    
    def save_config(self) -> bool:
        """
        Save current configuration to file
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Value to set
            save: Whether to save immediately
            
        Returns:
            True if set successfully
        """
        self.config[key] = value
        
        if save:
            return self.save_config()
        return True
    
    def update(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """
        Update multiple configuration values
        
        Args:
            updates: Dictionary of key-value pairs to update
            save: Whether to save immediately
            
        Returns:
            True if updated successfully
        """
        self.config.update(updates)
        
        if save:
            return self.save_config()
        return True
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values
        
        Returns:
            True if reset successfully
        """
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save_config()
    
    def _validate_paths(self):
        """Validate file and directory paths in configuration"""
        # Check if output path exists, reset to default if not
        output_path = self.config.get('output_path')
        if output_path and not os.path.exists(output_path):
            self.config['output_path'] = self.DEFAULT_CONFIG['output_path']
        
        # Check if cookie file exists, clear if not
        cookie_file = self.config.get('cookie_file_path')
        if cookie_file and not os.path.exists(cookie_file):
            self.config['cookie_file_path'] = ''
    
    def get_output_directory(self) -> str:
        """
        Get validated output directory, creating if necessary
        
        Returns:
            Path to output directory
        """
        output_path = self.config.get('output_path', self.DEFAULT_CONFIG['output_path'])
        
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            print(f"Error creating output directory: {e}")
            # Fall back to default
            output_path = self.DEFAULT_CONFIG['output_path']
            os.makedirs(output_path, exist_ok=True)
            self.set('output_path', output_path)
        
        return output_path