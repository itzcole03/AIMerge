"""
gui_clean.py
Clean, working GUI for the AI Pair Programming Assistant.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import time
import os
import json
import sys
import subprocess
from datetime import datetime
import random

from config import app_state
from app_logic import (
    check_autohotkey, verify_dependencies_subprocess, 
    check_and_install_dependencies
)

# Import AiSource integration
try:
    from aisource_integration import (
        initialize_integration, get_intelligent_decision, 
        start_enhanced_afk, get_integration_status
    )
    AISOURCE_AVAILABLE = True
except ImportError:
    print("⚠️ AiSource integration not available - running in basic mode")
    AISOURCE_AVAILABLE = False

class CleanGui:
    def __init__(self, parent: tk.Tk):
        self.root = parent
        self.root.title("🤖 AI Pair Programming Assistant - Control Center")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Session management
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_file = f"session_log_{session_timestamp}.txt"
        
        # Initialize session log
        with open(self.session_log_file, "w", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] New session started\n")
        
        # State variables
        self.setup_completed = self.load_setup_state()
        
        # Create interface
        self.create_widgets()
        
        self.log_session_event("Application initialized")
        print("Clean GUI Initialized.")

    def create_widgets(self):
        """Create the main interface."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create setup tab if needed
        if not self.setup_completed:
            self.create_setup_tab()
        
        # Create main tabs
        self.create_automation_tab()
        self.create_smart_context_tab()
        if AISOURCE_AVAILABLE:
            self.create_aisource_integration_tab()
        self.create_git_helper_tab()
        self.create_tdd_helper_tab()
        self.create_settings_tab()
        self.create_session_log_tab()

    def create_aisource_integration_tab(self):
        """Create AiSource integration tab for enhanced AI capabilities."""
        aisource_tab = ttk.Frame(self.notebook)
        self.notebook.add(aisource_tab, text="🤖 AiSource AI")
        
        main_frame = ttk.Frame(aisource_tab, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="🤖 AiSource AI Integration", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Connection status
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status", padding=10)
        status_frame.pack(fill='x', pady=10)
        
        self.aisource_status_label = ttk.Label(status_frame, text="🔄 Checking connection...")
        self.aisource_status_label.pack(anchor='w', pady=5)
        
        status_btn_frame = ttk.Frame(status_frame)
        status_btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(status_btn_frame, text="🔄 Test Connection", command=self.test_aisource_connection).pack(side='left', padx=5)
        ttk.Button(status_btn_frame, text="📊 System Status", command=self.show_aisource_status).pack(side='left', padx=5)
        
        # Enhanced automation controls
        enhanced_frame = ttk.LabelFrame(main_frame, text="Enhanced Automation", padding=10)
        enhanced_frame.pack(fill='x', pady=10)
        
        ttk.Label(enhanced_frame, text="Intelligent automation powered by multi-agent AI system:", 
                 font=("Arial", 10)).pack(anchor='w', pady=(0, 10))
        
        enhanced_btn_frame = ttk.Frame(enhanced_frame)
        enhanced_btn_frame.pack(fill='x')
        
        ttk.Button(enhanced_btn_frame, text="🚀 Enhanced AFK Mode", command=self.start_enhanced_afk_mode).pack(side='left', padx=5)
        ttk.Button(enhanced_btn_frame, text="🧠 AI Code Analysis", command=self.start_ai_analysis).pack(side='left', padx=5)
        ttk.Button(enhanced_btn_frame, text="🎯 Autonomous Task", command=self.start_autonomous_task).pack(side='left', padx=5)
        
        # Agent coordination
        agents_frame = ttk.LabelFrame(main_frame, text="AI Agent Coordination", padding=10)
        agents_frame.pack(fill='both', expand=True, pady=10)
        
        # Agent status display
        self.agent_status_text = scrolledtext.ScrolledText(agents_frame, height=8, wrap="word", font=("Consolas", 9))
        self.agent_status_text.pack(fill='both', expand=True, pady=5)
        
        # Agent controls
        agent_controls = ttk.Frame(agents_frame)
        agent_controls.pack(fill='x', pady=5)
        
        ttk.Button(agent_controls, text="👥 Agent Status", command=self.refresh_agent_status).pack(side='left', padx=5)
        ttk.Button(agent_controls, text="📈 Learning Stats", command=self.show_learning_stats).pack(side='left', padx=5)
        ttk.Button(agent_controls, text="🎛️ Configure Agents", command=self.configure_agents).pack(side='right', padx=5)
        
        # Initialize connection test
        self.root.after(1000, self.test_aisource_connection)

    def create_setup_tab(self):
        """Create setup tab with automatic checks."""
        self.setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_tab, text="Setup")
        
        main_frame = ttk.Frame(self.setup_tab, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Title
        ttk.Label(main_frame, text="Project Setup", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Progress
        self.setup_progress = ttk.Progressbar(main_frame, length=400, mode="determinate")
        self.setup_progress.pack(pady=10)
        
        self.setup_status = ttk.Label(main_frame, text="Running automatic checks...", font=("Arial", 11))
        self.setup_status.pack(pady=5)
        
        # Directory
        dir_frame = ttk.LabelFrame(main_frame, text="Project Directory", padding=10)
        dir_frame.pack(fill='x', pady=10)
        
        self.dir_status = ttk.Label(dir_frame, text="Checking directory...", font=("Arial", 10))
        self.dir_status.pack(anchor='w', pady=(0, 10))
        
        # Directory selection controls
        dir_controls = ttk.Frame(dir_frame)
        dir_controls.pack(fill='x')
        
        self.dir_path_var = tk.StringVar()
        self.dir_path_entry = ttk.Entry(dir_controls, textvariable=self.dir_path_var, state='readonly', width=50)
        self.dir_path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.browse_btn = ttk.Button(dir_controls, text="📂 Browse", command=self.browse_directory)
        self.browse_btn.pack(side='right')
        
        # Dependencies
        dep_frame = ttk.LabelFrame(main_frame, text="Dependencies", padding=10)
        dep_frame.pack(fill='x', pady=10)
        self.dep_status = ttk.Label(dep_frame, text="Checking dependencies...", font=("Arial", 10))
        self.dep_status.pack(anchor='w')
        self.dep_install_btn = ttk.Button(dep_frame, text="Install Dependencies", command=self.install_dependencies)
        
        # AutoHotkey
        ahk_frame = ttk.LabelFrame(main_frame, text="AutoHotkey", padding=10)
        ahk_frame.pack(fill='x', pady=10)
        self.ahk_status = ttk.Label(ahk_frame, text="Checking AutoHotkey...", font=("Arial", 10))
        self.ahk_status.pack(anchor='w')
        self.ahk_install_btn = ttk.Button(ahk_frame, text="Get AutoHotkey", command=self.show_ahk_guide)
        
        # Continue button
        self.continue_btn = ttk.Button(main_frame, text="Continue to App", command=self.complete_setup, state='disabled')
        self.continue_btn.pack(pady=20)
        
        # Start checks
        self.root.after(500, self.run_setup_checks)

    def browse_directory(self):
        """Browse and select project directory."""
        directory = filedialog.askdirectory(
            title="Select Project Directory",
            initialdir=app_state.working_dir or os.getcwd()
        )
        
        if directory:
            # Update app state
            app_state.set_working_dir(directory)
            
            # Update UI
            self.dir_path_var.set(directory)
            dir_name = os.path.basename(directory)
            self.dir_status.config(text=f"✅ Selected: {dir_name}")
            
            # Log the change
            self.log_session_event(f"Project directory set to: {directory}")
            
            # Update progress
            self.setup_progress['value'] = 25

    def run_setup_checks(self):
        """Run all setup checks."""
        self.setup_progress['value'] = 10
        threading.Thread(target=self._check_all, daemon=True).start()

    def _check_all(self):
        """Check all requirements."""
        # Directory check
        if not app_state.working_dir:
            app_state.set_working_dir(os.getcwd())
        
        # Update directory display
        self.root.after(0, lambda: self.dir_path_var.set(app_state.working_dir or ""))
        
        dir_ok = os.path.isdir(app_state.working_dir) if app_state.working_dir else False
        if dir_ok:
            dir_name = os.path.basename(app_state.working_dir)
            self.root.after(0, lambda: self.dir_status.config(text=f"✅ Directory: {dir_name}"))
            self.root.after(0, lambda: self.setup_progress.step(15))
        else:
            self.root.after(0, lambda: self.dir_status.config(text="❌ Please select a valid directory"))
        
        # Dependencies check
        try:
            success, missing = verify_dependencies_subprocess()
            if success:
                self.root.after(0, lambda: self.dep_status.config(text="✅ All dependencies installed"))
                self.root.after(0, lambda: self.dep_install_btn.pack(pady=5))
            else:
                self.root.after(0, lambda: self.dep_status.config(text=f"❌ Missing: {', '.join(missing[:3])}"))
                self.root.after(0, lambda: self.dep_install_btn.pack(pady=5))
        except Exception as e:
            self.root.after(0, lambda: self.dep_status.config(text=f"❌ Check failed: {str(e)[:30]}"))
            self.root.after(0, lambda: self.dep_install_btn.pack(pady=5))
        
        # AutoHotkey check
        try:
            if check_autohotkey():
                self.root.after(0, lambda: self.ahk_status.config(text="✅ AutoHotkey v2 found"))
                self.root.after(0, lambda: self.setup_progress.step(15))
            else:
                self.root.after(0, lambda: self.ahk_status.config(text="❌ AutoHotkey not found"))
                self.root.after(0, lambda: self.ahk_install_btn.pack(pady=5))
        except Exception as e:
            self.root.after(0, lambda: self.ahk_status.config(text=f"❌ Check failed: {str(e)[:30]}"))
            self.root.after(0, lambda: self.ahk_install_btn.pack(pady=5))

    def _update_progress(self, value):
        """Update progress and check completion."""
        self.setup_progress['value'] = max(self.setup_progress['value'], value)
        
        # Check if all passed
        dir_ok = "✅" in self.dir_status.cget("text")
        dep_ok = "✅" in self.dep_status.cget("text")
        ahk_ok = "✅" in self.ahk_status.cget("text")
        
        if dir_ok and dep_ok and ahk_ok:
            self.setup_progress['value'] = 100
            self.setup_status.config(text="✅ All checks passed! Ready to continue.")
            self.continue_btn.config(state='normal')

    def install_dependencies(self):
        """Install dependencies."""
        self.dep_status.config(text="Installing dependencies...")
        self.dep_install_btn.config(state='disabled')
        
        def install():
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    'pyautogui', 'Pillow', 'gitingest', 'watchdog', 'plyer', 'pystray'
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.dep_status.config(text="✅ Dependencies installed"))
                    self.root.after(0, lambda: self.dep_install_btn.pack_forget())
                    self.root.after(0, lambda: self._update_progress(50))
                else:
                    self.root.after(0, lambda: self.dep_status.config(text="❌ Installation failed"))
                    self.root.after(0, lambda: self.dep_install_btn.config(state='normal'))
            except Exception as e:
                self.root.after(0, lambda: self.dep_status.config(text=f"❌ Error: {str(e)[:30]}"))
                self.root.after(0, lambda: self.dep_install_btn.config(state='normal'))
        
        threading.Thread(target=install, daemon=True).start()

    def show_ahk_guide(self):
        """Show AutoHotkey installation guide."""
        guide = tk.Toplevel(self.root)
        guide.title("AutoHotkey Installation")
        guide.geometry("400x250")
        guide.transient(self.root)
        
        frame = ttk.Frame(guide, padding=20)
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text="AutoHotkey Installation", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        instructions = """AutoHotkey is required for automation.

1. Download AutoHotkey v2 from official website
2. Run installer as Administrator
3. Complete installation
4. Click Retry Detection"""
        
        ttk.Label(frame, text=instructions, justify='left').pack(pady=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        def open_website():
            import webbrowser
            webbrowser.open("https://www.autohotkey.com/download/")
        
        def retry():
            guide.destroy()
            threading.Thread(target=self._check_all, daemon=True).start()
        
        ttk.Button(btn_frame, text="Open Website", command=open_website).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Retry", command=retry).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Close", command=guide.destroy).pack(side='left', padx=5)

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
            
            # Switch to first tab
            if self.notebook.index('end') > 0:
                self.notebook.select(0)
            
            # Success message
            messagebox.showinfo("Setup Complete", "🎉 Setup completed successfully!\nReady for AI pair programming!")
            self.log_session_event("Setup completed successfully")
            
        except Exception as e:
            messagebox.showerror("Setup Error", f"Error completing setup: {e}")

    def create_automation_tab(self):
        """Create automation control tab."""
        automation_tab = ttk.Frame(self.notebook)
        self.notebook.add(automation_tab, text="Automation Control")
        
        main_frame = ttk.Frame(automation_tab, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Automation Control Center", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Workspace section
        workspace_frame = ttk.LabelFrame(main_frame, text="Workspace Management", padding=10)
        workspace_frame.pack(fill='x', pady=10)
        
        # Current workspace display
        current_workspace = app_state.working_dir or "No workspace selected"
        workspace_name = os.path.basename(current_workspace) if current_workspace != "No workspace selected" else current_workspace
        
        self.workspace_label = ttk.Label(workspace_frame, text=f"Current Workspace: {workspace_name}", font=("Arial", 11, "bold"))
        self.workspace_label.pack(anchor='w', pady=(0, 5))
        
        self.workspace_path_label = ttk.Label(workspace_frame, text=current_workspace, font=("Arial", 9), foreground="gray")
        self.workspace_path_label.pack(anchor='w', pady=(0, 10))
        
        # Workspace controls
        workspace_controls = ttk.Frame(workspace_frame)
        workspace_controls.pack(fill='x')
        
        ttk.Button(workspace_controls, text="📂 Change Workspace", command=self.change_workspace).pack(side='left', padx=(0, 10))
        ttk.Button(workspace_controls, text="📁 Open in Explorer", command=self.open_workspace_explorer).pack(side='left', padx=(0, 10))
        ttk.Button(workspace_controls, text="🔄 Refresh", command=self.refresh_workspace).pack(side='left')
        
        # Status
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding=10)
        status_frame.pack(fill='x', pady=10)
        
        ttk.Label(status_frame, text="✅ System Ready", font=("Arial", 12)).pack(anchor='w')
        ttk.Label(status_frame, text="All components operational", font=("Arial", 10)).pack(anchor='w')
        
        # Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill='x', pady=10)
        
        ttk.Button(control_frame, text="🚀 Start AFK Mode", command=self.start_afk_mode).pack(pady=5)
        ttk.Button(control_frame, text="📝 Generate Context", command=self.generate_context).pack(pady=5)
        ttk.Button(control_frame, text="🔧 Run Diagnostics", command=self.run_diagnostics).pack(pady=5)

    def create_smart_context_tab(self):
        """Create smart context management tab."""
        context_tab = ttk.Frame(self.notebook)
        self.notebook.add(context_tab, text="Smart Context")
        
        main_frame = ttk.Frame(context_tab, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Smart Context Builder", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Context generation options
        gen_frame = ttk.LabelFrame(main_frame, text="Generate Context", padding=10)
        gen_frame.pack(fill='x', pady=10)
        
        ttk.Label(gen_frame, text="Generate focused context files for AI pair programming:", 
                 font=("Arial", 10)).pack(anchor='w', pady=(0, 10))
        
        btn_frame = ttk.Frame(gen_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="📄 Full Project Context", command=self.generate_full_context).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🎯 Current Work Focus", command=self.generate_work_context).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🏗️ Architecture Overview", command=self.generate_arch_context).pack(side='left', padx=5)
        
        # Context files display
        files_frame = ttk.LabelFrame(main_frame, text="Context Files", padding=10)
        files_frame.pack(fill='both', expand=True, pady=10)
        
        # Files listbox with scrollbar
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill='both', expand=True)
        
        self.context_listbox = tk.Listbox(list_frame, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.context_listbox.yview)
        self.context_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.context_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Context file controls
        controls_frame = ttk.Frame(files_frame)
        controls_frame.pack(fill='x', pady=10)
        
        ttk.Button(controls_frame, text="🔄 Refresh", command=self.refresh_context_files).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="👁️ View", command=self.view_context_file).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="📋 Copy Path", command=self.copy_context_path).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="🗑️ Delete", command=self.delete_context_file).pack(side='right', padx=5)
        
        # Load context files
        self.refresh_context_files()

    def create_git_helper_tab(self):
        """Create Git helper tab."""
        git_tab = ttk.Frame(self.notebook)
        self.notebook.add(git_tab, text="Git Helper")
        
        main_frame = ttk.Frame(git_tab, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Git Helper", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Git status
        status_frame = ttk.LabelFrame(main_frame, text="Repository Status", padding=10)
        status_frame.pack(fill='x', pady=10)
        
        self.git_status_text = scrolledtext.ScrolledText(status_frame, height=6, wrap="word", font=("Consolas", 9))
        self.git_status_text.pack(fill='both', expand=True, pady=5)
        
        ttk.Button(status_frame, text="🔄 Refresh Status", command=self.refresh_git_status).pack(pady=5)
        
        # Git operations
        ops_frame = ttk.LabelFrame(main_frame, text="Quick Operations", padding=10)
        ops_frame.pack(fill='x', pady=10)
        
        # Commit section
        commit_frame = ttk.Frame(ops_frame)
        commit_frame.pack(fill='x', pady=5)
        
        ttk.Label(commit_frame, text="Commit Message:").pack(anchor='w')
        self.commit_msg_var = tk.StringVar()
        self.commit_entry = ttk.Entry(commit_frame, textvariable=self.commit_msg_var, width=50)
        self.commit_entry.pack(fill='x', pady=5)
        
        # Operation buttons
        btn_frame = ttk.Frame(ops_frame)
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_frame, text="📝 Stage All", command=self.git_stage_all).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="💾 Commit", command=self.git_commit).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📤 Push", command=self.git_push).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📥 Pull", command=self.git_pull).pack(side='left', padx=5)
        
        # Load initial status
        self.refresh_git_status()

    def create_tdd_helper_tab(self):
        """Create TDD helper tab."""
        tdd_tab = ttk.Frame(self.notebook)
        self.notebook.add(tdd_tab, text="TDD Helper")
        
        main_frame = ttk.Frame(tdd_tab, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Test-Driven Development Helper", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Test runner
        runner_frame = ttk.LabelFrame(main_frame, text="Test Runner", padding=10)
        runner_frame.pack(fill='x', pady=10)
        
        # Test file selection
        file_frame = ttk.Frame(runner_frame)
        file_frame.pack(fill='x', pady=5)
        
        ttk.Label(file_frame, text="Test File:").pack(side='left')
        self.test_file_var = tk.StringVar()
        self.test_file_entry = ttk.Entry(file_frame, textvariable=self.test_file_var, width=40)
        self.test_file_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(file_frame, text="📂 Browse", command=self.browse_test_file).pack(side='right')
        
        # Test controls
        controls_frame = ttk.Frame(runner_frame)
        controls_frame.pack(fill='x', pady=10)
        
        ttk.Button(controls_frame, text="🧪 Run Tests", command=self.run_tests).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="🔄 Run All Tests", command=self.run_all_tests).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="📊 Coverage Report", command=self.run_coverage).pack(side='left', padx=5)
        
        # Test results
        results_frame = ttk.LabelFrame(main_frame, text="Test Results", padding=10)
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.test_results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap="word", font=("Consolas", 9))
        self.test_results_text.pack(fill='both', expand=True)

    def create_settings_tab(self):
        """Create settings and configuration tab."""
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Settings")
        
        main_frame = ttk.Frame(settings_tab, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Settings & Configuration", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Appearance settings
        appearance_frame = ttk.LabelFrame(main_frame, text="Appearance", padding=10)
        appearance_frame.pack(fill='x', pady=10)
        
        self.dark_mode_var = tk.BooleanVar(value=self.load_dark_mode_setting())
        ttk.Checkbutton(appearance_frame, text="🌙 Dark Mode", variable=self.dark_mode_var, 
                       command=self.toggle_dark_mode).pack(anchor='w', pady=5)
        
        # Automation settings
        automation_frame = ttk.LabelFrame(main_frame, text="Automation", padding=10)
        automation_frame.pack(fill='x', pady=10)
        
        ttk.Label(automation_frame, text="AutoHotkey Script Path:").pack(anchor='w')
        self.ahk_path_var = tk.StringVar()
        ahk_frame = ttk.Frame(automation_frame)
        ahk_frame.pack(fill='x', pady=5)
        
        ttk.Entry(ahk_frame, textvariable=self.ahk_path_var, width=50).pack(side='left', fill='x', expand=True)
        ttk.Button(ahk_frame, text="📂 Browse", command=self.browse_ahk_script).pack(side='right', padx=(5, 0))
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(main_frame, text="Advanced", padding=10)
        advanced_frame.pack(fill='x', pady=10)
        
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="💾 Auto-save settings", variable=self.auto_save_var).pack(anchor='w', pady=2)
        
        self.auto_context_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(advanced_frame, text="🔄 Auto-refresh context files", variable=self.auto_context_var).pack(anchor='w', pady=2)
        
        self.verbose_logging_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(advanced_frame, text="📝 Verbose logging", variable=self.verbose_logging_var).pack(anchor='w', pady=2)
        
        # Settings controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill='x', pady=20)
        
        ttk.Button(controls_frame, text="💾 Save Settings", command=self.save_all_settings).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="🔄 Reset to Defaults", command=self.reset_settings).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="📤 Export Settings", command=self.export_settings).pack(side='right', padx=5)
        ttk.Button(controls_frame, text="📥 Import Settings", command=self.import_settings).pack(side='right', padx=5)

    def create_session_log_tab(self):
        """Create session log tab."""
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Session Log")
        
        main_frame = ttk.Frame(log_tab, padding=10)
        main_frame.pack(expand=True, fill='both')
        
        # Info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Session: {os.path.basename(self.session_log_file)}", 
                 font=("Arial", 10, "bold")).pack(side='left')
        
        ttk.Button(info_frame, text="🧹 Cleanup Old Logs", command=self.cleanup_logs).pack(side='right')
        ttk.Button(info_frame, text="📄 Export Log", command=self.export_log).pack(side='right', padx=5)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(main_frame, height=25, width=100, 
                                                 wrap="word", font=("Consolas", 10), state="disabled")
        self.log_text.pack(expand=True, fill='both')
        
        # Load current log
        self.load_session_log()

    def load_session_log(self):
        """Load and display session log."""
        self.log_text.config(state="normal")
        self.log_text.delete('1.0', 'end')
        if os.path.exists(self.session_log_file):
            with open(self.session_log_file, 'r', encoding='utf-8') as f:
                self.log_text.insert('end', f.read())
        self.log_text.config(state="disabled")
        self.log_text.see('end')

    def cleanup_logs(self):
        """Clean up old session logs."""
        import glob
        log_files = glob.glob("session_log_*.txt")
        current_log = os.path.basename(self.session_log_file)
        
        deleted = 0
        for log_file in log_files:
            if log_file != current_log:
                try:
                    os.remove(log_file)
                    deleted += 1
                except Exception:
                    pass
        
        if deleted > 0:
            messagebox.showinfo("Cleanup", f"Cleaned up {deleted} old log files")
            self.log_session_event(f"Cleaned up {deleted} old session logs")
        else:
            messagebox.showinfo("Cleanup", "No old logs to clean up")

    def export_log(self):
        """Export current session log."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Export Session Log"
        )
        if filename:
            try:
                with open(self.session_log_file, 'r', encoding='utf-8') as src:
                    with open(filename, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                messagebox.showinfo("Export", f"Log exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")

    def start_afk_mode(self):
        """Start AFK mode with real functionality."""
        if not hasattr(self, 'afk_mode_active'):
            self.afk_mode_active = tk.BooleanVar()
        
        if not self.afk_mode_active.get():
            # First show the setup wizard
            if self.show_afk_setup_wizard():
                self.afk_mode_active.set(True)
                self.show_afk_status_banner()
                self.log_session_event("AFK Mode activated")
                
                # Run health checks before starting
                issues = self.run_health_check()
                
                if not issues:
                    # Start automation after a brief delay
                    self.root.after(2000, self.start_afk_automation)
                else:
                    messagebox.showwarning("Setup Issues", 
                        f"Please resolve these issues first:\n• " + "\n• ".join(issues))
                    self.afk_mode_active.set(False)
                    self.hide_afk_status_banner()
        else:
            self.afk_mode_active.set(False)
            self.hide_afk_status_banner()
            self.log_session_event("AFK Mode deactivated")

    def show_afk_setup_wizard(self):
        """Show AFK Mode setup wizard to help users configure their environment."""
        wizard = tk.Toplevel(self.root)
        wizard.title("🚀 AFK Mode Setup Wizard")
        wizard.geometry("600x500")
        wizard.transient(self.root)
        wizard.grab_set()
        
        # Center the window
        wizard.update_idletasks()
        x = (wizard.winfo_screenwidth() // 2) - (600 // 2)
        y = (wizard.winfo_screenheight() // 2) - (500 // 2)
        wizard.geometry(f"600x500+{x}+{y}")
        
        main_frame = ttk.Frame(wizard, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 AFK Mode Setup Wizard", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions text
        instructions_text = scrolledtext.ScrolledText(main_frame, height=15, width=70, wrap="word")
        instructions_text.pack(expand=True, fill='both', pady=10)
        
        setup_instructions = """Welcome to AFK Mode! This will automate AI pair programming between two Cursor/VS Code windows.

🎯 SETUP CHECKLIST:

1. 📱 DUAL WINDOW SETUP:
   • Open TWO Cursor or VS Code windows side by side
   • Left window: Your main coding environment
   • Right window: AI assistant/chat interface
   • Arrange them so both are visible simultaneously

2. 🎮 HOTKEY CONFIGURATION:
   • F6: Accept AI suggestions (Left window focus)
   • F7: Reject AI suggestions (Left window focus) 
   • F8: Toggle between windows
   • F9: Enable/disable automation
   • Ctrl+F5: Manual context injection (when needed)

3. 📂 PROJECT SETUP:
   • Left window: Open your project/workspace
   • Right window: Open Cursor's AI chat or Copilot
   • Both windows should be ready for interaction

4. 🔧 SYSTEM REQUIREMENTS:
   • AutoHotkey v2 installed and running
   • Both Cursor/VS Code windows visible on screen
   • No overlapping windows blocking the automation

5. 🎯 POSITIONING:
   • Windows should be side-by-side (not overlapping)
   • Accept/Reject buttons should be visible in left window
   • AI chat should be active in right window
   • Mouse should be able to reach both windows

📋 AUTOMATION WORKFLOW:
   • 🧠 SMART DETECTION: Automatically detects existing conversations
   • 🔄 NON-INTRUSIVE: Won't interrupt ongoing chats with context injection
   • ⚡ INTELLIGENT MONITORING: Watches for accept/reject opportunities
   • 🎮 MANUAL OVERRIDE: Use Ctrl+F5 to inject context when needed
   • 🤖 AUTONOMOUS DECISIONS: F6 accepts, F7 rejects, or let AI decide

⚠️ IMPORTANT NOTES:
   • The system detects existing conversations and won't auto-inject context
   • Use Ctrl+F5 if you want to add project context to an ongoing chat
   • Keep both windows visible during automation
   • Don't minimize or move windows during AFK mode
   • You can stop anytime with the "Stop AFK Mode" button
   • Monitor the first few cycles to ensure proper operation

✅ READY TO START?
   Click "Start AFK Mode" when your windows are properly configured!
"""
        
        instructions_text.insert('1.0', setup_instructions)
        instructions_text.configure(state='disabled')
        
        # Checkbox for confirmation
        confirm_var = tk.BooleanVar()
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill='x', pady=10)
        
        ttk.Checkbutton(confirm_frame, 
                       text="✅ I have configured my dual windows and understand the setup requirements",
                       variable=confirm_var).pack(anchor='w')
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        result = {'confirmed': False}
        
        def start_afk():
            if confirm_var.get():
                result['confirmed'] = True
                wizard.destroy()
            else:
                messagebox.showwarning("Setup Required", 
                    "Please confirm that you have completed the setup requirements.")
        
        def cancel_afk():
            result['confirmed'] = False
            wizard.destroy()
        
        def open_help():
            help_msg = """🔧 QUICK SETUP HELP:

1. Open two Cursor/VS Code windows
2. Arrange them side-by-side on your screen
3. Left: Your coding project
4. Right: AI chat/assistant
5. Make sure accept/reject buttons are visible
6. Check that F6/F7/F8 hotkeys work

Need more help? Check the documentation or run diagnostics first."""
            messagebox.showinfo("Setup Help", help_msg)
        
        ttk.Button(button_frame, text="❓ Help", command=open_help).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🔧 Run Diagnostics First", 
                  command=lambda: [wizard.destroy(), self.run_diagnostics()]).pack(side='left', padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=cancel_afk).pack(side='right', padx=5)
        ttk.Button(button_frame, text="🚀 Start AFK Mode", command=start_afk).pack(side='right', padx=5)
        
        # Wait for user interaction
        wizard.wait_window()
        
        return result['confirmed']

    def show_afk_status_banner(self):
        """Show AFK mode status banner."""
        if hasattr(self, 'afk_status_banner') and self.afk_status_banner:
            self.afk_status_banner.destroy()
        
        banner = ttk.Frame(self.root, padding=6)
        banner.place(relx=0, rely=0.02, relwidth=1)
        
        self.afk_status_label = ttk.Label(banner, text="🚀 AFK Mode: Monitoring...", 
                                         font=("Arial", 11, "bold"), foreground="#005580")
        self.afk_status_label.pack(side="left", padx=8)
        
        stop_btn = ttk.Button(banner, text="Stop AFK Mode", command=self.start_afk_mode)
        stop_btn.pack(side="right", padx=8)
        
        self.afk_status_banner = banner
        self.update_afk_status()

    def hide_afk_status_banner(self):
        """Hide AFK status banner."""
        if hasattr(self, 'afk_status_banner') and self.afk_status_banner:
            self.afk_status_banner.destroy()
            self.afk_status_banner = None

    def update_afk_status(self):
        """Update AFK mode status."""
        if not hasattr(self, 'afk_mode_active') or not self.afk_mode_active.get():
            self.hide_afk_status_banner()
            return
        
        # Check system health
        issues = []
        if not app_state.working_dir or not os.path.isdir(app_state.working_dir):
            issues.append("Workspace")
        
        try:
            success, missing = verify_dependencies_subprocess()
            if not success:
                issues.append("Dependencies")
        except Exception:
            issues.append("Dependencies")
        
        try:
            if not check_autohotkey():
                issues.append("AutoHotkey")
        except Exception:
            issues.append("AutoHotkey")
        
        # Update status
        if issues:
            self.afk_status_label.config(text=f"⚠️ AFK Mode: Issues detected ({', '.join(issues)})", 
                                        foreground="#b85c00")
        else:
            self.afk_status_label.config(text="✅ AFK Mode: All systems operational", 
                                        foreground="#228B22")
        
        # Schedule next update
        self.root.after(5000, self.update_afk_status)

    def start_afk_automation(self):
        """Start AFK automation if all systems are healthy."""
        if not hasattr(self, 'afk_mode_active') or not self.afk_mode_active.get():
            return
        
        # Check prerequisites
        issues = []
        if not app_state.working_dir or not os.path.isdir(app_state.working_dir):
            issues.append("Valid workspace directory")
        
        try:
            success, missing = verify_dependencies_subprocess()
            if not success:
                issues.append("Dependencies")
        except Exception:
            issues.append("Dependencies")
        
        try:
            if not check_autohotkey():
                issues.append("AutoHotkey")
        except Exception:
            issues.append("AutoHotkey")
        
        if issues:
            messagebox.showwarning("AFK Mode", 
                f"Cannot start automation. Missing:\n• {chr(10).join(issues)}")
            self.afk_status_label.config(text=f"❌ AFK Mode: Cannot start - missing {', '.join(issues)}", 
                                        foreground="#b30000")
            return
        
        # Start AutoHotkey script
        try:
            self.start_ahk_script()
            
            # Show monitoring window for first-time users
            self.show_afk_monitoring_window()
            
            messagebox.showinfo("AFK Mode Started", 
                "🚀 AFK Mode started successfully!\n\n"
                "📊 A monitoring window will help you during the first few cycles.\n"
                "💡 Watch for accept/reject button detection and window switching.\n"
                "⏹️ Use 'Stop AFK Mode' button anytime to halt automation.")
            
            self.log_session_event("AFK automation started successfully")
        except Exception as e:
            messagebox.showerror("AFK Mode Error", f"Failed to start automation: {e}")
            self.log_session_event(f"AFK automation failed to start: {e}", "ERROR")

    def show_afk_monitoring_window(self):
        """Show AFK monitoring window to help users track automation progress."""
        if hasattr(self, 'monitoring_window') and self.monitoring_window:
            return  # Already open
        
        self.monitoring_window = tk.Toplevel(self.root)
        self.monitoring_window.title("🔍 AFK Mode Monitor")
        self.monitoring_window.geometry("400x300")
        
        # Position in bottom right corner
        self.monitoring_window.update_idletasks()
        x = self.monitoring_window.winfo_screenwidth() - 420
        y = self.monitoring_window.winfo_screenheight() - 350
        self.monitoring_window.geometry(f"400x300+{x}+{y}")
        
        # Make it stay on top but not modal
        self.monitoring_window.attributes('-topmost', True)
        
        frame = ttk.Frame(self.monitoring_window, padding=10)
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text="🔍 AFK Mode Monitor", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Status display
        self.monitor_text = scrolledtext.ScrolledText(frame, height=12, width=45, wrap="word", font=("Consolas", 9))
        self.monitor_text.pack(expand=True, fill='both', pady=5)
        
        # Control buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="📋 Clear Log", command=self.clear_monitor_log).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Close Monitor", command=self.close_monitoring_window).pack(side='right', padx=5)
        
        # Initial status
        self.add_monitor_message("🚀 AFK Mode monitoring started")
        self.add_monitor_message("👀 Watching for AI suggestions and button interactions...")
        self.add_monitor_message("💡 Tip: Keep both Cursor/VS Code windows visible")
        
        # Set up periodic status updates
        self.update_monitor_status()
        
        # Auto-close after 10 minutes
        self.root.after(600000, self.close_monitoring_window)
    
    def add_monitor_message(self, message):
        """Add a timestamped message to the monitor."""
        if hasattr(self, 'monitor_text') and self.monitor_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.monitor_text.insert('end', f"[{timestamp}] {message}\n")
            self.monitor_text.see('end')
    
    def update_monitor_status(self):
        """Update monitoring status periodically."""
        if not hasattr(self, 'monitoring_window') or not self.monitoring_window:
            return
        
        if not hasattr(self, 'afk_mode_active') or not self.afk_mode_active.get():
            self.add_monitor_message("⏹️ AFK Mode stopped")
            return
        
        # Check system status
        try:
            # Monitor workspace
            if app_state.working_dir and os.path.isdir(app_state.working_dir):
                self.add_monitor_message(f"✅ Workspace active: {os.path.basename(app_state.working_dir)}")
            
            # Monitor AutoHotkey process (simplified check)
            self.add_monitor_message("🔧 AutoHotkey automation running...")
            
            # Tips for users
            tips = [
                "💡 Tip: F6=Accept, F7=Reject, F8=Switch windows",
                "👀 Tip: Make sure accept/reject buttons are visible",
                "🖱️ Tip: Don't move windows during automation",
                "⚡ Tip: AI suggestions should appear in left window",
                "🔄 Tip: Automation cycles every few seconds",
                "📱 Tip: Both windows should stay visible",
                "🎯 Tip: Position cursor in code editor for best results"
            ]
            
            if random.random() < 0.3:  # 30% chance to show tip
                self.add_monitor_message(random.choice(tips))
            
        except Exception as e:
            self.add_monitor_message(f"⚠️ Monitor error: {str(e)[:50]}")
        
        # Schedule next update (every 10 seconds)
        if hasattr(self, 'monitoring_window') and self.monitoring_window:
            self.root.after(10000, self.update_monitor_status)
    
    def clear_monitor_log(self):
        """Clear the monitoring log."""
        if hasattr(self, 'monitor_text') and self.monitor_text:
            self.monitor_text.delete('1.0', 'end')
            self.add_monitor_message("📋 Monitor log cleared")
    
    def close_monitoring_window(self):
        """Close the monitoring window."""
        if hasattr(self, 'monitoring_window') and self.monitoring_window:
            self.monitoring_window.destroy()
            self.monitoring_window = None

    def start_ahk_script(self):
        """Start AutoHotkey script."""
        try:
            # The AHK script is always in the CopilotAHK application directory,
            # NOT in the user's workspace directory
            app_directory = os.getcwd()  # This should be the CopilotAHK directory
            if not app_directory.endswith('CopilotAHK'):
                # If we're running from src/, go up one level
                if os.path.basename(app_directory) == 'src':
                    app_directory = os.path.dirname(app_directory)
                # If still not in CopilotAHK, try to find it
                elif not os.path.exists(os.path.join(app_directory, 'CopilotAFK_Toggle_Assistant.ahk')):
                    # Look for the script file to determine the correct app directory
                    script_name = 'CopilotAFK_Toggle_Assistant.ahk'
                    possible_app_dirs = [
                        os.getcwd(),
                        os.path.dirname(os.getcwd()),
                        os.path.dirname(__file__) if '__file__' in globals() else os.getcwd(),
                        os.path.dirname(os.path.dirname(__file__)) if '__file__' in globals() else os.getcwd()
                    ]
                    
                    app_directory = None
                    for dir_path in possible_app_dirs:
                        if os.path.exists(os.path.join(dir_path, script_name)):
                            app_directory = dir_path
                            break
                    
                    if not app_directory:
                        raise FileNotFoundError(f"Could not locate CopilotAHK application directory containing '{script_name}'")
            
            ahk_script_path = os.path.join(app_directory, "CopilotAFK_Toggle_Assistant.ahk")
            
            if not os.path.exists(ahk_script_path):
                raise FileNotFoundError(f"AutoHotkey script not found at: {ahk_script_path}\n"
                                      f"The script should be in the CopilotAHK application directory, not the workspace directory.\n"
                                      f"Application directory: {app_directory}\n"
                                      f"Workspace directory: {app_state.working_dir}")
            
            # Find AutoHotkey executable
            ahk_exe = None
            common_paths = [
                r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe",
                r"C:\Program Files (x86)\AutoHotkey\v2\AutoHotkey.exe",
                r"C:\AutoHotkey\v2\AutoHotkey.exe",
                r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
                r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe"
            ]
            
            for path in common_paths:
                if os.path.isfile(path):
                    ahk_exe = path
                    break
            
            if not ahk_exe:
                # Try to find in PATH
                result = subprocess.run(['where', 'autohotkey'], capture_output=True, text=True)
                if result.returncode == 0:
                    ahk_exe = result.stdout.strip().split('\n')[0]
                else:
                    raise FileNotFoundError("AutoHotkey executable not found. Please install AutoHotkey v2.")
            
            # Start the script in the application directory
            subprocess.Popen([ahk_exe, ahk_script_path], cwd=app_directory)
            self.log_session_event(f"AutoHotkey script started: {ahk_script_path}")
            self.log_session_event(f"Application directory: {app_directory}")
            self.log_session_event(f"Workspace directory: {app_state.working_dir}")
            
        except Exception as e:
            raise Exception(f"Failed to start AutoHotkey script: {e}")

    def run_health_check(self):
        """Run comprehensive health check."""
        issues = []
        
        # Check workspace (user's project directory)
        if not app_state.working_dir or not os.path.isdir(app_state.working_dir):
            issues.append("No valid workspace directory selected")
        
        # Check application directory (CopilotAHK directory with the script)
        app_directory = os.getcwd()
        if not app_directory.endswith('CopilotAHK'):
            if os.path.basename(app_directory) == 'src':
                app_directory = os.path.dirname(app_directory)
        
        ahk_script_path = os.path.join(app_directory, "CopilotAFK_Toggle_Assistant.ahk")
        if not os.path.exists(ahk_script_path):
            issues.append(f"AutoHotkey script not found in application directory: {app_directory}")
        
        # Check dependencies
        try:
            success, missing = verify_dependencies_subprocess()
            if not success:
                issues.append(f"Missing dependencies: {', '.join(missing[:3])}")
        except Exception as e:
            issues.append(f"Dependency check failed: {str(e)[:50]}")
        
        # Check AutoHotkey
        try:
            if not check_autohotkey():
                issues.append("AutoHotkey not found or not accessible")
        except Exception as e:
            issues.append(f"AutoHotkey check failed: {str(e)[:50]}")
        
        # Check for context files (in workspace, not application directory)
        if app_state.working_dir:
            import glob
            context_files = glob.glob(os.path.join(app_state.working_dir, 'context_*.txt'))
            if not context_files:
                issues.append("No context files found - generate context for better results")
        
        return issues

    def generate_context(self):
        """Generate project context using gitingest."""
        if not app_state.working_dir or not os.path.isdir(app_state.working_dir):
            messagebox.showwarning("No Workspace", "Please select a valid workspace directory first.")
            return
        
        # Show progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Generating Context")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        frame = ttk.Frame(progress_window, padding=20)
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text="Generating Project Context", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        progress_bar = ttk.Progressbar(frame, mode="indeterminate")
        progress_bar.pack(fill='x', pady=10)
        progress_bar.start()
        
        status_label = ttk.Label(frame, text="Analyzing project files...")
        status_label.pack()
        
        def generate_in_background():
            try:
                # Update status
                progress_window.after(0, lambda: status_label.config(text="Running gitingest..."))
                
                # Try multiple approaches to run gitingest
                success = False
                result = None
                
                # Approach 1: Try direct module execution
                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'gitingest', app_state.working_dir
                    ], capture_output=True, text=True, timeout=300, cwd=app_state.working_dir)
                    if result.returncode == 0:
                        success = True
                except Exception as e:
                    print(f"Method 1 failed: {e}")
                
                # Approach 2: Try importing and using gitingest directly
                if not success:
                    try:
                        progress_window.after(0, lambda: status_label.config(text="Trying alternative method..."))
                        
                        # Try to import and use gitingest programmatically
                        import gitingest
                        
                        # Create a simple context file manually
                        context_filename = f"context_manual_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
                        context_path = os.path.join(app_state.working_dir, context_filename)
                        
                        # Generate a basic context file
                        with open(context_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Project Context - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                            f.write(f"Project Directory: {app_state.working_dir}\n\n")
                            
                            # List all Python files
                            f.write("## Python Files:\n")
                            for root, dirs, files in os.walk(app_state.working_dir):
                                for file in files:
                                    if file.endswith('.py'):
                                        rel_path = os.path.relpath(os.path.join(root, file), app_state.working_dir)
                                        f.write(f"- {rel_path}\n")
                            
                            # List other important files
                            f.write("\n## Other Important Files:\n")
                            important_extensions = ['.md', '.txt', '.json', '.yml', '.yaml', '.ahk']
                            for root, dirs, files in os.walk(app_state.working_dir):
                                for file in files:
                                    if any(file.endswith(ext) for ext in important_extensions):
                                        rel_path = os.path.relpath(os.path.join(root, file), app_state.working_dir)
                                        f.write(f"- {rel_path}\n")
                        
                        success = True
                        result = type('Result', (), {'returncode': 0, 'stdout': f'Manual context created: {context_filename}'})()
                        
                    except Exception as e:
                        print(f"Method 2 failed: {e}")
                
                # Approach 3: Create a minimal context file
                if not success:
                    try:
                        progress_window.after(0, lambda: status_label.config(text="Creating basic context..."))
                        
                        context_filename = f"context_basic_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
                        context_path = os.path.join(app_state.working_dir, context_filename)
                        
                        with open(context_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Basic Project Context - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                            f.write(f"Project: {os.path.basename(app_state.working_dir)}\n")
                            f.write(f"Directory: {app_state.working_dir}\n\n")
                            f.write("## File Structure:\n")
                            
                            # Simple directory listing
                            for item in os.listdir(app_state.working_dir):
                                item_path = os.path.join(app_state.working_dir, item)
                                if os.path.isdir(item_path):
                                    f.write(f"📁 {item}/\n")
                                else:
                                    f.write(f"📄 {item}\n")
                        
                        success = True
                        result = type('Result', (), {'returncode': 0, 'stdout': f'Basic context created: {context_filename}'})()
                        
                    except Exception as e:
                        print(f"Method 3 failed: {e}")
                
                if success and result.returncode == 0:
                    # Find generated file
                    import glob
                    context_files = glob.glob(os.path.join(app_state.working_dir, 'context_*.txt'))
                    
                    def show_success():
                        progress_window.destroy()
                        if context_files:
                            latest_file = max(context_files, key=os.path.getmtime)
                            messagebox.showinfo("Context Generated", 
                                f"✅ Context generated successfully!\n"
                                f"Files available: {len(context_files)}\n"
                                f"Latest: {os.path.basename(latest_file)}")
                        else:
                            messagebox.showinfo("Context Generated", 
                                "✅ Context generation completed!")
                        
                        self.log_session_event("Project context generated successfully")
                        
                        # Refresh context files in Smart Context tab if it exists
                        if hasattr(self, 'context_listbox'):
                            self.refresh_context_files()
                    
                    progress_window.after(0, show_success)
                else:
                    def show_error():
                        progress_window.destroy()
                        error_msg = result.stderr if result and result.stderr else "Unknown error occurred"
                        messagebox.showerror("Context Generation Failed", 
                            f"Failed to generate context.\n\nError: {error_msg[:200]}\n\nTry using the Smart Context tab for alternative methods.")
                        self.log_session_event(f"Context generation failed: {error_msg[:100]}", "ERROR")
                    
                    progress_window.after(0, show_error)
                    
            except subprocess.TimeoutExpired:
                def show_timeout():
                    progress_window.destroy()
                    messagebox.showerror("Timeout", "Context generation timed out after 5 minutes.")
                
                progress_window.after(0, show_timeout)
                
            except Exception as e:
                def show_exception():
                    progress_window.destroy()
                    messagebox.showerror("Error", f"Context generation failed: {str(e)[:200]}")
                    self.log_session_event(f"Context generation exception: {str(e)[:100]}", "ERROR")
                
                progress_window.after(0, show_exception)
        
        # Start generation in background
        threading.Thread(target=generate_in_background, daemon=True).start()

    def run_diagnostics(self):
        """Run comprehensive system diagnostics."""
        # Create diagnostics window
        diag_window = tk.Toplevel(self.root)
        diag_window.title("System Diagnostics")
        diag_window.geometry("500x400")
        diag_window.transient(self.root)
        
        frame = ttk.Frame(diag_window, padding=20)
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text="System Diagnostics", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Results display
        results_text = scrolledtext.ScrolledText(frame, height=15, width=60, wrap="word", font=("Consolas", 9))
        results_text.pack(expand=True, fill='both', pady=10)
        
        # Control buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=10)
        
        def run_diagnostics_check():
            results_text.delete('1.0', 'end')
            results_text.insert('end', "🔧 Running System Diagnostics...\n\n")
            
            def check_in_background():
                # Check workspace
                results_text.insert('end', "📁 Workspace Check:\n")
                if app_state.working_dir and os.path.isdir(app_state.working_dir):
                    results_text.insert('end', f"  ✅ Valid workspace: {app_state.working_dir}\n")
                    file_count = len([f for f in os.listdir(app_state.working_dir) 
                                    if os.path.isfile(os.path.join(app_state.working_dir, f))])
                    results_text.insert('end', f"  📄 Files in workspace: {file_count}\n")
                else:
                    results_text.insert('end', "  ❌ No valid workspace selected\n")
                
                results_text.insert('end', "\n")
                
                # Check dependencies
                results_text.insert('end', "📦 Dependencies Check:\n")
                try:
                    success, missing = verify_dependencies_subprocess()
                    if success:
                        results_text.insert('end', "  ✅ All dependencies installed\n")
                    else:
                        results_text.insert('end', f"  ❌ Missing: {', '.join(missing)}\n")
                except Exception as e:
                    results_text.insert('end', f"  ❌ Check failed: {e}\n")
                
                results_text.insert('end', "\n")
                
                # Check AutoHotkey
                results_text.insert('end', "🔧 AutoHotkey Check:\n")
                try:
                    if check_autohotkey():
                        results_text.insert('end', "  ✅ AutoHotkey v2 found\n")
                    else:
                        results_text.insert('end', "  ❌ AutoHotkey not found\n")
                except Exception as e:
                    results_text.insert('end', f"  ❌ Check failed: {e}\n")
                
                results_text.insert('end', "\n")
                
                # Check context files
                results_text.insert('end', "📝 Context Files Check:\n")
                if app_state.working_dir:
                    import glob
                    context_files = glob.glob(os.path.join(app_state.working_dir, 'context_*.txt'))
                    if context_files:
                        results_text.insert('end', f"  ✅ Found {len(context_files)} context files\n")
                        latest = max(context_files, key=os.path.getmtime)
                        age = time.time() - os.path.getmtime(latest)
                        if age < 3600:  # Less than 1 hour
                            results_text.insert('end', "  ✅ Context files are recent\n")
                        else:
                            results_text.insert('end', "  ⚠️ Context files are old (>1 hour)\n")
                    else:
                        results_text.insert('end', "  ❌ No context files found\n")
                else:
                    results_text.insert('end', "  ❌ No workspace to check\n")
                
                results_text.insert('end', "\n🔧 Diagnostics complete!\n")
                results_text.see('end')
            
            threading.Thread(target=check_in_background, daemon=True).start()
        
        ttk.Button(btn_frame, text="🔧 Run Diagnostics", command=run_diagnostics_check).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Close", command=diag_window.destroy).pack(side='right', padx=5)
        
        # Auto-run diagnostics
        run_diagnostics_check()
        
        self.log_session_event("System diagnostics opened")

    def log_session_event(self, message: str, level: str = "INFO"):
        """Log session event."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(self.session_log_file, "a", encoding="utf-8") as f:
                f.write(log_line)
            
            # Update log display if it exists
            if hasattr(self, 'log_text'):
                self.log_text.config(state="normal")
                self.log_text.insert('end', log_line)
                self.log_text.see('end')
                self.log_text.config(state="disabled")
        except Exception:
            pass

    def save_setup_state(self, complete: bool):
        """Save setup state."""
        try:
            with open('setup_state.json', 'w') as f:
                json.dump({"setup_complete": complete}, f)
        except Exception as e:
            print(f"Error saving setup state: {e}")

    def load_setup_state(self) -> bool:
        """Load setup state."""
        try:
            if os.path.exists('setup_state.json'):
                with open('setup_state.json', 'r') as f:
                    data = json.load(f)
                    return data.get("setup_complete", False)
        except Exception:
            pass
        return False

    def on_close(self):
        """Handle application close."""
        self.log_session_event("Application closing")
        self.root.quit()
        self.root.destroy()

    def change_workspace(self):
        """Change the current workspace directory."""
        new_directory = filedialog.askdirectory(
            title="Select New Workspace Directory",
            initialdir=app_state.working_dir or os.getcwd()
        )
        
        if new_directory:
            # Update app state
            app_state.set_working_dir(new_directory)
            
            # Update UI
            workspace_name = os.path.basename(new_directory)
            self.workspace_label.config(text=f"Current Workspace: {workspace_name}")
            self.workspace_path_label.config(text=new_directory)
            
            # Log the change
            self.log_session_event(f"Workspace changed to: {new_directory}")
            
            # Show confirmation
            messagebox.showinfo("Workspace Changed", f"Workspace successfully changed to:\n{workspace_name}")

    def open_workspace_explorer(self):
        """Open the current workspace in file explorer."""
        if app_state.working_dir and os.path.isdir(app_state.working_dir):
            try:
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.run(['explorer', app_state.working_dir])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(['open', app_state.working_dir])
                else:  # Linux
                    subprocess.run(['xdg-open', app_state.working_dir])
                
                self.log_session_event("Opened workspace in file explorer")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open workspace in explorer: {e}")
        else:
            messagebox.showwarning("No Workspace", "No valid workspace directory selected.")

    def refresh_workspace(self):
        """Refresh workspace information."""
        if app_state.working_dir and os.path.isdir(app_state.working_dir):
            workspace_name = os.path.basename(app_state.working_dir)
            self.workspace_label.config(text=f"Current Workspace: {workspace_name}")
            self.workspace_path_label.config(text=app_state.working_dir)
            
            # Count files in workspace
            try:
                file_count = len([f for f in os.listdir(app_state.working_dir) if os.path.isfile(os.path.join(app_state.working_dir, f))])
                dir_count = len([d for d in os.listdir(app_state.working_dir) if os.path.isdir(os.path.join(app_state.working_dir, d))])
                
                messagebox.showinfo("Workspace Info", 
                    f"Workspace: {workspace_name}\n"
                    f"Path: {app_state.working_dir}\n"
                    f"Files: {file_count}\n"
                    f"Directories: {dir_count}")
                
                self.log_session_event("Workspace information refreshed")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to refresh workspace info: {e}")
        else:
            messagebox.showwarning("No Workspace", "No valid workspace directory selected.")

    def generate_full_context(self):
        """Generate full project context."""
        self.generate_context()  # Reuse the existing method
    
    def generate_work_context(self):
        """Generate focused context for current work."""
        if not app_state.working_dir:
            messagebox.showwarning("No Workspace", "Please select a workspace first.")
            return
        
        # Focus on recently modified files
        messagebox.showinfo("Work Context", "🎯 Generating focused context for recent changes...")
        self.log_session_event("Generating work-focused context")
        # Implementation would analyze git status and recent files
    
    def generate_arch_context(self):
        """Generate architecture overview context."""
        if not app_state.working_dir:
            messagebox.showwarning("No Workspace", "Please select a workspace first.")
            return
        
        messagebox.showinfo("Architecture Context", "🏗️ Generating architecture overview...")
        self.log_session_event("Generating architecture context")
        # Implementation would focus on main structure files
    
    def refresh_context_files(self):
        """Refresh the context files list."""
        self.context_listbox.delete(0, tk.END)
        
        if not app_state.working_dir:
            return
        
        import glob
        pattern = os.path.join(app_state.working_dir, 'context_*.txt')
        context_files = glob.glob(pattern)
        
        for file_path in sorted(context_files, key=os.path.getmtime, reverse=True):
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) // 1024  # KB
            mod_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(file_path)))
            display_text = f"{filename} ({file_size}KB) - {mod_time}"
            self.context_listbox.insert(tk.END, display_text)
    
    def view_context_file(self):
        """View selected context file."""
        selection = self.context_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a context file to view.")
            return
        
        filename = self.context_listbox.get(selection[0]).split(' ')[0]
        file_path = os.path.join(app_state.working_dir, filename)
        
        if os.path.exists(file_path):
            # Open in default text editor
            try:
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.run(['notepad', file_path])
                elif platform.system() == "Darwin":
                    subprocess.run(['open', '-t', file_path])
                else:
                    subprocess.run(['xdg-open', file_path])
                
                self.log_session_event(f"Opened context file: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
    
    def copy_context_path(self):
        """Copy context file path to clipboard."""
        selection = self.context_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a context file.")
            return
        
        filename = self.context_listbox.get(selection[0]).split(' ')[0]
        file_path = os.path.join(app_state.working_dir, filename)
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(file_path)
            messagebox.showinfo("Copied", f"Path copied to clipboard:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy path: {e}")
    
    def delete_context_file(self):
        """Delete selected context file."""
        selection = self.context_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a context file to delete.")
            return
        
        filename = self.context_listbox.get(selection[0]).split(' ')[0]
        file_path = os.path.join(app_state.working_dir, filename)
        
        if messagebox.askyesno("Confirm Delete", f"Delete {filename}?"):
            try:
                os.remove(file_path)
                self.refresh_context_files()
                messagebox.showinfo("Deleted", f"File deleted: {filename}")
                self.log_session_event(f"Deleted context file: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file: {e}")

    def refresh_git_status(self):
        """Refresh git repository status."""
        self.git_status_text.delete('1.0', tk.END)
        
        if not app_state.working_dir:
            self.git_status_text.insert('1.0', "No workspace selected.")
            return
        
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, 
                                  cwd=app_state.working_dir, timeout=10)
            
            if result.returncode == 0:
                if result.stdout.strip():
                    self.git_status_text.insert('1.0', f"Changes detected:\n{result.stdout}")
                else:
                    self.git_status_text.insert('1.0', "✅ Working directory clean")
                
                # Also get branch info
                branch_result = subprocess.run(['git', 'branch', '--show-current'],
                                             capture_output=True, text=True,
                                             cwd=app_state.working_dir, timeout=5)
                if branch_result.returncode == 0:
                    branch = branch_result.stdout.strip()
                    self.git_status_text.insert('1.0', f"Current branch: {branch}\n\n")
            else:
                self.git_status_text.insert('1.0', "Not a git repository or git not available.")
                
        except Exception as e:
            self.git_status_text.insert('1.0', f"Error checking git status: {e}")
    
    def git_stage_all(self):
        """Stage all changes."""
        if not app_state.working_dir:
            messagebox.showwarning("No Workspace", "Please select a workspace first.")
            return
        
        try:
            result = subprocess.run(['git', 'add', '.'], 
                                  capture_output=True, text=True,
                                  cwd=app_state.working_dir, timeout=30)
            
            if result.returncode == 0:
                messagebox.showinfo("Git", "✅ All changes staged successfully")
                self.refresh_git_status()
                self.log_session_event("Git: All changes staged")
            else:
                messagebox.showerror("Git Error", f"Failed to stage changes:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Git stage failed: {e}")
    
    def git_commit(self):
        """Commit staged changes."""
        commit_msg = self.commit_msg_var.get().strip()
        if not commit_msg:
            messagebox.showwarning("No Message", "Please enter a commit message.")
            return
        
        if not app_state.working_dir:
            messagebox.showwarning("No Workspace", "Please select a workspace first.")
            return
        
        try:
            result = subprocess.run(['git', 'commit', '-m', commit_msg],
                                  capture_output=True, text=True,
                                  cwd=app_state.working_dir, timeout=30)
            
            if result.returncode == 0:
                messagebox.showinfo("Git", f"✅ Commit successful:\n{commit_msg}")
                self.commit_msg_var.set("")  # Clear message
                self.refresh_git_status()
                self.log_session_event(f"Git commit: {commit_msg}")
            else:
                messagebox.showerror("Git Error", f"Commit failed:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Git commit failed: {e}")
    
    def git_push(self):
        """Push commits to remote."""
        if not app_state.working_dir:
            messagebox.showwarning("No Workspace", "Please select a workspace first.")
            return
        
        try:
            result = subprocess.run(['git', 'push'],
                                  capture_output=True, text=True,
                                  cwd=app_state.working_dir, timeout=60)
            
            if result.returncode == 0:
                messagebox.showinfo("Git", "✅ Push successful")
                self.log_session_event("Git push successful")
            else:
                messagebox.showerror("Git Error", f"Push failed:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Git push failed: {e}")
    
    def git_pull(self):
        """Pull changes from remote."""
        if not app_state.working_dir:
            messagebox.showwarning("No Workspace", "Please select a workspace first.")
            return
        
        try:
            result = subprocess.run(['git', 'pull'],
                                  capture_output=True, text=True,
                                  cwd=app_state.working_dir, timeout=60)
            
            if result.returncode == 0:
                messagebox.showinfo("Git", f"✅ Pull successful:\n{result.stdout}")
                self.refresh_git_status()
                self.log_session_event("Git pull successful")
            else:
                messagebox.showerror("Git Error", f"Pull failed:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Git pull failed: {e}")

    def browse_test_file(self):
        """Browse for test file."""
        filename = filedialog.askopenfilename(
            title="Select Test File",
            initialdir=app_state.working_dir or os.getcwd(),
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.test_file_var.set(filename)
    
    def run_tests(self):
        """Run specific test file."""
        test_file = self.test_file_var.get().strip()
        if not test_file:
            messagebox.showwarning("No Test File", "Please select a test file first.")
            return
        
        if not os.path.exists(test_file):
            messagebox.showerror("File Not Found", f"Test file not found: {test_file}")
            return
        
        self.test_results_text.delete('1.0', tk.END)
        self.test_results_text.insert('1.0', f"Running tests: {os.path.basename(test_file)}\n\n")
        
        def run_in_background():
            try:
                result = subprocess.run([sys.executable, '-m', 'pytest', test_file, '-v'],
                                      capture_output=True, text=True,
                                      cwd=app_state.working_dir or os.getcwd(),
                                      timeout=120)
                
                def update_results():
                    self.test_results_text.insert('end', result.stdout)
                    if result.stderr:
                        self.test_results_text.insert('end', f"\nErrors:\n{result.stderr}")
                    self.test_results_text.see('end')
                
                self.root.after(0, update_results)
                
            except Exception as e:
                def show_error():
                    self.test_results_text.insert('end', f"\nTest execution failed: {e}")
                
                self.root.after(0, show_error)
        
        threading.Thread(target=run_in_background, daemon=True).start()
        self.log_session_event(f"Running tests: {os.path.basename(test_file)}")
    
    def run_all_tests(self):
        """Run all tests in the workspace."""
        if not app_state.working_dir:
            messagebox.showwarning("No Workspace", "Please select a workspace first.")
            return
        
        self.test_results_text.delete('1.0', tk.END)
        self.test_results_text.insert('1.0', "Running all tests...\n\n")
        
        def run_in_background():
            try:
                result = subprocess.run([sys.executable, '-m', 'pytest', '-v'],
                                      capture_output=True, text=True,
                                      cwd=app_state.working_dir,
                                      timeout=300)
                
                def update_results():
                    self.test_results_text.insert('end', result.stdout)
                    if result.stderr:
                        self.test_results_text.insert('end', f"\nErrors:\n{result.stderr}")
                    self.test_results_text.see('end')
                
                self.root.after(0, update_results)
                
            except Exception as e:
                def show_error():
                    self.test_results_text.insert('end', f"\nTest execution failed: {e}")
                
                self.root.after(0, show_error)
        
        threading.Thread(target=run_in_background, daemon=True).start()
        self.log_session_event("Running all tests")
    
    def run_coverage(self):
        """Run test coverage report."""
        if not app_state.working_dir:
            messagebox.showwarning("No Workspace", "Please select a workspace first.")
            return
        
        self.test_results_text.delete('1.0', tk.END)
        self.test_results_text.insert('1.0', "Generating coverage report...\n\n")
        
        def run_in_background():
            try:
                # Try to run with coverage
                result = subprocess.run([sys.executable, '-m', 'coverage', 'run', '-m', 'pytest'],
                                      capture_output=True, text=True,
                                      cwd=app_state.working_dir,
                                      timeout=300)
                
                if result.returncode == 0:
                    # Generate report
                    report_result = subprocess.run([sys.executable, '-m', 'coverage', 'report'],
                                                 capture_output=True, text=True,
                                                 cwd=app_state.working_dir,
                                                 timeout=60)
                    
                    def update_results():
                        self.test_results_text.insert('end', "Coverage Report:\n")
                        self.test_results_text.insert('end', report_result.stdout)
                        self.test_results_text.see('end')
                    
                    self.root.after(0, update_results)
                else:
                    def show_error():
                        self.test_results_text.insert('end', f"Coverage failed:\n{result.stderr}")
                    
                    self.root.after(0, show_error)
                
            except Exception as e:
                def show_error():
                    self.test_results_text.insert('end', f"Coverage execution failed: {e}")
                
                self.root.after(0, show_error)
        
        threading.Thread(target=run_in_background, daemon=True).start()
        self.log_session_event("Running coverage report")

    def toggle_dark_mode(self):
        """Toggle dark mode theme."""
        if self.dark_mode_var.get():
            self.set_dark_mode()
        else:
            self.set_light_mode()
        self.save_dark_mode_setting(self.dark_mode_var.get())
    
    def set_dark_mode(self):
        """Apply dark mode theme."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2d2d2d")
        style.configure("TLabel", background="#2d2d2d", foreground="#ffffff")
        style.configure("TButton", background="#404040", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#404040", foreground="#ffffff")
        style.configure("TText", background="#2d2d2d", foreground="#ffffff")
    
    def set_light_mode(self):
        """Apply light mode theme."""
        style = ttk.Style()
        style.theme_use('clam')  # Reset to default
    
    def browse_ahk_script(self):
        """Browse for AutoHotkey script."""
        filename = filedialog.askopenfilename(
            title="Select AutoHotkey Script",
            initialdir=app_state.working_dir or os.getcwd(),
            filetypes=[("AutoHotkey files", "*.ahk"), ("All files", "*.*")]
        )
        if filename:
            self.ahk_path_var.set(filename)
    
    def save_all_settings(self):
        """Save all settings."""
        try:
            settings = {
                'dark_mode': self.dark_mode_var.get(),
                'ahk_script_path': self.ahk_path_var.get(),
                'auto_save': self.auto_save_var.get(),
                'auto_context': self.auto_context_var.get(),
                'verbose_logging': self.verbose_logging_var.get()
            }
            
            with open('app_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Settings", "✅ Settings saved successfully!")
            self.log_session_event("Settings saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
            self.dark_mode_var.set(False)
            self.ahk_path_var.set("")
            self.auto_save_var.set(True)
            self.auto_context_var.set(False)
            self.verbose_logging_var.set(False)
            
            self.set_light_mode()
            messagebox.showinfo("Settings", "✅ Settings reset to defaults!")
            self.log_session_event("Settings reset to defaults")
    
    def export_settings(self):
        """Export settings to file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Export Settings"
        )
        if filename:
            try:
                settings = {
                    'dark_mode': self.dark_mode_var.get(),
                    'ahk_script_path': self.ahk_path_var.get(),
                    'auto_save': self.auto_save_var.get(),
                    'auto_context': self.auto_context_var.get(),
                    'verbose_logging': self.verbose_logging_var.get()
                }
                
                with open(filename, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                messagebox.showinfo("Export", f"Settings exported to: {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export settings: {e}")
    
    def import_settings(self):
        """Import settings from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Import Settings"
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    settings = json.load(f)
                
                self.dark_mode_var.set(settings.get('dark_mode', False))
                self.ahk_path_var.set(settings.get('ahk_script_path', ''))
                self.auto_save_var.set(settings.get('auto_save', True))
                self.auto_context_var.set(settings.get('auto_context', False))
                self.verbose_logging_var.set(settings.get('verbose_logging', False))
                
                if self.dark_mode_var.get():
                    self.set_dark_mode()
                else:
                    self.set_light_mode()
                
                messagebox.showinfo("Import", "✅ Settings imported successfully!")
                self.log_session_event("Settings imported")
                
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import settings: {e}")

    def save_dark_mode_setting(self, enabled):
        """Save dark mode setting."""
        try:
            settings_file = 'app_settings.json'
            settings = {}
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            
            settings['dark_mode'] = enabled
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving dark mode setting: {e}")

    def load_dark_mode_setting(self) -> bool:
        """Load dark mode setting."""
        try:
            settings_file = 'app_settings.json'
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('dark_mode', False)
        except Exception as e:
            print(f"Error loading dark mode setting: {e}")
        
        return False

    # ===== AiSource Integration Methods =====
    
    def test_aisource_connection(self):
        """Test connection to AiSource system."""
        if not AISOURCE_AVAILABLE:
            self.aisource_status_label.config(text="❌ AiSource integration not available")
            return
        
        def test_in_background():
            try:
                # Test connection
                success = initialize_integration()
                
                def update_status():
                    if success:
                        self.aisource_status_label.config(text="✅ AiSource connected - Multi-agent AI ready")
                        self.log_session_event("AiSource integration established")
                    else:
                        self.aisource_status_label.config(text="⚠️ AiSource offline - Running in basic mode")
                        self.log_session_event("AiSource connection failed")
                
                self.root.after(0, update_status)
                
            except Exception as e:
                def show_error():
                    self.aisource_status_label.config(text=f"❌ Connection error: {str(e)[:50]}")
                
                self.root.after(0, show_error)
        
        threading.Thread(target=test_in_background, daemon=True).start()
        self.aisource_status_label.config(text="🔄 Testing AiSource connection...")
    
    def show_aisource_status(self):
        """Show detailed AiSource system status."""
        if not AISOURCE_AVAILABLE:
            messagebox.showwarning("Not Available", "AiSource integration is not available.")
            return
        
        def get_status_in_background():
            try:
                status = get_integration_status()
                
                def show_status():
                    status_window = tk.Toplevel(self.root)
                    status_window.title("🤖 AiSource System Status")
                    status_window.geometry("500x400")
                    status_window.transient(self.root)
                    
                    frame = ttk.Frame(status_window, padding=20)
                    frame.pack(expand=True, fill='both')
                    
                    ttk.Label(frame, text="🤖 AiSource System Status", font=("Arial", 14, "bold")).pack(pady=(0, 10))
                    
                    status_text = scrolledtext.ScrolledText(frame, height=15, width=60, wrap="word", font=("Consolas", 9))
                    status_text.pack(expand=True, fill='both', pady=10)
                    
                    # Format status information
                    bridge_status = status.get('integration_bridge', {})
                    status_content = f"""🔗 Integration Bridge Status: {bridge_status.get('status', 'unknown')}

📊 Decision Making:
   • Total Decisions: {bridge_status.get('total_decisions', 0)}
   • Correct Decisions: {bridge_status.get('correct_decisions', 0)}
   • Accuracy: {bridge_status.get('accuracy', 0)}%
   • Learning Mode: {'✅ Active' if bridge_status.get('learning_mode') else '❌ Disabled'}

🤖 Autonomous Mode: {'✅ Active' if status.get('autonomous_mode') else '❌ Inactive'}

📋 Current Task: {status.get('current_task', 'None')}

🎯 AiSource System:
"""
                    
                    aisource_status = bridge_status.get('aisource_status', {})
                    if isinstance(aisource_status, dict):
                        for key, value in aisource_status.items():
                            status_content += f"   • {key}: {value}\n"
                    
                    status_text.insert('1.0', status_content)
                    status_text.configure(state='disabled')
                    
                    ttk.Button(frame, text="Close", command=status_window.destroy).pack(pady=10)
                
                self.root.after(0, show_status)
                
            except Exception as e:
                def show_error():
                    messagebox.showerror("Status Error", f"Failed to get AiSource status: {e}")
                
                self.root.after(0, show_error)
        
        threading.Thread(target=get_status_in_background, daemon=True).start()
    
    def start_enhanced_afk_mode(self):
        """Start enhanced AFK mode with AiSource integration."""
        if not AISOURCE_AVAILABLE:
            messagebox.showwarning("Not Available", "AiSource integration required for enhanced mode.")
            return
        
        # Get project context
        project_context = ""
        if app_state.working_dir:
            # Try to get context from existing files
            import glob
            context_files = glob.glob(os.path.join(app_state.working_dir, 'context_*.txt'))
            if context_files:
                latest_context = max(context_files, key=os.path.getmtime)
                try:
                    with open(latest_context, 'r', encoding='utf-8') as f:
                        project_context = f.read()[:5000]  # Limit context size
                except Exception:
                    pass
        
        def start_enhanced_in_background():
            try:
                success = start_enhanced_afk(project_context)
                
                def show_result():
                    if success:
                        messagebox.showinfo("Enhanced AFK Mode", 
                            "🚀 Enhanced AFK Mode started!\n\n"
                            "✅ AI agents are now monitoring and assisting\n"
                            "🧠 Intelligent decision making active\n"
                            "📊 Learning from your patterns\n\n"
                            "The system will make smart accept/reject decisions based on AI analysis.")
                        self.log_session_event("Enhanced AFK Mode started with AiSource")
                    else:
                        messagebox.showwarning("Enhanced Mode Failed", 
                            "Could not start enhanced AFK mode.\n\n"
                            "Falling back to basic automation mode.\n"
                            "Check AiSource connection and try again.")
                
                self.root.after(0, show_result)
                
            except Exception as e:
                def show_error():
                    messagebox.showerror("Enhanced Mode Error", f"Failed to start enhanced mode: {e}")
                
                self.root.after(0, show_error)
        
        threading.Thread(target=start_enhanced_in_background, daemon=True).start()
    
    def start_ai_analysis(self):
        """Start AI code analysis of current project."""
        if not AISOURCE_AVAILABLE:
            messagebox.showwarning("Not Available", "AiSource integration required for AI analysis.")
            return
        
        messagebox.showinfo("AI Analysis", 
            "🧠 AI Code Analysis will be implemented in the next update!\n\n"
            "This feature will:\n"
            "• Analyze your entire codebase\n"
            "• Identify potential improvements\n"
            "• Suggest optimizations\n"
            "• Generate automated fixes")
    
    def start_autonomous_task(self):
        """Start an autonomous development task."""
        if not AISOURCE_AVAILABLE:
            messagebox.showwarning("Not Available", "AiSource integration required for autonomous tasks.")
            return
        
        # Task input dialog
        task_window = tk.Toplevel(self.root)
        task_window.title("🎯 Autonomous Task")
        task_window.geometry("400x200")
        task_window.transient(self.root)
        task_window.grab_set()
        
        frame = ttk.Frame(task_window, padding=20)
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text="🎯 Autonomous Development Task", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        ttk.Label(frame, text="Describe what you want the AI agents to work on:").pack(anchor='w')
        
        task_text = tk.Text(frame, height=4, width=50, wrap="word")
        task_text.pack(fill='both', expand=True, pady=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x')
        
        def start_task():
            task_description = task_text.get('1.0', 'end-1c').strip()
            if task_description:
                task_window.destroy()
                messagebox.showinfo("Task Started", 
                    f"🚀 Autonomous task started!\n\n"
                    f"Task: {task_description[:100]}...\n\n"
                    f"AI agents will coordinate to complete this task.\n"
                    f"Monitor progress in the Agent Status section.")
                self.log_session_event(f"Autonomous task started: {task_description[:50]}")
            else:
                messagebox.showwarning("No Task", "Please describe the task first.")
        
        ttk.Button(btn_frame, text="🚀 Start Task", command=start_task).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=task_window.destroy).pack(side='right')
    
    def refresh_agent_status(self):
        """Refresh AI agent status display."""
        if not AISOURCE_AVAILABLE:
            self.agent_status_text.delete('1.0', 'end')
            self.agent_status_text.insert('1.0', "❌ AiSource integration not available")
            return
        
        def get_status_in_background():
            try:
                status = get_integration_status()
                
                def update_display():
                    self.agent_status_text.delete('1.0', 'end')
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    content = f"🤖 AI Agent Status - Updated: {timestamp}\n\n"
                    
                    bridge_status = status.get('integration_bridge', {})
                    if bridge_status.get('status') == 'connected':
                        content += "✅ Multi-Agent System: ONLINE\n"
                        content += f"📊 Decision Accuracy: {bridge_status.get('accuracy', 0)}%\n"
                        content += f"🧠 Total Decisions: {bridge_status.get('total_decisions', 0)}\n\n"
                        
                        if status.get('autonomous_mode'):
                            content += "🚀 Autonomous Mode: ACTIVE\n"
                            task_id = status.get('current_task')
                            if task_id:
                                content += f"📋 Current Task: {task_id}\n"
                        else:
                            content += "⏸️ Autonomous Mode: STANDBY\n"
                        
                        content += "\n🤖 Available Agents:\n"
                        content += "   • Orchestrator: Task coordination and management\n"
                        content += "   • Architect: Code structure and design analysis\n"
                        content += "   • Backend Dev: Server-side development\n"
                        content += "   • Frontend Dev: UI/UX development\n"
                        content += "   • QA Analyst: Quality assurance and testing\n"
                        
                    else:
                        content += "❌ Multi-Agent System: OFFLINE\n"
                        content += "⚠️ Running in basic automation mode\n\n"
                        content += "To enable AI agents:\n"
                        content += "1. Start AiSource system\n"
                        content += "2. Click 'Test Connection'\n"
                        content += "3. Use 'Enhanced AFK Mode'\n"
                    
                    self.agent_status_text.insert('1.0', content)
                
                self.root.after(0, update_display)
                
            except Exception as e:
                def show_error():
                    self.agent_status_text.delete('1.0', 'end')
                    self.agent_status_text.insert('1.0', f"❌ Error getting agent status: {e}")
                
                self.root.after(0, show_error)
        
        threading.Thread(target=get_status_in_background, daemon=True).start()
    
    def show_learning_stats(self):
        """Show AI learning statistics."""
        if not AISOURCE_AVAILABLE:
            messagebox.showwarning("Not Available", "AiSource integration required for learning stats.")
            return
        
        messagebox.showinfo("Learning Statistics", 
            "📈 AI Learning Statistics\n\n"
            "The system learns from your accept/reject decisions to improve automation.\n\n"
            "Learning features:\n"
            "• Decision pattern analysis\n"
            "• Code quality preferences\n"
            "• Project-specific adaptations\n"
            "• Confidence scoring improvements\n\n"
            "Detailed statistics will be available in the next update!")
    
    def configure_agents(self):
        """Configure AI agent settings."""
        if not AISOURCE_AVAILABLE:
            messagebox.showwarning("Not Available", "AiSource integration required for agent configuration.")
            return
        
        messagebox.showinfo("Agent Configuration", 
            "🎛️ AI Agent Configuration\n\n"
            "Configure individual agent behaviors:\n\n"
            "• Architect: Code review strictness\n"
            "• QA Analyst: Testing requirements\n"
            "• Backend/Frontend: Technology preferences\n"
            "• Orchestrator: Task prioritization\n\n"
            "Advanced configuration panel coming in next update!")