"""
gui_advanced.py
Advanced GUI for the AI Pair Programming Assistant with unified setup and control center.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import time
import os
import json
import glob
import subprocess
import sys
from datetime import datetime

from config import app_state
from app_logic import (
    check_autohotkey, check_ahk_running, start_ahk_script, stop_ahk_script,
    git_status, git_add_all, git_commit, monitor_ahk_log, git_pull, git_push,
    get_current_branch, list_branches, create_branch, switch_branch,
    parse_implementation_plan, run_python_test_file, check_and_install_dependencies,
    verify_dependencies_subprocess
)

class AdvancedGui:
    def __init__(self, parent: tk.Tk):
        self.root = parent
        self.root.title("🤖 AI Pair Programming Assistant - Control Center")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Session management with per-session logging
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_file = f"session_log_{session_timestamp}.txt"
        self.session_log_lock = threading.Lock()
        
        # Initialize session log
        with open(self.session_log_file, "w", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] New session started\n")
        
        # Initialize state variables
        self.setup_completed = self.load_setup_state()
        self.afk_mode_active = tk.BooleanVar()
        self.dark_mode_var = tk.BooleanVar()
        self.autonomous_mode_var = tk.BooleanVar()
        
        # Threading and monitoring
        self.context_watcher_stop = threading.Event()
        self.context_watcher_thread = None
        self.ahk_log_stop_event = threading.Event()
        self.health_monitor_stop = threading.Event()
        
        # UI state
        self.afk_status_banner = None
        self.context_regen_banner = None
        self.health_alert_banner = None
        self.last_health_status = {}
        
        # Load settings and configure styles
        self.dark_mode_var.set(self.load_dark_mode_setting())
        self._configure_styles()
        if self.dark_mode_var.get():
            self.set_dark_mode()
        
        # Create main interface
        self.create_widgets()
        
        # Optional features
        try:
            self.setup_tray_icon()
        except Exception:
            pass
        
        # Start file monitoring
        self.start_context_watcher()
        
        self.log_session_event("Application initialized successfully")
        print("Advanced GUI Initialized.")

    def create_widgets(self):
        """Create the main notebook interface."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create tabs based on setup state
        if not self.setup_completed:
            self.create_setup_tab()
        
        # Always create main tabs
        self.create_automation_tab()
        self.create_context_tab()
        self.create_git_tab()
        self.create_session_tab()
        self.create_goal_tab()
        self.create_tdd_tab()
        self.create_settings_tab()
        self.create_session_log_tab()

    def create_setup_tab(self):
        """Create a clean, working setup tab with automatic checks."""
        self.setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_tab, text="Setup")
        
        main_frame = ttk.Frame(self.setup_tab, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title = ttk.Label(main_frame, text="Project Setup", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20))
        
        # Progress bar
        self.setup_progress = ttk.Progressbar(main_frame, length=400, mode="determinate")
        self.setup_progress.pack(pady=10)
        
        # Status label
        self.setup_status = ttk.Label(main_frame, text="Initializing setup...", font=("Arial", 11))
        self.setup_status.pack(pady=5)
        
        # Directory section
        dir_frame = ttk.LabelFrame(main_frame, text="Project Directory", padding=10)
        dir_frame.pack(fill='x', pady=10)
        
        self.dir_status = ttk.Label(dir_frame, text="Checking directory...", font=("Arial", 10))
        self.dir_status.pack(anchor='w')
        
        # Dependencies section
        dep_frame = ttk.LabelFrame(main_frame, text="Dependencies", padding=10)
        dep_frame.pack(fill='x', pady=10)
        
        self.dep_status = ttk.Label(dep_frame, text="Checking dependencies...", font=("Arial", 10))
        self.dep_status.pack(anchor='w')
        
        self.dep_install_btn = ttk.Button(dep_frame, text="Install Dependencies", 
                                         command=self.install_dependencies)
        # Don't pack initially
        
        # AutoHotkey section
        ahk_frame = ttk.LabelFrame(main_frame, text="AutoHotkey", padding=10)
        ahk_frame.pack(fill='x', pady=10)
        
        self.ahk_status = ttk.Label(ahk_frame, text="Checking AutoHotkey...", font=("Arial", 10))
        self.ahk_status.pack(anchor='w')
        
        self.ahk_install_btn = ttk.Button(ahk_frame, text="Get AutoHotkey", 
                                         command=self.show_ahk_install_guide)
        # Don't pack initially
        
        # Continue button
        self.continue_btn = ttk.Button(main_frame, text="Continue to App", 
                                      command=self.complete_setup, state='disabled')
        self.continue_btn.pack(pady=20)
        
        # Start automatic setup checks
        self.root.after(500, self.run_setup_checks)

    def run_setup_checks(self):
        """Run all setup checks automatically."""
        self.setup_progress['value'] = 10
        self.setup_status.config(text="Running automatic checks...")
        
        # Start background checks
        threading.Thread(target=self._check_directory, daemon=True).start()
        threading.Thread(target=self._check_dependencies, daemon=True).start()
        threading.Thread(target=self._check_autohotkey, daemon=True).start()

    def _check_directory(self):
        """Check project directory in background."""
        try:
            if not app_state.working_dir:
                app_state.set_working_dir(os.getcwd())
            
            if os.path.isdir(app_state.working_dir):
                dir_name = os.path.basename(app_state.working_dir)
                self.root.after(0, lambda: self.dir_status.config(
                    text=f"✅ Directory: {dir_name}"))
                self.root.after(0, lambda: self._update_setup_progress(25))
            else:
                self.root.after(0, lambda: self.dir_status.config(
                    text="❌ Invalid directory"))
        except Exception as e:
            self.root.after(0, lambda: self.dir_status.config(
                text=f"❌ Directory error: {str(e)[:30]}"))

    def _check_dependencies(self):
        """Check dependencies in background."""
        try:
            success, missing = verify_dependencies_subprocess()
            
            if success:
                self.root.after(0, lambda: self.dep_status.config(
                    text="✅ All dependencies installed"))
                self.root.after(0, lambda: self._update_setup_progress(50))
            else:
                self.root.after(0, lambda: self.dep_status.config(
                    text=f"❌ Missing: {', '.join(missing[:3])}"))
                self.root.after(0, lambda: self.dep_install_btn.pack(pady=5))
        except Exception as e:
            self.root.after(0, lambda: self.dep_status.config(
                text=f"❌ Dependency check failed: {str(e)[:30]}"))
            self.root.after(0, lambda: self.dep_install_btn.pack(pady=5))

    def _check_autohotkey(self):
        """Check AutoHotkey in background."""
        try:
            if check_autohotkey():
                self.root.after(0, lambda: self.ahk_status.config(
                    text="✅ AutoHotkey v2 found"))
                self.root.after(0, lambda: self._update_setup_progress(75))
            else:
                self.root.after(0, lambda: self.ahk_status.config(
                    text="❌ AutoHotkey not found"))
                self.root.after(0, lambda: self.ahk_install_btn.pack(pady=5))
        except Exception as e:
            self.root.after(0, lambda: self.ahk_status.config(
                text=f"❌ AutoHotkey check failed: {str(e)[:30]}"))
            self.root.after(0, lambda: self.ahk_install_btn.pack(pady=5))

    def _update_setup_progress(self, value):
        """Update setup progress and check if complete."""
        self.setup_progress['value'] = max(self.setup_progress['value'], value)
        
        # Check if all checks passed
        dir_ok = "✅" in self.dir_status.cget("text")
        dep_ok = "✅" in self.dep_status.cget("text")
        ahk_ok = "✅" in self.ahk_status.cget("text")
        
        if dir_ok and dep_ok and ahk_ok:
            self.setup_progress['value'] = 100
            self.setup_status.config(text="✅ All checks passed! Ready to continue.")
            self.continue_btn.config(state='normal')

    def install_dependencies(self):
        """Install missing dependencies."""
        self.dep_status.config(text="Installing dependencies...")
        self.dep_install_btn.config(state='disabled')
        
        def install():
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    'pyautogui', 'Pillow', 'gitingest', 'watchdog', 'plyer', 'pystray'
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.dep_status.config(
                        text="✅ Dependencies installed successfully"))
                    self.root.after(0, lambda: self.dep_install_btn.pack_forget())
                    self.root.after(0, lambda: self._update_setup_progress(50))
                else:
                    self.root.after(0, lambda: self.dep_status.config(
                        text="❌ Installation failed"))
                    self.root.after(0, lambda: self.dep_install_btn.config(state='normal'))
            except Exception as e:
                self.root.after(0, lambda: self.dep_status.config(
                    text=f"❌ Installation error: {str(e)[:30]}"))
                self.root.after(0, lambda: self.dep_install_btn.config(state='normal'))
        
        threading.Thread(target=install, daemon=True).start()

    def show_ahk_install_guide(self):
        """Show AutoHotkey installation guide."""
        guide = tk.Toplevel(self.root)
        guide.title("AutoHotkey Installation")
        guide.geometry("400x300")
        guide.transient(self.root)
        guide.grab_set()
        
        frame = ttk.Frame(guide, padding=20)
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text="AutoHotkey Installation", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        instructions = """AutoHotkey is required for automation features.

1. Download AutoHotkey v2 from the official website
2. Run the installer as Administrator
3. Complete the installation
4. Click "Retry Detection" below"""
        
        ttk.Label(frame, text=instructions, justify='left').pack(pady=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        def open_website():
            import webbrowser
            webbrowser.open("https://www.autohotkey.com/download/")
        
        def retry():
            guide.destroy()
            threading.Thread(target=self._check_autohotkey, daemon=True).start()
        
        ttk.Button(btn_frame, text="Open Website", command=open_website).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Retry Detection", command=retry).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=guide.destroy).pack(side='left', padx=5)

    def complete_setup(self):
        """Complete setup and switch to main app."""
        try:
            # Save setup state
            self.save_setup_state(True)
            self.setup_completed = True
            
            # Remove setup tab
            for i in range(self.notebook.index('end')):
                if self.notebook.tab(i, option='text') == 'Setup':
                    self.notebook.forget(i)
                    break
            
            # Switch to first tab (Automation Control)
            self.notebook.select(0)
            
            # Show success notification
            self.show_notification("🎉 Setup Complete!", "Ready for AI pair programming!")
            self.log_session_event("Setup completed successfully")
            
        except Exception as e:
            messagebox.showerror("Setup Error", f"Error completing setup: {e}")

    def save_setup_state(self, complete: bool):
        """Save setup completion state."""
        try:
            state_file = os.path.join(os.getcwd(), 'setup_state.json')
            with open(state_file, 'w') as f:
                json.dump({"setup_complete": complete}, f)
        except Exception as e:
            print(f"Error saving setup state: {e}")

    def load_setup_state(self) -> bool:
        """Load setup completion state."""
        try:
            state_file = os.path.join(os.getcwd(), 'setup_state.json')
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    return data.get("setup_complete", False)
        except Exception:
            pass
        return False