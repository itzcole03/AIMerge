"""
utils.py
Utility functions for the AI Pair Programming Assistant application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Tuple, List, Any, Union
import queue
import subprocess
import sys
import os
import time
import zipfile
from datetime import datetime

def create_output_window(
    title: str, parent: Optional[tk.Widget] = None
) -> Tuple[tk.Toplevel, Any, tk.Label, tk.Button]:
    """Creates a standardized window for displaying command output."""
    if parent:
        window = tk.Toplevel(parent)
    else:
        window = tk.Toplevel()
        
    window.title(title)
    window.geometry("700x500")

    status_label = tk.Label(window, text="Starting...", anchor="w", justify="left")
    status_label.pack(side="top", fill="x", padx=10, pady=5)

    output_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, height=20)
    output_text.pack(expand=True, fill="both", padx=10, pady=5)
    output_text.configure(state="disabled")

    close_button = ttk.Button(window, text="Close", command=window.destroy)
    close_button.pack(side="bottom", pady=10)
    
    return window, output_text, status_label, close_button


def run_subprocess_with_output(
    cmd: List[str], 
    cwd: str, 
    timeout: int, 
    output_queue: queue.Queue[Tuple[str, Union[str, int]]]
) -> None:
    """
    Runs a subprocess and streams its output to a queue.
    'output_queue' will receive tuples of ('stdout', line) or ('done', return_code).
    """
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=cwd
        )

        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                output_queue.put(("stdout", line))
        
        process.wait(timeout=timeout)
        output_queue.put(("done", process.returncode))

    except FileNotFoundError as e:
        output_queue.put(("stdout", f"Error: Command not found - {e}\n"))
        output_queue.put(("done", 1))
    except subprocess.TimeoutExpired:
        output_queue.put(("stdout", "Error: Process timed out.\n"))
        process.kill()
        output_queue.put(("done", 1))
    except Exception as e:
        output_queue.put(("stdout", f"An unexpected error occurred: {e}\n"))
        output_queue.put(("done", 1))


def verify_dependencies_subprocess() -> Tuple[bool, List[str]]:
    """
    Verifies if required Python packages are installed using a subprocess.
    This avoids issues with cached imports in the main application process.
    """
    required_packages = ["pyautogui", "Pillow", "gitingest"]
    missing_packages = []
    
    for package in required_packages:
        try:
            # Use sys.executable to ensure we're checking the same Python environment
            subprocess.check_call(
                [sys.executable, "-m", "importlib.util", "-c", f"importlib.util.find_spec('{package}')"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            # This means find_spec returned a non-zero exit code (package not found)
            missing_packages.append(package)
            
    return not missing_packages, missing_packages 

def run_auto_tests(project_dir: str, log_file: str = None) -> tuple[bool, str]:
    """
    Runs pytest in the given project directory. Optionally logs output to log_file.
    Returns (success, output).
    """
    result = subprocess.run([
        'python', '-m', 'pytest', '--maxfail=5', '--disable-warnings', '-v', '--tb=short', '--ignore=test_wizard_navigation.py'
    ], capture_output=True, text=True, cwd=project_dir)
    output = result.stdout
    if log_file:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Auto-test-on-save triggered.\n")
            f.write(output + '\n')
    return (result.returncode == 0, output) 

def create_bug_report_zip(files: list[str], output_dir: str) -> str:
    """
    Packages the given files into a zip archive in output_dir.
    Returns the path to the created zip file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_path = os.path.join(output_dir, f'bug_report_{timestamp}.zip')
    with zipfile.ZipFile(zip_path, 'w') as z:
        for f in files:
            if os.path.exists(f):
                z.write(f, arcname=os.path.basename(f))
    return zip_path 