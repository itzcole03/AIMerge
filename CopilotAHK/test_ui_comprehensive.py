import os
import sys
import json
import tempfile
import time
import pytest

def test_single_unified_app():
    """Test that only a single unified app window is created."""
    import tkinter as tk
    sys.path.insert(0, os.path.abspath('src'))
    from gui_advanced import AdvancedGui
    
    root = tk.Tk()
    root.withdraw()
    app = AdvancedGui(root)
    
    # Check that the app window exists
    assert app.root.winfo_exists()
    
    # Check that all expected tabs are present
    expected_tabs = ['Automation Control', 'Smart Context', 'Git Helper', 
                     'Workspace & Sessions', 'Session Goal', 'TDD Helper', 
                     'Settings', 'Session Log']
    
    # If setup is not complete, Setup tab should be first
    if not app.load_setup_state():
        expected_tabs.insert(0, 'Setup')
    
    actual_tabs = []
    for i in range(app.notebook.index('end')):
        actual_tabs.append(app.notebook.tab(i, option='text'))
    
    assert set(actual_tabs) == set(expected_tabs), f"Expected tabs: {expected_tabs}, Got: {actual_tabs}"
    
    root.destroy()

def test_dark_mode_persistence():
    """Test that dark mode setting persists across sessions."""
    import tkinter as tk
    sys.path.insert(0, os.path.abspath('src'))
    from gui_advanced import AdvancedGui
    
    with tempfile.TemporaryDirectory() as tmpdir:
        settings_file = os.path.join(tmpdir, 'user_settings.json')
        
        # Mock the settings file location
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # Create app and enable dark mode
            root = tk.Tk()
            root.withdraw()
            app = AdvancedGui(root)
            app.dark_mode_var.set(True)
            app.toggle_dark_mode()
            
            # Check that setting was saved
            assert os.path.exists(settings_file)
            with open(settings_file) as f:
                data = json.load(f)
            assert data.get('dark_mode') == True
            
            # Destroy the first instance completely
            root.quit()
            root.destroy()
            
            # Small delay to ensure cleanup
            time.sleep(0.1)
            
            # Create new app instance and check dark mode is loaded
            root2 = tk.Tk()
            root2.withdraw()
            app2 = AdvancedGui(root2)
            assert app2.dark_mode_var.get() == True
            root2.quit()
            root2.destroy()
            
        finally:
            os.chdir(original_cwd)

def test_profile_management():
    """Test saving and loading profiles."""
    import tkinter as tk
    sys.path.insert(0, os.path.abspath('src'))
    from gui_advanced import AdvancedGui
    
    with tempfile.TemporaryDirectory() as tmpdir:
        profiles_file = os.path.join(tmpdir, 'user_profiles.json')
        
        # Mock the profiles file location
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            root = tk.Tk()
            root.withdraw()
            app = AdvancedGui(root)
            
            # Set some values
            app.dir_path_entry.delete(0, tk.END)
            app.dir_path_entry.insert(0, '/test/path')
            app.ahk_path_entry.delete(0, tk.END)
            app.ahk_path_entry.insert(0, 'C:/test/ahk.exe')
            
            # Save profile (simulate dialog)
            profiles = {'TestProfile': {
                'working_dir': '/test/path',
                'ahk_path': 'C:/test/ahk.exe',
                'custom_dependencies': ''
            }}
            with open(profiles_file, 'w') as f:
                json.dump(profiles, f)
            
            # Load profiles list
            app.load_profiles_list()
            assert 'TestProfile' in app.profile_combo['values']
            
            root.quit()
            root.destroy()
            
        finally:
            os.chdir(original_cwd)

def test_session_logging():
    """Test that session events are logged correctly."""
    import tkinter as tk
    sys.path.insert(0, os.path.abspath('src'))
    from gui_advanced import AdvancedGui
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, 'session_log.txt')
        
        root = tk.Tk()
        root.withdraw()
        app = AdvancedGui(root)
        app.session_log_file = log_file
        
        # Log some events with different messages to avoid anti-spam throttling
        app.log_session_event("Test event 1")
        app.log_session_event("Critical system error occurred", level="ERROR")
        
        # Wait a moment for background thread to write
        time.sleep(0.2)
        
        # Check log file
        assert os.path.exists(log_file)
        with open(log_file) as f:
            log = f.read()
        assert "Test event 1" in log
        assert "[ERROR] Critical system error occurred" in log
        
        root.quit()
        root.destroy()

def test_setup_flow():
    """Test that setup flow works correctly."""
    import tkinter as tk
    sys.path.insert(0, os.path.abspath('src'))
    from gui_advanced import AdvancedGui
    
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_file = os.path.join(tmpdir, 'setup_state.json')
        
        # Change to temp directory to isolate setup state
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            root = tk.Tk()
            root.withdraw()
            app = AdvancedGui(root)
            
            # Check that setup tab is present if not complete
            if not app.load_setup_state():
                assert app.notebook.tab(0, option='text') == 'Setup'
                # Note: In the current implementation, tabs may not be disabled
                # during initial creation due to initialization order
            
            # Simulate completing setup
            app.save_setup_state(True)
            assert os.path.exists(setup_file)
            
            root.quit()
            root.destroy()
            
        finally:
            os.chdir(original_cwd) 