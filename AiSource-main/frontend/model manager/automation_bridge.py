#!/usr/bin/env python3
"""
Automation Bridge
Bridges the CopilotAHK automation capabilities with the unified platform
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add CopilotAHK to path if available
copilot_ahk_path = Path(__file__).parent.parent.parent / "CopilotAHK"
if copilot_ahk_path.exists():
    sys.path.append(str(copilot_ahk_path / "src"))

logger = logging.getLogger(__name__)

class AutomationBridge:
    """Bridge between unified platform and CopilotAHK"""
    
    def __init__(self):
        self.ahk_process = None
        self.working_dir = None
        self.automation_available = False
        self.settings = {
            "autonomousMode": False,
            "acceptRate": 85,
            "supervisorRate": 70,
            "cycleTime": 180,
            "hotkeysEnabled": True
        }
        
        # Try to import CopilotAHK components
        try:
            from app_logic import check_autohotkey, run_gitingest
            from config import app_state
            self.check_autohotkey = check_autohotkey
            self.run_gitingest = run_gitingest
            self.app_state = app_state
            self.automation_available = True
            logger.info("CopilotAHK integration available")
        except ImportError as e:
            logger.warning(f"CopilotAHK integration not available: {e}")
    
    def is_available(self) -> bool:
        """Check if automation is available"""
        return self.automation_available and self.check_autohotkey() if hasattr(self, 'check_autohotkey') else False
    
    def set_working_directory(self, path: str) -> bool:
        """Set the working directory for project analysis"""
        try:
            if os.path.exists(path):
                self.working_dir = path
                if hasattr(self, 'app_state'):
                    self.app_state.working_dir = path
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to set working directory: {e}")
            return False
    
    def generate_project_summary(self, progress_callback=None) -> Dict[str, Any]:
        """Generate project summary using GitIngest"""
        if not self.automation_available or not hasattr(self, 'run_gitingest'):
            return {"success": False, "error": "GitIngest not available"}
        
        try:
            if not self.working_dir:
                return {"success": False, "error": "No working directory set"}
            
            # Use the GitIngest functionality from CopilotAHK
            success, message = self.run_gitingest(progress_callback)
            
            if success:
                # Check if summary file was created
                summary_file = os.path.join(self.working_dir, "gitingest_summary.txt")
                if os.path.exists(summary_file):
                    file_size = os.path.getsize(summary_file)
                    return {
                        "success": True,
                        "message": message,
                        "summary_file": summary_file,
                        "file_size": file_size
                    }
            
            return {"success": False, "error": message}
            
        except Exception as e:
            logger.error(f"Failed to generate project summary: {e}")
            return {"success": False, "error": str(e)}
    
    def start_automation(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Start the AutoHotkey automation"""
        try:
            if not self.is_available():
                return {"success": False, "error": "Automation not available"}
            
            self.settings.update(settings)
            
            # Find and start the AutoHotkey script
            ahk_script = copilot_ahk_path / "CopilotAFK_Toggle_Assistant.ahk"
            if not ahk_script.exists():
                return {"success": False, "error": "AutoHotkey script not found"}
            
            # Start the AHK process
            self.ahk_process = subprocess.Popen(
                ["autohotkey.exe", str(ahk_script)],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            logger.info("AutoHotkey automation started")
            return {"success": True, "message": "Automation started", "pid": self.ahk_process.pid}
            
        except Exception as e:
            logger.error(f"Failed to start automation: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_automation(self) -> Dict[str, Any]:
        """Stop the AutoHotkey automation"""
        try:
            if self.ahk_process:
                self.ahk_process.terminate()
                self.ahk_process.wait(timeout=5)
                self.ahk_process = None
                logger.info("AutoHotkey automation stopped")
            
            return {"success": True, "message": "Automation stopped"}
            
        except Exception as e:
            logger.error(f"Failed to stop automation: {e}")
            return {"success": False, "error": str(e)}
    
    def is_running(self) -> bool:
        """Check if automation is currently running"""
        if self.ahk_process:
            return self.ahk_process.poll() is None
        return False
    
    def trigger_accept(self) -> Dict[str, Any]:
        """Trigger manual accept"""
        try:
            # Try to use pyautogui if available
            import pyautogui
            pyautogui.press('f6')
            return {"success": True, "action": "accept"}
        except ImportError:
            return {"success": False, "error": "pyautogui not available"}
        except Exception as e:
            logger.error(f"Failed to trigger accept: {e}")
            return {"success": False, "error": str(e)}
    
    def trigger_reject(self) -> Dict[str, Any]:
        """Trigger manual reject"""
        try:
            # Try to use pyautogui if available
            import pyautogui
            pyautogui.press('f7')
            return {"success": True, "action": "reject"}
        except ImportError:
            return {"success": False, "error": "pyautogui not available"}
        except Exception as e:
            logger.error(f"Failed to trigger reject: {e}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current automation status"""
        return {
            "available": self.is_available(),
            "running": self.is_running(),
            "settings": self.settings,
            "working_dir": self.working_dir,
            "ahk_available": hasattr(self, 'check_autohotkey') and self.check_autohotkey() if hasattr(self, 'check_autohotkey') else False
        }

# Global automation bridge instance
automation_bridge = AutomationBridge()

def get_automation_bridge() -> AutomationBridge:
    """Get the global automation bridge instance"""
    return automation_bridge
