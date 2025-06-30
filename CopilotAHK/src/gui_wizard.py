"""
gui_wizard.py
The setup wizard for the AI Pair Programming Assistant.
Guides the user through project setup, dependency checks, and initial configuration.
"""

import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
from typing import Optional

from config import app_state
from app_logic import check_and_install_dependencies, check_autohotkey, run_gitingest
from gui_advanced import AdvancedGui

class SetupWizard:
    """
    A guided setup wizard for a streamlined user experience.
    """
    
    def __init__(self, parent: tk.Tk):
        print("[DEBUG] SetupWizard __init__ starting...")
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("🤖 AI Pair Programming Assistant - Quick Setup")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        self.root.configure(bg="#f5f5f5")
        
        self.root.minsize(900, 800)
        
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"900x800+{x}+{y}")
        
        self.current_step = 1
        self.total_steps = 5
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_interface()
        self.show_welcome_step()
        print("[DEBUG] SetupWizard __init__ complete.")

    def on_close(self):
        print("[DEBUG] Wizard window closed. Exiting application.")
        self.parent.destroy()

    def create_interface(self):
        """Creates the main wizard interface, including header, progress bar, and content area."""
        # Header
        header_frame = ttk.Frame(self.root, style='Header.TFrame', height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        ttk.Label(
            header_frame,
            text="🤖 AI Pair Programming Assistant",
            style='Header.TLabel'
        ).pack(side="left", padx=20, pady=10)

        # Advanced Mode button in header
        ttk.Button(
            header_frame,
            text="⚙️ Skip to Advanced Mode",
            command=self.open_advanced_mode,
            style='Header.TButton'
        ).pack(side="right", padx=20, pady=10)
        
        # Main content area
        self.content_frame = ttk.Frame(self.root, style='Content.TFrame')
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Navigation buttons frame
        self.nav_frame = ttk.Frame(self.root, style='Nav.TFrame', height=70)
        self.nav_frame.pack(side="bottom", fill="x")
        self.nav_frame.pack_propagate(False)

        self._configure_styles()

    def _configure_styles(self):
        """Configures the ttk styles for the wizard."""
        style = ttk.Style(self.root)
        style.theme_use('clam')

        # Frames
        style.configure('Header.TFrame', background='#1976D2')
        style.configure('Content.TFrame', background='white', relief='raised', borderwidth=1)
        style.configure('Nav.TFrame', background='white', relief='raised', borderwidth=1)
        style.configure('Card.TFrame', background='#f8f9fa', relief='solid', borderwidth=1)

        # Labels
        style.configure('Header.TLabel', background='#1976D2', foreground='white', font=("Arial", 18, "bold"))
        style.configure('Title.TLabel', background='white', foreground='#1976D2', font=("Arial", 18, "bold"))
        style.configure('H2.TLabel', background='#f8f9fa', foreground='#1976D2', font=("Arial", 15, "bold"))
        style.configure('Dir.TLabel', background='#ffffff', foreground='#666', relief='solid', borderwidth=1, padding=(15, 12), anchor='center')
        style.configure('Success.Dir.TLabel', background='#E8F5E8', foreground='#2E7D32', font=("Arial", 10, "bold"), padding=10)

        # Buttons
        style.configure('TButton', font=("Arial", 10), padding=(20, 10))
        style.configure('Primary.TButton', background='#4CAF50', foreground='white', font=("Arial", 12, "bold"))
        style.map('Primary.TButton', background=[('active', '#45a049')])
        style.configure('Nav.TButton', font=("Arial", 12, "bold"), padding=(30, 15))
        style.configure('Header.TButton', font=("Arial", 10, "bold"), background='#FF6D00', foreground='white')
        style.map('Header.TButton', background=[('active', '#FF8A00')])

    def clear_content(self):
        """Clears the content frame of all widgets."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def update_nav_buttons(self, step: int):
        """Creates and places navigation buttons appropriate for the current step."""
        for widget in self.nav_frame.winfo_children():
            widget.destroy()
        
        # Back button is common to most steps
        if step > 1:
            ttk.Button(self.nav_frame, text="← Back", command=self.get_previous_step_func(step)).pack(side="left", padx=20, pady=15)

        if step == 1:
            # No back button on first step
            self.next_btn = ttk.Button(self.nav_frame, text="Select Directory First →", command=self.show_dependency_step, style='Nav.TButton', state="disabled")
            self.next_btn.pack(side="right", padx=20, pady=15)
        elif step == 2:
             ttk.Button(self.nav_frame, text="⏭️ Skip to Automation", command=self.show_completion_step).pack(side="left", padx=(150, 20), pady=15)
             self.next_btn = ttk.Button(self.nav_frame, text="Continue →", command=self.show_analysis_step, style='Nav.TButton', state="disabled")
             self.next_btn.pack(side="right", padx=20, pady=15)
        elif step == 3:
            ttk.Button(self.nav_frame, text="⏭️ Skip Analysis", command=self.show_completion_step).pack(side="left", padx=(150, 20), pady=15)
            self.next_btn = ttk.Button(self.nav_frame, text="Continue →", command=self.show_completion_step, style='Nav.TButton', state="disabled")
            self.next_btn.pack(side="right", padx=20, pady=15)
        elif step == 4:
            ttk.Button(self.nav_frame, text="🔄 Restart Setup", command=self.restart_wizard).pack(side="left", padx=(150, 20), pady=15)
            self.next_btn = ttk.Button(self.nav_frame, text="🚀 Launch Control Center", command=self.show_launch_step, style='Primary.TButton')
            self.next_btn.pack(side="right", padx=20, pady=15)
        elif step == 5:
            ttk.Button(self.nav_frame, text="🔄 Restart Setup", command=self.restart_wizard).pack(side="left", padx=(150, 20), pady=15)
            # No "next" button, launch is in main content

    def get_previous_step_func(self, step):
        """Returns the function to go to the previous step."""
        if step == 2:
            return self.show_welcome_step
        elif step == 3:
            return self.show_dependency_step
        elif step == 4:
            return self.show_analysis_step
        elif step == 5:
            return self.show_completion_step
        return None # Should not happen

    def restart_wizard(self):
        """Restarts the wizard from the beginning."""
        print("Restarting setup wizard...")
        app_state.reset_wizard_state()
        self.show_welcome_step()

    def show_welcome_step(self):
        """Step 1: Welcome and directory selection."""
        self.current_step = 1
        self.clear_content()
        self.update_nav_buttons(1)

        welcome_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        welcome_frame.pack(fill="both", expand=True, padx=30, pady=15)

        ttk.Label(welcome_frame, text="🚀", font=("Arial", 36), background='white').pack(pady=(0, 5))
        ttk.Label(welcome_frame, text="Welcome to AI Pair Programming!", style='Title.TLabel').pack()
        ttk.Label(welcome_frame, text="Set up your autonomous AI assistant in just a few clicks.", font=("Arial", 11), background='white', foreground='#666').pack(pady=(5, 0))

        dir_main_frame = ttk.Frame(welcome_frame, style='Card.TFrame')
        dir_main_frame.pack(pady=15, padx=15, fill="x")

        ttk.Label(dir_main_frame, text="Choose Your Project Directory", style='H2.TLabel').pack(pady=(15, 8))
        self.dir_display = ttk.Label(dir_main_frame, text="📁 No directory selected yet", style='Dir.TLabel', width=60)
        self.dir_display.pack(pady=(0, 15))

        browse_btn = ttk.Button(dir_main_frame, text="📂 Browse for Directory", command=self.select_directory, style='Primary.TButton')
        browse_btn.pack(pady=(0, 20))

    def select_directory(self):
        """Handles directory selection and updates the UI and app state."""
        selected = filedialog.askdirectory(
            initialdir=app_state.working_dir,
            title="Select Your Project Directory"
        )
        if selected:
            app_state.set_working_dir(selected)
            
            dir_name = os.path.basename(selected)
            display_path = f"...{selected[-47:]}" if len(selected) > 50 else selected
            
            self.dir_display.config(text=f"✅ {dir_name}\n📍 {display_path}", style='Success.Dir.TLabel')
            self.next_btn.config(state="normal", text="Continue: Check Dependencies →")

    def show_dependency_step(self):
        """Step 2: Dependency check and installation."""
        self.current_step = 2
        self.clear_content()
        self.update_nav_buttons(2)

        dep_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        dep_frame.pack(expand=True, fill="both", padx=40, pady=40)

        ttk.Label(dep_frame, text="🔧 Setting Up Your System", style='Title.TLabel').pack(pady=20)

        self.dep_progress_text = scrolledtext.ScrolledText(dep_frame, height=12, width=70, wrap="word", font=("Consolas", 10))
        self.dep_progress_text.pack(fill="both", expand=True, pady=20)
        self.dep_progress_text.config(state="disabled")

        self.root.after(500, self.start_dependency_check)

    def start_dependency_check(self):
        """Starts the dependency checking process in a background thread."""
        self.add_progress_text("🔍 Checking system requirements...")
        threading.Thread(target=self.check_dependencies_background, daemon=True).start()

    def check_dependencies_background(self):
        """The actual dependency check logic that runs in the background."""
        try:
            # Check Python (implicitly ok since we are running)
            self.add_progress_text("✓ Python installation found")
            time.sleep(0.5)

            # Check and install packages
            install_successful = check_and_install_dependencies(self.add_progress_text)
            
            if not install_successful:
                 self.add_progress_text("❌ Could not install dependencies. Please check your internet connection and pip configuration.")
                 return

            # Check AutoHotkey
            self.add_progress_text("🔍 Checking for AutoHotkey...")
            if check_autohotkey():
                self.add_progress_text("✅ AutoHotkey v2 found.")
            else:
                self.add_progress_text("⚠️ AutoHotkey not found. Some features will be disabled. Please install AHK v2 for full functionality.")
            
            self.add_progress_text("\n🎉 System setup complete!")
            self.root.after(0, lambda: self.next_btn.config(state="normal"))

        except Exception as e:
            self.add_progress_text(f"❌ An unexpected error occurred: {e}")

    def add_progress_text(self, text: str):
        """Adds a line of text to the progress display, ensuring it's thread-safe."""
        def _update_text():
            self.dep_progress_text.config(state="normal")
            self.dep_progress_text.insert("end", f"{text}\n")
            self.dep_progress_text.see("end")
            self.dep_progress_text.config(state="disabled")
        
        # Make sure UI updates happen on the main thread
        self.root.after(0, _update_text)
        
    def show_analysis_step(self):
        """Step 3: Project analysis."""
        self.current_step = 3
        self.clear_content()
        self.update_nav_buttons(3)

        analysis_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        analysis_frame.pack(expand=True, fill="both", padx=40, pady=40)

        ttk.Label(analysis_frame, text="📊 Analyzing Your Project", style='Title.TLabel').pack(pady=20)
        ttk.Label(analysis_frame, text="Creating AI context from your project files...", font=("Arial", 12), background='white', foreground='#666').pack(pady=10)

        self.analysis_progress = scrolledtext.ScrolledText(analysis_frame, height=15, width=70, wrap="word", font=("Consolas", 10))
        self.analysis_progress.pack(fill="both", expand=True, pady=20)
        self.analysis_progress.config(state="disabled")

        self.root.after(500, self.start_project_analysis)

    def start_project_analysis(self):
        """Starts the project analysis in a background thread."""
        self.add_analysis_text("🔍 Starting project analysis...")
        threading.Thread(target=self.analyze_project_background, daemon=True).start()

    def analyze_project_background(self):
        """Runs the project analysis and updates the UI."""
        success = run_gitingest(self.add_analysis_text)
        if success:
            self.root.after(0, lambda: self.next_btn.config(state="normal"))
        else:
            self.add_analysis_text("❌ Analysis failed. You can try again or skip this step.")
            # Optionally enable the back button or a retry button here

    def add_analysis_text(self, text: str):
        """Adds a line of text to the analysis progress display."""
        def _update_text():
            self.analysis_progress.config(state="normal")
            self.analysis_progress.insert("end", f"{text}\n")
            self.analysis_progress.see("end")
            self.analysis_progress.config(state="disabled")
        self.root.after(0, _update_text)

    def show_completion_step(self):
        """Step 4: Setup completion summary."""
        self.current_step = 4
        self.clear_content()
        self.update_nav_buttons(4)
        
        comp_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        comp_frame.pack(expand=True, fill="both", padx=40, pady=40)

        ttk.Label(comp_frame, text="🎉", font=("Arial", 48), background='white').pack(pady=(20, 10))
        ttk.Label(comp_frame, text="Setup Complete!", style='Title.TLabel', foreground='#4CAF50').pack()
        ttk.Label(comp_frame, text="Your AI Pair Programming Assistant is ready to go!", font=("Arial", 12), background='white', foreground='#666').pack(pady=10)

        summary_card = ttk.Frame(comp_frame, style='Card.TFrame')
        summary_card.pack(pady=20, padx=20, fill='x')

        ttk.Label(summary_card, text="✅ What's Been Set Up", font=("Arial", 14, "bold"), background='#f8f9fa', foreground='#1976D2').pack(pady=10)
        
        summary_items = [
            ("📁", "Project directory configured"),
            ("🐍", "Python dependencies verified"),
            ("🔧", "AutoHotkey integration ready"),
            ("📊", "Project analysis completed"),
        ]
        
        for emoji, description in summary_items:
            item_frame = ttk.Frame(summary_card, style='Card.TFrame')
            item_frame.pack(fill="x", pady=4, padx=20)
            ttk.Label(item_frame, text=emoji, font=("Arial", 14), background='#f8f9fa').pack(side="left", padx=(0, 10))
            ttk.Label(item_frame, text=description, font=("Arial", 12), background='#f8f9fa', foreground='#333').pack(side="left")

    def show_launch_step(self):
        """Step 5: Launch control center."""
        self.current_step = 5
        self.clear_content()
        self.update_nav_buttons(5)

        launch_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        launch_frame.pack(expand=True, fill="both", padx=40, pady=40)

        ttk.Label(launch_frame, text="🚀", font=("Arial", 48), background='white').pack(pady=(20, 10))
        ttk.Label(launch_frame, text="Mission Control Center", style='Title.TLabel').pack()
        ttk.Label(launch_frame, text="All systems are go. Start your automation tasks.", font=("Arial", 12), background='white', foreground='#666').pack(pady=10)

        btn_frame = ttk.Frame(launch_frame, style='Content.TFrame')
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="⚙️ Open Advanced Control Center", command=self.open_advanced_mode).pack(pady=10, padx=10, fill='x')
        ttk.Button(btn_frame, text="Exit", command=self.on_close).pack(pady=10, padx=10, fill='x')

    def open_advanced_mode(self):
        """Destroys the wizard and opens the main advanced GUI window."""
        print("Opening advanced mode...")
        self.root.destroy()
        AdvancedGui(self.parent) 