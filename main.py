#!/usr/bin/env python3
"""
YouTube Downloader - Main Entry Point
Entry point for the YouTube downloader application.
"""

import tkinter as tk
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import YouTubeDownloaderGUI

def main():
    """Main application entry point"""
    try:
        # Create the main tkinter window
        root = tk.Tk()
        
        # Create and start the application
        app = YouTubeDownloaderGUI(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()