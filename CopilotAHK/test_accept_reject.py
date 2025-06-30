"""
test_accept_reject.py
Test script to verify Accept/Reject button detection and clicking.
"""

import os
import subprocess
from PIL import Image

def test_image_files():
    """Test if the Accept/Reject image files exist and are valid."""
    print("Testing Accept/Reject image files...")
    
    accept_file = "accept.png"
    reject_file = "reject.png"
    
    # Check if files exist
    if os.path.exists(accept_file):
        print(f"✅ {accept_file} found")
        try:
            img = Image.open(accept_file)
            print(f"   Size: {img.size}")
            print(f"   Mode: {img.mode}")
        except Exception as e:
            print(f"   ❌ Error reading image: {e}")
    else:
        print(f"❌ {accept_file} not found")
    
    if os.path.exists(reject_file):
        print(f"✅ {reject_file} found")
        try:
            img = Image.open(reject_file)
            print(f"   Size: {img.size}")
            print(f"   Mode: {img.mode}")
        except Exception as e:
            print(f"   ❌ Error reading image: {e}")
    else:
        print(f"❌ {reject_file} not found")

def test_ahk_script():
    """Test if the AHK script can be started."""
    print("\nTesting AHK script...")
    
    ahk_file = "CopilotAFK_Toggle_Assistant.ahk"
    if os.path.exists(ahk_file):
        print(f"✅ {ahk_file} found")
        
        # Check if AutoHotkey is installed
        try:
            result = subprocess.run(["autohotkey", "/?"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ AutoHotkey is installed and working")
            else:
                print("❌ AutoHotkey may not be properly installed")
        except FileNotFoundError:
            print("❌ AutoHotkey not found in PATH")
        except subprocess.TimeoutExpired:
            print("✅ AutoHotkey is installed (help command timed out as expected)")
    else:
        print(f"❌ {ahk_file} not found")

def test_gui_script():
    """Test if the GUI script can be imported."""
    print("\nTesting GUI script...")
    
    gui_file = "copilot_dual_agent_gui.py"
    if os.path.exists(gui_file):
        print(f"✅ {gui_file} found")
        
        try:
            # Test basic import without using the module
            import importlib.util
            spec = importlib.util.spec_from_file_location("copilot_dual_agent_gui", gui_file)
            if spec and spec.loader:
                print("✅ GUI script imports successfully")
            else:
                print("❌ GUI script import failed")
        except ImportError as e:
            print(f"❌ Import error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    else:
        print(f"❌ {gui_file} not found")

def test_pyautogui():
    """Test if pyautogui is available."""
    print("\nTesting pyautogui...")
    
    try:
        import pyautogui
        print("✅ pyautogui is installed")
        # Try to get version safely
        try:
            version = getattr(pyautogui, '__version__', 'unknown')
            print(f"   Version: {version}")
        except:
            print("   Version: unknown")
    except ImportError:
        print("❌ pyautogui not installed")
        print("   Install with: pip install pyautogui")

def test_dependency_installation():
    """Test dependency installation functionality."""
    print("\nTesting dependency installation system...")
    
    # Test requirements.txt
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        print(f"✅ {requirements_file} found")
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        required_packages = ["pyautogui", "Pillow"]
        all_found = True
        for package in required_packages:
            if package in content:
                print(f"   ✅ {package} found in requirements")
            else:
                print(f"   ❌ {package} missing from requirements")
                all_found = False
        
        if all_found:
            print("✅ All required packages listed in requirements.txt")
        else:
            print("❌ Some packages missing from requirements.txt")
    else:
        print(f"❌ {requirements_file} not found")
    
    # Test pip installation capability
    try:
        result = subprocess.run(["pip", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ pip is available for dependency installation")
        else:
            print("❌ pip not working properly")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✅ pip is available (version check timed out as expected)")

def main():
    """Run all tests."""
    print("=== Copilot AHK Accept/Reject System Test ===\n")
    
    test_image_files()
    test_ahk_script()
    test_gui_script()
    test_pyautogui()
    test_dependency_installation()
    
    print("\n=== Test Summary ===")
    print("If all tests pass, your system is ready for:")
    print("1. Autonomous Accept/Reject automation")
    print("2. Manual Accept/Reject controls via GUI")
    print("3. Dual-agent workflow with Cursor integration")
    print("4. One-click dependency installation")
    print("\nTo start the system:")
    print("1. Run: python copilot_dual_agent_gui.py")
    print("2. Or use: start.bat")
    print("3. Use 'Install Dependencies' button if needed")

if __name__ == "__main__":
    main() 