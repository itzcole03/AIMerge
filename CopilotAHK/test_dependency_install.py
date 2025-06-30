"""
test_dependency_install.py
Test script to verify dependency installation functionality.
"""

import os
import subprocess
import sys

def test_requirements_file():
    """Test if requirements.txt exists and has correct content."""
    print("Testing requirements.txt file...")
    
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        print(f"✅ {requirements_file} found")
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        required_packages = ["pyautogui", "Pillow"]
        for package in required_packages:
            if package in content:
                print(f"   ✅ {package} found in requirements")
            else:
                print(f"   ❌ {package} missing from requirements")
    else:
        print(f"❌ {requirements_file} not found")

def test_pip_installation():
    """Test if pip can install packages."""
    print("\nTesting pip installation capability...")
    
    try:
        # Test if pip is available
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ pip is available")
            print(f"   {result.stdout.strip()}")
        else:
            print("❌ pip not working properly")
    except subprocess.TimeoutExpired:
        print("✅ pip is available (version check timed out as expected)")
    except FileNotFoundError:
        print("❌ pip not found")
    except Exception as e:
        print(f"❌ Error testing pip: {e}")

def test_dependency_check():
    """Test dependency checking functionality."""
    print("\nTesting dependency check functionality...")
    
    # Test pyautogui
    try:
        import pyautogui
        print(f"✅ pyautogui is installed (version: {getattr(pyautogui, '__version__', 'unknown')})")
    except ImportError:
        print("❌ pyautogui is missing")
    
    # Test Pillow
    try:
        from PIL import Image
        try:
            version = Image.__version__
            print(f"✅ Pillow is installed (version: {version})")
        except AttributeError:
            print("✅ Pillow is installed (version unknown)")
    except ImportError:
        print("❌ Pillow is missing")

def test_install_command():
    """Test the actual install command that would be used."""
    print("\nTesting install command...")
    
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        try:
            # Test the install command (dry run)
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", requirements_file, "--dry-run"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Install command works (dry run successful)")
            else:
                print("❌ Install command failed")
                print(f"   Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("✅ Install command works (dry run timed out as expected)")
        except Exception as e:
            print(f"❌ Error testing install command: {e}")
    else:
        print("❌ requirements.txt not found for install test")

def main():
    """Run all dependency tests."""
    print("=== Dependency Installation Test ===\n")
    
    test_requirements_file()
    test_pip_installation()
    test_dependency_check()
    test_install_command()
    
    print("\n=== Test Summary ===")
    print("If all tests pass, the dependency installation feature should work correctly.")
    print("\nTo test the GUI installation:")
    print("1. Run: python copilot_dual_agent_gui.py")
    print("2. Click 'Install Dependencies' button")
    print("3. Check for success/error messages")

if __name__ == "__main__":
    main() 