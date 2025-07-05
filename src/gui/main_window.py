"""
Main GUI window for YouTube Downloader
Provides the user interface and coordinates between GUI and core functionality.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import webbrowser
import sys
import os

# Import core functionality
from core.config import ConfigManager
from core.downloader import DownloadEngine
from core.cookies import CookieManager
from core.ffmpeg import FFmpegManager

# Import utilities
from utils.validators import URLValidator, PathValidator, QualityValidator
from utils.platform_utils import PlatformUtils

class YouTubeDownloaderGUI:
    """Main GUI application class"""
    
    def __init__(self, root):
        """
        Initialize the GUI application
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("900x700")
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.cookie_manager = CookieManager()
        self.ffmpeg_manager = FFmpegManager()
        self.download_engine = DownloadEngine(self.cookie_manager)
        
        # Set up callbacks
        self.download_engine.set_progress_callback(self.update_progress)
        self.download_engine.set_log_callback(self.log_message)
        self.cookie_manager.set_log_callback(self.log_message)
        
        # GUI variables
        self.setup_variables()
        
        # Load configuration
        self.load_configuration()
        
        # Set application icon
        self.setup_icon()
        
        # Show FFmpeg warning if needed
        if not self.ffmpeg_manager.is_available():
            self.show_ffmpeg_warning()
        
        # Create GUI
        self.create_widgets()
        
        # Additional state
        self.download_complete = False
    
    def setup_variables(self):
        """Initialize tkinter variables"""
        self.output_path = tk.StringVar(value="./downloads")
        self.progress_var = tk.DoubleVar()
        self.progress_text = tk.StringVar(value="Ready")
        self.quality_var = tk.StringVar(value="1080p")
        
        # Cookie variables
        self.use_cookies = tk.BooleanVar(value=False)
        self.cookie_source = tk.StringVar(value="browser")
        self.browser_choice = tk.StringVar(value="chrome")
        self.cookie_file_path = tk.StringVar(value="")
    
    def setup_icon(self):
        """Set up application icon"""
        try:
            icon_path = PlatformUtils.get_resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except (tk.TclError, FileNotFoundError, AttributeError):
            # Icon file not found, continue without icon
            pass
    
    def load_configuration(self):
        """Load configuration from config manager"""
        config = self.config_manager.config
        
        # Load basic settings
        self.output_path.set(config.get('output_path', './downloads'))
        self.quality_var.set(config.get('last_quality', '1080p'))
        
        # Load cookie settings
        self.use_cookies.set(config.get('use_cookies', False))
        self.cookie_source.set(config.get('cookie_source', 'browser'))
        self.browser_choice.set(config.get('browser_choice', 'chrome'))
        self.cookie_file_path.set(config.get('cookie_file_path', ''))
        
        # Configure managers
        self.cookie_manager.configure(
            self.use_cookies.get(),
            self.cookie_source.get(),
            self.browser_choice.get(),
            self.cookie_file_path.get()
        )
        
        # Set window geometry if saved
        geometry = config.get('window_geometry')
        if geometry:
            try:
                self.root.geometry(geometry)
            except tk.TclError:
                pass
    
    def save_configuration(self):
        """Save current configuration"""
        updates = {
            'output_path': self.output_path.get(),
            'last_quality': self.quality_var.get(),
            'use_cookies': self.use_cookies.get(),
            'cookie_source': self.cookie_source.get(),
            'browser_choice': self.browser_choice.get(),
            'cookie_file_path': self.cookie_file_path.get(),
            'window_geometry': self.root.geometry()
        }
        
        self.config_manager.update(updates)
        
        # Update cookie manager
        self.cookie_manager.configure(
            self.use_cookies.get(),
            self.cookie_source.get(),
            self.browser_choice.get(),
            self.cookie_file_path.get()
        )
    
    def show_ffmpeg_warning(self):
        """Show initial FFmpeg warning dialog"""
        result = messagebox.askyesno("FFmpeg Not Found", 
                                   self.ffmpeg_manager.get_warning_message())
        if result:
            self.ffmpeg_manager.open_installation_guide()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        current_row = 0
        
        # URL input section
        current_row = self.create_url_section(main_frame, current_row)
        
        # Output folder section
        current_row = self.create_folder_section(main_frame, current_row)
        
        # Quality selection section
        current_row = self.create_quality_section(main_frame, current_row)
        
        # Cookie settings section
        current_row = self.create_cookie_section(main_frame, current_row)
        
        # Button section
        current_row = self.create_button_section(main_frame, current_row)
        
        # Progress section
        current_row = self.create_progress_section(main_frame, current_row)
        
        # Status section
        current_row = self.create_status_section(main_frame, current_row)
        
        # Footer section
        current_row = self.create_footer_section(main_frame, current_row)
        
        # FFmpeg status
        self.create_ffmpeg_status(main_frame, current_row)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(current_row - 1, weight=1)  # Make status section expandable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def create_url_section(self, parent, start_row):
        """Create URL input section"""
        ttk.Label(parent, text="YouTube URL:", font=("Arial", 12)).grid(
            row=start_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.url_entry = ttk.Entry(parent, width=70, font=("Arial", 10))
        self.url_entry.grid(
            row=start_row + 1, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), pady=(0, 15)
        )
        
        return start_row + 2
    
    def create_folder_section(self, parent, start_row):
        """Create output folder section"""
        ttk.Label(parent, text="Download Folder:", font=("Arial", 12)).grid(
            row=start_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        folder_frame = ttk.Frame(parent)
        folder_frame.grid(
            row=start_row + 1, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), pady=(0, 15)
        )
        
        self.folder_entry = ttk.Entry(
            folder_frame, textvariable=self.output_path, 
            width=50, font=("Arial", 10)
        )
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(
            folder_frame, text="Browse", 
            command=self.browse_folder
        ).grid(row=0, column=1, padx=(10, 0))
        
        folder_frame.columnconfigure(0, weight=1)
        
        return start_row + 2
    
    def create_quality_section(self, parent, start_row):
        """Create quality selection section"""
        ttk.Label(parent, text="Quality:", font=("Arial", 12)).grid(
            row=start_row, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        quality_frame = ttk.Frame(parent)
        quality_frame.grid(
            row=start_row + 1, column=0, columnspan=2, 
            sticky=tk.W, pady=(0, 15)
        )
        
        ttk.Radiobutton(
            quality_frame, text="Best Available", 
            variable=self.quality_var, value="best"
        ).grid(row=0, column=0, padx=(0, 15))
        
        ttk.Radiobutton(
            quality_frame, text="1080p", 
            variable=self.quality_var, value="1080p"
        ).grid(row=0, column=1, padx=(0, 15))
        
        ttk.Radiobutton(
            quality_frame, text="720p", 
            variable=self.quality_var, value="720p"
        ).grid(row=0, column=2, padx=(0, 15))
        
        ttk.Radiobutton(
            quality_frame, text="Audio Only", 
            variable=self.quality_var, value="audio"
        ).grid(row=0, column=3)
        
        return start_row + 2
    
    def create_cookie_section(self, parent, start_row):
        """Create cookie settings section"""
        cookie_frame = ttk.LabelFrame(
            parent, text="Cookie Settings (for age-restricted videos)", 
            padding="10"
        )
        cookie_frame.grid(
            row=start_row, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), pady=(0, 15)
        )
        
        # Use cookies checkbox
        ttk.Checkbutton(
            cookie_frame, text="Use cookies for age-restricted videos",
            variable=self.use_cookies, command=self.toggle_cookie_options
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Cookie source selection
        source_frame = ttk.Frame(cookie_frame)
        source_frame.grid(
            row=1, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), pady=(0, 10)
        )
        
        ttk.Radiobutton(
            source_frame, text="From Browser", 
            variable=self.cookie_source, value="browser",
            command=self.toggle_cookie_options
        ).grid(row=0, column=0, padx=(0, 20))
        
        ttk.Radiobutton(
            source_frame, text="From File", 
            variable=self.cookie_source, value="file",
            command=self.toggle_cookie_options
        ).grid(row=0, column=1)
        
        # Browser selection frame
        self.browser_frame = ttk.Frame(cookie_frame)
        self.browser_frame.grid(
            row=2, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), pady=(0, 10)
        )
        
        ttk.Label(self.browser_frame, text="Browser:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        browser_combo = ttk.Combobox(
            self.browser_frame, textvariable=self.browser_choice,
            values=["chrome", "firefox", "edge", "safari", "opera"],
            state="readonly", width=15
        )
        browser_combo.grid(row=0, column=1, sticky=tk.W)
        
        # Cookie file selection frame
        self.file_frame = ttk.Frame(cookie_frame)
        self.file_frame.grid(
            row=3, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), pady=(0, 10)
        )
        
        ttk.Label(self.file_frame, text="Cookie File:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        self.cookie_file_entry = ttk.Entry(
            self.file_frame, textvariable=self.cookie_file_path, width=40
        )
        self.cookie_file_entry.grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10)
        )
        
        ttk.Button(
            self.file_frame, text="Browse", 
            command=self.browse_cookie_file
        ).grid(row=0, column=2)
        
        self.file_frame.columnconfigure(1, weight=1)
        
        # Help text
        help_text = (
            "Cookies help download age-restricted videos. Choose 'From Browser' to automatically "
            "extract cookies from your browser, or 'From File' to use a cookies.txt file."
        )
        help_label = ttk.Label(
            cookie_frame, text=help_text, 
            font=("Arial", 8), foreground="gray"
        )
        help_label.grid(
            row=4, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), pady=(10, 0)
        )
        
        # Initially hide cookie options
        self.toggle_cookie_options()
        
        return start_row + 1
    
    def create_button_section(self, parent, start_row):
        """Create button section"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=start_row, column=0, columnspan=2, pady=20)
        
        # Download button
        self.download_btn = ttk.Button(
            button_frame, text="Download", 
            command=self.start_download, style="Accent.TButton"
        )
        self.download_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Export cookies button
        self.export_cookies_btn = ttk.Button(
            button_frame, text="Export Browser Cookies", 
            command=self.export_cookies
        )
        self.export_cookies_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Open folder button (initially hidden)
        self.open_folder_btn = ttk.Button(
            button_frame, text="Open Folder", 
            command=self.open_destination_folder
        )
        self.open_folder_btn.grid(row=0, column=2, padx=(0, 10))
        self.open_folder_btn.grid_remove()  # Hide initially
        
        # Convert another button (initially hidden)
        self.convert_another_btn = ttk.Button(
            button_frame, text="Convert Another", 
            command=self.convert_another
        )
        self.convert_another_btn.grid(row=0, column=3)
        self.convert_another_btn.grid_remove()  # Hide initially
        
        return start_row + 1
    
    def create_progress_section(self, parent, start_row):
        """Create progress section"""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(
            row=start_row, column=0, columnspan=2, 
            sticky=(tk.W, tk.E), pady=(0, 10)
        )
        
        # Progress label
        self.progress_label = ttk.Label(
            progress_frame, textvariable=self.progress_text, 
            font=("Arial", 10)
        )
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        progress_frame.columnconfigure(0, weight=1)
        
        return start_row + 1
    
    def create_status_section(self, parent, start_row):
        """Create status text section"""
        self.status_text = tk.Text(
            parent, height=8, width=70, font=("Consolas", 9)
        )
        self.status_text.grid(
            row=start_row, column=0, columnspan=2, 
            sticky=(tk.W, tk.E, tk.N, tk.S)
        )
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(
            parent, orient="vertical", command=self.status_text.yview
        )
        scrollbar.grid(row=start_row, column=2, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        return start_row + 1
    
    def create_footer_section(self, parent, start_row):
        """Create footer section"""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(
            row=start_row, column=0, columnspan=2, pady=(15, 0)
        )
        
        # Made by text
        made_by_label = ttk.Label(
            footer_frame, text="Made by Mooni", font=("Arial", 9)
        )
        made_by_label.grid(row=0, column=0, padx=(0, 10))
        
        # YouTube link
        youtube_link = ttk.Label(
            footer_frame, text="Visit my YouTube channel",
            font=("Arial", 9), foreground="blue", cursor="hand2"
        )
        youtube_link.grid(row=0, column=1)
        youtube_link.bind("<Button-1>", self.open_youtube)
        
        return start_row + 1
    
    def create_ffmpeg_status(self, parent, start_row):
        """Create FFmpeg status indicator"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(
            row=start_row, column=0, columnspan=2, 
            pady=(10, 0), sticky=tk.W
        )
        
        # FFmpeg status
        status_text = self.ffmpeg_manager.get_status_text()
        status_label = ttk.Label(
            status_frame, text=status_text, font=("Arial", 9)
        )
        status_label.grid(row=0, column=0, padx=(0, 10))
        
        if not self.ffmpeg_manager.is_available():
            install_link = ttk.Label(
                status_frame, text="(Click here for installation guide)",
                font=("Arial", 9), foreground="blue", cursor="hand2"
            )
            install_link.grid(row=0, column=1)
            install_link.bind("<Button-1>", self.show_ffmpeg_help)
    
    # Event handlers and utility methods
    
    def toggle_cookie_options(self):
        """Show/hide cookie options based on selection"""
        if self.use_cookies.get():
            self.browser_frame.grid()
            self.file_frame.grid()
            if self.cookie_source.get() == "browser":
                self.browser_frame.grid()
                self.file_frame.grid_remove()
            else:
                self.browser_frame.grid_remove()
                self.file_frame.grid()
        else:
            self.browser_frame.grid_remove()
            self.file_frame.grid_remove()
    
    def browse_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)
            self.save_configuration()
    
    def browse_cookie_file(self):
        """Browse for cookie file"""
        file_path = filedialog.askopenfilename(
            title="Select Cookie File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.cookie_file_path.set(file_path)
            self.save_configuration()
    
    def export_cookies(self):
        """Export cookies from browser to a file"""
        if not self.use_cookies.get():
            messagebox.showinfo(
                "Info", 
                "Please enable 'Use cookies' first and select a browser."
            )
            return
        
        # Ask where to save the cookie file
        save_path = filedialog.asksaveasfilename(
            title="Save Cookie File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not save_path:
            return
        
        def export_thread():
            try:
                success = self.cookie_manager.export_cookies_from_browser(
                    save_path, self.update_progress
                )
                
                if success:
                    # Update GUI variables
                    self.cookie_file_path.set(save_path)
                    self.cookie_source.set("file")
                    self.toggle_cookie_options()
                    self.save_configuration()
                    
                    messagebox.showinfo(
                        "Success", 
                        f"Cookies exported successfully to:\n{save_path}"
                    )
                else:
                    error_msg = self.cookie_manager.get_export_error_help("")
                    messagebox.showerror("Error", error_msg)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export cookies: {str(e)}")
        
        threading.Thread(target=export_thread, daemon=True).start()
    
    def open_destination_folder(self):
        """Open the destination folder"""
        folder_path = self.output_path.get()
        
        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "The destination folder no longer exists.")
            return
        
        if not PlatformUtils.open_folder(folder_path):
            messagebox.showerror("Error", "Could not open folder.")
    
    def open_youtube(self, event):
        """Open YouTube channel in browser"""
        webbrowser.open("https://www.youtube.com/@Mooni_Dev")
    
    def show_ffmpeg_help(self, event=None):
        """Show FFmpeg installation guide"""
        self.ffmpeg_manager.open_installation_guide()
    
    def log_message(self, message):
        """Log message to status text"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, percentage, status_text):
        """Update progress bar and status text"""
        def update():
            self.progress_var.set(percentage)
            self.progress_text.set(status_text)
        
        self.root.after(0, update)
    
    def show_action_buttons(self):
        """Show action buttons after successful download"""
        def show():
            self.open_folder_btn.grid()
            self.convert_another_btn.grid()
        
        self.root.after(0, show)
    
    def hide_action_buttons(self):
        """Hide action buttons when starting new download"""
        self.open_folder_btn.grid_remove()
        self.convert_another_btn.grid_remove()
    
    def convert_another(self):
        """Clear interface for another conversion"""
        # Clear the URL entry
        self.url_entry.delete(0, tk.END)
        
        # Clear the status text
        self.status_text.delete(1.0, tk.END)
        
        # Reset progress
        self.progress_var.set(0)
        self.progress_text.set("Ready")
        
        # Hide the action buttons
        self.hide_action_buttons()
        
        # Reset download complete flag
        self.download_complete = False
        
        # Focus on the URL entry
        self.url_entry.focus_set()
        
        # Log message
        self.log_message("Ready for new download. Enter a YouTube URL above.")
    
    def validate_inputs(self):
        """Validate all user inputs"""
        # Validate URL
        url = self.url_entry.get().strip()
        is_valid, message = URLValidator.validate_url(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", message)
            return False
        
        # Validate output path
        output_path = self.output_path.get().strip()
        is_valid, message = PathValidator.validate_output_directory(output_path)
        if not is_valid:
            messagebox.showerror("Invalid Output Folder", message)
            return False
        
        # Validate quality
        quality = self.quality_var.get()
        is_valid, message = QualityValidator.validate_quality(quality)
        if not is_valid:
            messagebox.showerror("Invalid Quality", message)
            return False
        
        # Validate cookie file if using file source
        if self.use_cookies.get() and self.cookie_source.get() == "file":
            cookie_file = self.cookie_file_path.get()
            is_valid, message = PathValidator.validate_cookie_file(cookie_file)
            if not is_valid:
                messagebox.showerror("Invalid Cookie File", message)
                return False
        
        return True
    
    def check_ffmpeg_requirements(self):
        """Check FFmpeg requirements for selected quality"""
        quality = self.quality_var.get()
        
        if not self.ffmpeg_manager.is_available() and self.ffmpeg_manager.requires_ffmpeg(quality):
            result = messagebox.askyesnocancel(
                "FFmpeg Required",
                self.ffmpeg_manager.get_quality_warning_message(quality),
                icon='warning'
            )
            
            if result is True:  # Yes - show instructions
                self.show_ffmpeg_help()
                return False
            elif result is None:  # Cancel
                return False
            # If False (No), continue with download attempt
        
        return True
    
    def start_download(self):
        """Start the download process"""
        # Validate inputs
        if not self.validate_inputs():
            return
        
        # Check FFmpeg requirements
        if not self.check_ffmpeg_requirements():
            return
        
        # Get values
        url = self.url_entry.get().strip()
        output_path = self.output_path.get().strip()
        quality = self.quality_var.get()
        
        # Reset UI state
        self.progress_var.set(0)
        self.progress_text.set("Preparing...")
        self.download_btn.config(state="disabled")
        self.export_cookies_btn.config(state="disabled")
        self.status_text.delete(1.0, tk.END)
        self.download_complete = False
        
        # Hide action buttons
        self.hide_action_buttons()
        
        # Save configuration
        self.save_configuration()
        
        # Start download in separate thread
        def download_thread():
            try:
                success = self.download_engine.download(url, output_path, quality)
                
                if success:
                    self.download_complete = True
                    self.show_action_buttons()
                
            finally:
                # Re-enable buttons
                self.root.after(0, lambda: [
                    self.download_btn.config(state="normal"),
                    self.export_cookies_btn.config(state="normal")
                ])
        
        threading.Thread(target=download_thread, daemon=True).start()