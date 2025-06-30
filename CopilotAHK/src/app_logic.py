"""
app_logic.py
Core, non-GUI logic for the AI Pair Programming Assistant application.
This includes dependency management, script execution, and project analysis.
"""

import os
import subprocess
import sys
import re
from typing import List, Tuple, Callable
import queue
import threading
import psutil
import time

from config import app_state, AHK_SCRIPT, SUMMARY_FILE, GITINGEST_SCRIPT, CONTEXT_DIR
from utils import verify_dependencies_subprocess, run_subprocess_with_output

# AHK log file constant
AHK_LOG_FILE = "ahk_log.txt"

def verify_dependencies_subprocess() -> tuple[bool, list[str]]:
    """
    Verify dependencies using subprocess to avoid import caching issues.
    Returns (success, missing_packages).
    """
    required_packages = [
        'tkinter', 'threading', 'subprocess', 'os', 'json', 'datetime',
        'pyautogui', 'PIL', 'gitingest', 'watchdog', 'plyer', 'pystray'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            # Use subprocess to check if package can be imported
            result = subprocess.run([
                sys.executable, '-c', f'import {package}'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                missing.append(package)
        except (subprocess.TimeoutExpired, Exception):
            missing.append(package)
    
    return len(missing) == 0, missing

def check_autohotkey() -> bool:
    """
    Simple AutoHotkey installation checker.
    Returns True if AutoHotkey v2 is found, False otherwise.
    """
    import subprocess
    import os
    
    # Common AutoHotkey v2 installation paths
    common_paths = [
        r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe"
    ]
    
    # Check common installation paths first
    for path in common_paths:
        if os.path.isfile(path):
            return True
    
    # Check if AutoHotkey is in PATH
    try:
        result = subprocess.run(
            ['where', 'autohotkey'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    # Alternative check for 'ahk' command
    try:
        result = subprocess.run(
            ['where', 'ahk'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return False

def check_ahk_running() -> bool:
    """Checks if the AHK script process is currently running."""
    # A simple check based on process name. This might need to be made more robust.
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            # Check if 'AutoHotkey' is in the process name and our script is in the command line
            if 'autohotkey' in proc.info['name'].lower() and AHK_SCRIPT in ' '.join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def start_ahk(progress_callback: Callable[[str], None]):
    """
    Starts the AutoHotkey script using the configured AHK executable.
    """
    if check_ahk_running():
        progress_callback("AHK script is already running.")
        return

    progress_callback("Attempting to start AHK script...")
    ahk_exe_path = app_state.settings.get("ahk_exe_path")
    if not ahk_exe_path or not check_autohotkey():
        progress_callback(f"❌ AutoHotkey not found or path is invalid: '{ahk_exe_path}'.")
        progress_callback("   Please configure the correct path in the Settings tab.")
        return

    script_path = os.path.join(app_state.working_dir, AHK_SCRIPT)
    if not os.path.exists(script_path):
        progress_callback(f"❌ AHK script not found at {script_path}")
        return

    try:
        subprocess.Popen([ahk_exe_path, script_path], cwd=app_state.working_dir)
        progress_callback(f"✅ AHK script '{AHK_SCRIPT}' started.")
        app_state.automation_state['ahk_running'] = True
    except Exception as e:
        progress_callback(f"❌ Failed to start AHK script: {e}")
        app_state.automation_state['ahk_running'] = False

def monitor_ahk_log(progress_callback: Callable[[str], None], stop_event: threading.Event) -> None:
    """
    Monitors the AHK log file for new entries and sends them to the callback.
    """
    log_path = os.path.join(app_state.working_dir, AHK_LOG_FILE)
    progress_callback(f"[AHK Monitor] Started for {log_path}")

    # Ensure log file exists before we start
    if not os.path.exists(log_path):
        # Create it if AHK hasn't yet
        try:
            open(log_path, 'a').close()
        except IOError as e:
            progress_callback(f"[AHK Monitor] Error creating log file: {e}")
            return

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            f.seek(0, 2)  # Go to the end of the file
            while not stop_event.is_set():
                line = f.readline()
                if not line:
                    time.sleep(0.5)  # Wait for new lines
                    continue
                progress_callback(f"[AHK] {line.strip()}")
    except Exception as e:
        progress_callback(f"[AHK Monitor] Error reading log file: {e}")
    
    progress_callback("[AHK Monitor] Stopped.")

def stop_ahk(progress_callback: Callable[[str], None]):
    """
    Stops the AutoHotkey script process.
    """
    progress_callback("Attempting to stop AHK script...")
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if 'autohotkey' in proc.info['name'].lower() and AHK_SCRIPT in ' '.join(proc.info['cmdline']):
                proc.terminate()
                progress_callback(f"✅ AHK script process terminated.")
                app_state.automation_state['ahk_running'] = False
                return
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    progress_callback("AHK script process not found or already stopped.")
    app_state.automation_state['ahk_running'] = False

def find_ahk_executable() -> str:
    """DEPRECATED: Use app_state.settings['ahk_exe_path'] instead."""
    return app_state.settings.get("ahk_exe_path", "AutoHotkey.exe")

def install_dependencies(progress_callback: Callable[[str], None]):
    """
    Installs missing Python packages from a requirements.txt file.
    Creates requirements.txt if it doesn't exist.
    """
    requirements_file = os.path.join(app_state.working_dir, "requirements.txt")
    if not os.path.exists(requirements_file):
        progress_callback("requirements.txt not found. Creating one...")
        requirements_content = "pyautogui>=0.9.54\nPillow>=10.0.0\ngitingest"
        with open(requirements_file, 'w') as f:
            f.write(requirements_content)
        progress_callback("requirements.txt created.")

    progress_callback("Installing dependencies from requirements.txt...")
    cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_file, "--upgrade"]
    
    output_queue = queue.Queue()
    thread = threading.Thread(
        target=run_subprocess_with_output, 
        args=(cmd, app_state.working_dir, 300, output_queue),
        daemon=True
    )
    thread.start()

    while thread.is_alive() or not output_queue.empty():
        try:
            message_type, data = output_queue.get(timeout=0.1)
            if message_type == "stdout":
                progress_callback(f"  {data.strip()}")
            elif message_type == "done":
                if data == 0:
                    progress_callback("✓ Package installation completed successfully.")
                    return True
                else:
                    progress_callback("❌ Package installation failed.")
                    return False
        except queue.Empty:
            continue
    return False

def check_and_install_dependencies(progress_callback: Callable[[str], None]) -> bool:
    """
    Checks for dependencies and installs them if missing.
    Uses callbacks to update the UI with progress.
    """
    progress_callback("🔍 Checking for required Python packages...")
    success, missing = verify_dependencies_subprocess()
    
    if success:
        progress_callback("✅ All required packages are already installed.")
        app_state.wizard_state['dependencies_ready'] = True
        return True
    
    progress_callback(f"⚠️ Missing packages found: {', '.join(missing)}")
    return install_dependencies(progress_callback)

def run_gitingest(progress_callback: Callable[[str], None]) -> bool:
    """
    Runs gitingest to analyze the project and create a summary file.
    """
    progress_callback("📊 Starting project analysis...")
    try:
        from gitingest import ingest
        
        progress_callback("   - Scanning project structure...")
        summary, tree, content = ingest(app_state.working_dir)
        
        progress_callback("   - Creating AI context file...")
        summary_path = os.path.join(app_state.working_dir, SUMMARY_FILE)
        
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"{summary}\n\n{tree}\n\n{content}")
            
        if os.path.exists(summary_path):
            file_size = os.path.getsize(summary_path)
            lines = content.count('\\n') + summary.count('\\n') + tree.count('\\n')
            progress_callback(f"✅ Analysis complete!")
            progress_callback(f"   - Generated: {SUMMARY_FILE}")
            progress_callback(f"   - File size: {file_size:,} bytes, Lines: {lines:,}")
            app_state.wizard_state["project_analyzed"] = True
            return True
        else:
            raise Exception("Failed to create summary file.")
            
    except ImportError:
        progress_callback("❌ gitingest module not found.")
        progress_callback("   Please ensure it was installed correctly.")
        return False
    except Exception as e:
        progress_callback(f"❌ Analysis error: {e}")
        return False

def generate_smart_context(focus_keywords: List[str], file_patterns: List[str], max_lines: int) -> Tuple[bool, str]:
    """
    Generates a focused context from the main gitingest summary using regex.
    """
    summary_path = os.path.join(app_state.working_dir, SUMMARY_FILE)
    if not os.path.exists(summary_path):
        return False, "Summary file not found. Please run a full project analysis first."

    with open(summary_path, 'r', encoding='utf-8') as f:
        full_content = f.read()

    # If no criteria, return a truncated version of the full content
    if not any(focus_keywords) and not any(file_patterns):
        # A simple truncation based on lines
        return True, "\n".join(full_content.splitlines()[:max_lines])

    context_content = f"Focused Context | Keywords: {focus_keywords} | Patterns: {file_patterns}\n\n"
    
    # Compile regex for keywords and patterns for efficiency
    try:
        # Filter out empty strings before compiling regex
        keyword_regex = re.compile('|'.join(filter(None, focus_keywords)), re.IGNORECASE) if any(focus_keywords) else None
        # Convert file glob patterns to regex
        pattern_regex_str = '|'.join(re.escape(p).replace(r'\*', '.*').replace(r'\?', '.') for p in filter(None, file_patterns))
        pattern_regex = re.compile(pattern_regex_str) if pattern_regex_str else None
    except re.error as e:
        return False, f"Invalid regex in keywords or patterns: {e}"

    # Extract relevant file content
    current_file = None
    collecting = False
    
    # Split content by file sections
    file_sections = re.split(r'(^### File: `.*`\n)', full_content, flags=re.MULTILINE)
    
    # The first element is anything before the first file, which we can include
    context_content += file_sections[0]
    
    # Process pairs of (file_header, file_content)
    for i in range(1, len(file_sections), 2):
        header = file_sections[i]
        content = file_sections[i+1]
        
        # Extract file path from header: ### File: `path/to/file.py`
        match = re.search(r'`(.*?)`', header)
        if not match:
            continue
        current_file = match.group(1)

        file_matches = pattern_regex and pattern_regex.search(current_file)
        
        # If the file path matches the patterns, include the whole file
        if file_matches:
            context_content += header + content
            continue

        # If no keyword regex, we only match by file pattern, so skip if no match
        if not keyword_regex:
            continue
            
        # Otherwise, search for keywords within the file content
        relevant_lines = [line for line in content.splitlines() if keyword_regex.search(line)]
        
        if relevant_lines:
            context_content += header + "\n".join(relevant_lines) + "\n\n"

    # Limit the context length
    context_lines = context_content.splitlines()
    if len(context_lines) > max_lines:
        context_content = "\n".join(context_lines[:max_lines])
        context_content += f"\n\n... (context truncated at {max_lines} lines) ..."

    return True, context_content

def save_context(context_content: str, filename: str) -> Tuple[bool, str]:
    """
    Saves the provided context content to a file.
    """
    if not filename.endswith('.md'):
        filename += '.md'
    
    save_path = os.path.join(app_state.working_dir, filename)
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(context_content)
        return True, f"Context saved successfully to {save_path}"
    except Exception as e:
        return False, f"Error saving context: {e}"

# --- Git Helper Functions ---

def git_status() -> Tuple[bool, str]:
    """
    Gets the git status of the project repository.
    """
    if not os.path.isdir(os.path.join(app_state.working_dir, '.git')):
        return False, "This is not a Git repository."
    
    try:
        result = subprocess.run(
            ["git", "status"],
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except FileNotFoundError:
        return False, "Git not found. Please ensure Git is installed and in your system's PATH."
    except subprocess.CalledProcessError as e:
        return False, f"Error getting Git status:\n{e.stderr}"

def git_add_all() -> Tuple[bool, str]:
    """
    Stages all changes in the repository.
    """
    try:
        result = subprocess.run(
            ["git", "add", "."],
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return True, "All changes staged successfully."
    except Exception as e:
        return False, f"Error staging changes: {e}"

def git_commit(message: str) -> Tuple[bool, str]:
    """
    Commits the staged changes with a given message.
    """
    try:
        # Use --quiet to reduce output unless there's an error
        result = subprocess.run(
            ["git", "commit", "-m", message, "--quiet"],
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # On success, git commit --quiet produces no stdout. We provide our own success message.
        return True, f"Commit successful:\n{result.stdout or 'Changes committed.'}"
    except subprocess.CalledProcessError as e:
        return False, f"Error committing changes: {e.stderr}"
    except Exception as e:
        return False, f"An unexpected error occurred during commit: {e}"

def git_push() -> Tuple[bool, str]:
    """
    Pushes committed changes to the remote repository.
    """
    try:
        result = subprocess.run(
            ["git", "push"],
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, f"Push successful:\n{result.stderr or result.stdout}"
    except subprocess.CalledProcessError as e:
        return False, f"Error pushing changes: {e.stderr}"
    except Exception as e:
        return False, f"An unexpected error occurred during push: {e}"

def git_pull() -> Tuple[bool, str]:
    """
    Pulls changes from the remote repository.
    """
    try:
        result = subprocess.run(
            ["git", "pull"],
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, f"Pull successful:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return False, f"Error pulling changes: {e.stderr}"
    except Exception as e:
        return False, f"An unexpected error occurred during pull: {e}"

def run_python_test_file(test_file_path: str) -> Tuple[bool, str]:
    """
    Runs a Python test file using pytest and captures the output.
    Returns a tuple of (success, output).
    """
    # Ensure the file path is absolute
    if not os.path.isabs(test_file_path):
        test_file_path = os.path.join(app_state.working_dir, test_file_path)

    if not os.path.exists(test_file_path):
        return False, f"Test file not found: {test_file_path}"
    
    # We use pytest to run tests. It's a common dependency for testing.
    # The command will be `python -m pytest <file>`
    cmd = [sys.executable, "-m", "pytest", test_file_path]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            timeout=120 # 2 minute timeout for tests
        )
        # Pytest exit codes: 0 = all tests passed, 1 = tests failed, >1 = other errors
        success = result.returncode == 0
        output = result.stdout + "\n" + result.stderr
        return success, output
        
    except FileNotFoundError:
        # This could happen if python/pytest is not in PATH, though unlikely
        return False, "Error: `pytest` not found. Please ensure it is installed (`pip install pytest`)."
    except subprocess.TimeoutExpired:
        return False, "Error: Test run timed out after 120 seconds."
    except Exception as e:
        return False, f"An unexpected error occurred while running tests: {e}"

def parse_implementation_plan(plan_content: str) -> List[str]:
    """
    Parses a markdown string for unchecked checklist items.
    Returns a list of task strings.
    """
    tasks = []
    # Regex to find lines starting with '- [ ]' and capture the text after it
    task_regex = re.compile(r'^\s*-\s*\[\s*\]\s+(.*)', re.MULTILINE)
    
    found_tasks = task_regex.findall(plan_content)
    
    for task in found_tasks:
        tasks.append(task.strip())
        
    return tasks

def get_current_branch() -> Tuple[bool, str]:
    """Gets the current active Git branch."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, result.stdout.strip()
    except Exception as e:
        return False, f"Could not get current branch: {e}"

def list_branches() -> Tuple[bool, List[str]]:
    """Lists all local Git branches."""
    try:
        result = subprocess.run(
            ["git", "branch"],
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        branches = [b.strip().lstrip('* ') for b in result.stdout.splitlines()]
        return True, branches
    except Exception as e:
        return False, [f"Could not list branches: {e}"]

def create_branch(branch_name: str) -> Tuple[bool, str]:
    """Creates and switches to a new Git branch."""
    try:
        # First, ensure the branch name is valid
        if not re.match(r'^[a-zA-Z0-9_-]+$', branch_name):
             return False, "Invalid branch name. Use only letters, numbers, underscores, and hyphens."
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, result.stderr or result.stdout # checkout -b outputs to stderr
    except subprocess.CalledProcessError as e:
        return False, f"Error creating branch (it may already exist):\n{e.stderr}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"

def switch_branch(branch_name: str) -> Tuple[bool, str]:
    """Switches to an existing Git branch."""
    try:
        result = subprocess.run(
            ["git", "checkout", branch_name],
            cwd=app_state.working_dir,
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, result.stderr or result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error switching branch:\n{e.stderr}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}" 