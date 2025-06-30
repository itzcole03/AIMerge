"""
config.py
Configuration variables for the AI Pair Programming Assistant application.
"""

import os
import json
import subprocess
from typing import Optional, Dict, Any

# --- FILE AND SCRIPT PATHS ---
AHK_SCRIPT = "CopilotAFK_Toggle_Assistant.ahk"
GITINGEST_SCRIPT = "generate_gitingest_summary.py"
SUMMARY_FILE = "gitingest_summary.txt"
CONFIG_FILE = "config.json"
CONTEXT_DIR = "copilot_context"

def get_working_dir() -> str:
    """
    Determines the working directory by checking for the AHK script's presence.
    Falls back to the current directory if the script is not found in its own path.
    """
    try:
        # Get the directory of the currently running script (e.g., main.py)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # We need to look in the parent directory for the AHK script, as we are in src/
        project_root = os.path.dirname(script_dir)
        
        ahk_in_root = os.path.exists(os.path.join(project_root, AHK_SCRIPT))
        
        if ahk_in_root:
            print(f"[DEBUG] AHK script found in project root. Working directory set to: {project_root}")
            return project_root
        else:
            # Fallback for when the structure is different
            print(f"[DEBUG] AHK script not in project root. Falling back to current directory: {os.path.abspath('.')}")
            return os.path.abspath(".")

    except Exception as e:
        print(f"[DEBUG] Error in working directory setup: {e}")
        return os.path.abspath(".")

# --- STATE MANAGEMENT ---
class AppState:
    """
    A class to manage the state of the application.
    """
    def __init__(self, working_dir: str):
        self.working_dir: str = working_dir
        self.automation_state: Dict[str, Any] = {
            "ahk_running": False,
            "last_context_update": None,
            "autonomous_mode": False,
            "dual_agent_active": False,
            "context_auto_update": False
        }
        self.session_goal: Dict[str, Any] = {
            "plan_path": None,
            "tasks": [], # List of strings
            "current_task_index": -1
        }
        self.wizard_state: Dict[str, bool] = {
            "directory_set": False,
            "dependencies_ready": False,
            "project_analyzed": False,
            "automation_ready": False,
            "setup_complete": False
        }
        self.settings: Dict[str, Any] = {
            "ahk_exe_path": self.find_initial_ahk_executable()
        }
        self.load_settings()

    def set_working_dir(self, path: str):
        self.working_dir = path
        self.wizard_state["directory_set"] = True

    def reset_wizard_state(self):
        self.wizard_state = {
            "directory_set": False,
            "dependencies_ready": False,
            "project_analyzed": False,
            "automation_ready": False,
            "setup_complete": False
        }
        self.session_goal = {
            "plan_path": None,
            "tasks": [],
            "current_task_index": -1
        }

    def find_initial_ahk_executable(self) -> str:
        """
        Checks for a valid AutoHotkey v2 installation in common directories.
        This is used for initial setup or if no config file is found.
        Returns the path if found, otherwise a default.
        """
        ahk_paths = [
            r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe",
            r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        ]
        for path in ahk_paths:
            if os.path.exists(path):
                return path
        # As a fallback, check if AutoHotkey is in the system's PATH via 'where'
        try:
            result = subprocess.run(["where", "AutoHotkey.exe"], check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # where can return multiple paths, take the first one
            first_path = result.stdout.strip().splitlines()[0]
            return first_path
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
            # Default if not found anywhere, user must configure it.
            return "AutoHotkey.exe"

    def save_settings(self) -> None:
        """Saves the current settings to the config file."""
        config_path = os.path.join(self.working_dir, CONFIG_FILE)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            print(f"Settings saved to {config_path}")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_settings(self) -> None:
        """Loads settings from the config file if it exists."""
        config_path = os.path.join(self.working_dir, CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Update settings, but don't add new keys from the file
                    for key in self.settings:
                        if key in loaded_settings:
                            self.settings[key] = loaded_settings[key]
                    print(f"Settings loaded from {config_path}")
            except Exception as e:
                print(f"Error loading settings from {config_path}: {e}")

# Initialize state with the determined working directory
app_state = AppState(get_working_dir()) 