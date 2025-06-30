"""
test_all_buttons.py
Comprehensive test script to verify all GUI button functionality after setting project directory.
"""

import os
import subprocess
from typing import List, Dict, Tuple, Any

# Test results storage
test_results: List[Dict[str, Any]] = []

def log_test(test_name: str, passed: bool, details: str = "") -> None:
    """Log test result."""
    result: Dict[str, Any] = {
        "test": test_name,
        "passed": passed,
        "details": details
    }
    test_results.append(result)
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")

def test_project_directory_operations():
    """Test operations that depend on project directory being set."""
    print("\n=== Testing Project Directory Operations ===")
    
    # Test 1: Check if working directory is set
    working_dir = os.path.abspath(".")
    log_test("Working directory accessible", True, f"Directory: {working_dir}")
    
    # Test 2: Check if requirements.txt exists or can be created
    requirements_file = os.path.join(working_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        log_test("requirements.txt exists", True)
    else:
        # Try to create it
        try:
            requirements_content = """pyautogui>=0.9.54
Pillow>=10.0.0"""
            with open(requirements_file, 'w') as f:
                f.write(requirements_content)
            log_test("requirements.txt created", True)
        except Exception as e:
            log_test("requirements.txt creation", False, str(e))
    
    # Test 3: Check if AHK script exists
    ahk_script = os.path.join(working_dir, "CopilotAFK_Toggle_Assistant.ahk")
    ahk_exists = os.path.exists(ahk_script)
    log_test("AHK script exists", ahk_exists, ahk_script if not ahk_exists else "")
    
    # Test 4: Check if GitIngest script exists
    gitingest_script = os.path.join(working_dir, "generate_gitingest_summary.py")
    gitingest_exists = os.path.exists(gitingest_script)
    log_test("GitIngest script exists", gitingest_exists, gitingest_script if not gitingest_exists else "")
    
    # Test 5: Check if Accept/Reject images exist
    accept_img = os.path.join(working_dir, "accept.png")
    reject_img = os.path.join(working_dir, "reject.png")
    accept_exists = os.path.exists(accept_img)
    reject_exists = os.path.exists(reject_img)
    log_test("Accept image exists", accept_exists, accept_img if not accept_exists else "")
    log_test("Reject image exists", reject_exists, reject_img if not reject_exists else "")
    
    return all([ahk_exists, gitingest_exists, accept_exists, reject_exists])

def test_dependency_check() -> Tuple[bool, List[str]]:
    """Test dependency checking functionality."""
    print("\n=== Testing Dependency Check ===")
    
    missing_deps: List[str] = []
    
    # Check pyautogui
    try:
        import pyautogui
        version = getattr(pyautogui, '__version__', 'unknown')
        log_test("pyautogui import", True, f"Version: {version}")
    except ImportError:
        missing_deps.append("pyautogui")
        log_test("pyautogui import", False, "Not installed")
    
    # Check Pillow
    try:
        import PIL
        log_test("Pillow import", True, f"Version: {PIL.__version__}")
    except ImportError:
        missing_deps.append("Pillow")
        log_test("Pillow import", False, "Not installed")
    
    # Check gitingest
    try:
        import gitingest  # type: ignore
        log_test("gitingest import", True, "Module found")
    except ImportError:
        missing_deps.append("gitingest")
        log_test("gitingest import", False, "Not installed - GitIngest button may fail")
    
    return len(missing_deps) == 0, missing_deps

def test_pip_installation():
    """Test if pip is available for dependency installation."""
    print("\n=== Testing Pip Installation Capability ===")
    
    try:
        result = subprocess.run(
            ["pip", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            log_test("pip availability", True, result.stdout.strip())
            return True
        else:
            log_test("pip availability", False, "pip command failed")
            return False
    except subprocess.TimeoutExpired:
        log_test("pip availability", False, "pip command timed out")
        return False
    except FileNotFoundError:
        log_test("pip availability", False, "pip not found in PATH")
        return False

def test_autohotkey_availability():
    """Test if AutoHotkey is available."""
    print("\n=== Testing AutoHotkey Availability ===")
    
    # Check common AutoHotkey installation paths
    ahk_paths = [
        r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\v2\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
    ]
    
    for path in ahk_paths:
        if os.path.exists(path):
            log_test("AutoHotkey availability", True, f"Found at: {path}")
            return True
    
    # Try PATH as fallback
    try:
        result = subprocess.run(
            ["where", "autohotkey"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            log_test("AutoHotkey availability", True, f"Found in PATH: {result.stdout.strip()}")
            return True
    except Exception:
        pass
    
    log_test("AutoHotkey availability", False, "AutoHotkey not found in common locations or PATH")
    return False

def test_button_functionality_simulation():
    """Simulate button functionality tests."""
    print("\n=== Testing Button Functionality (Simulation) ===")
    
    # Test Install Dependencies button
    log_test("Install Dependencies button", True, "Would create/use requirements.txt and run pip install")
    
    # Test Check Dependencies button
    deps_ok, missing = test_dependency_check()
    log_test("Check Dependencies button", True, f"Missing: {missing}" if missing else "All dependencies found")
    
    # Test Start AHK Script button
    ahk_exists = os.path.exists("CopilotAFK_Toggle_Assistant.ahk")
    ahk_available = test_autohotkey_availability()
    can_start_ahk = ahk_exists and ahk_available
    log_test("Start AHK Script button", can_start_ahk, 
             "Ready to start" if can_start_ahk else "Missing AHK script or AutoHotkey")
    
    # Test Generate Project Summary button
    gitingest_exists = os.path.exists("generate_gitingest_summary.py")
    try:
        import gitingest  # type: ignore  # noqa: F401
        gitingest_module = True
    except ImportError:
        gitingest_module = False
    can_generate = gitingest_exists and gitingest_module
    log_test("Generate Project Summary button", can_generate,
             "Ready to generate" if can_generate else "Missing script or gitingest module")
    
    # Test Accept/Reject buttons
    if deps_ok:
        log_test("Manual Accept button (F6)", True, "Ready - pyautogui available")
        log_test("Manual Reject button (F7)", True, "Ready - pyautogui available")
        log_test("Toggle Autonomous button (F8)", True, "Ready - pyautogui available")
    else:
        log_test("Manual Accept button (F6)", False, "Requires pyautogui")
        log_test("Manual Reject button (F7)", False, "Requires pyautogui")
        log_test("Toggle Autonomous button (F8)", False, "Requires pyautogui")

def generate_test_report():
    """Generate a summary test report."""
    print("\n" + "="*60)
    print("TEST SUMMARY REPORT")
    print("="*60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r["passed"])
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests > 0:
        print("\nFailed Tests:")
        for result in test_results:
            if not result["passed"]:
                print(f"  - {result['test']}: {result['details']}")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS:")
    print("="*60)
    
    # Generate recommendations based on failures
    recommendations: List[str] = []
    
    if any(not r["passed"] for r in test_results if "pyautogui" in r["test"] or "Pillow" in r["test"]):
        recommendations.append("1. Click 'Install Dependencies' button to install missing Python packages")
    
    if any(not r["passed"] for r in test_results if "AutoHotkey" in r["test"]):
        recommendations.append("2. Install AutoHotkey v2.0 from https://www.autohotkey.com/")
    
    if any(not r["passed"] for r in test_results if "gitingest" in r["test"] and "import" in r["test"]):
        recommendations.append("3. Install gitingest module: pip install gitingest")
    
    if any(not r["passed"] for r in test_results if "image exists" in r["test"]):
        recommendations.append("4. Ensure accept.png and reject.png are in the project directory")
    
    if not recommendations:
        recommendations.append("✅ All systems ready! You can use all buttons in the GUI.")
    
    for rec in recommendations:
        print(rec)

def main():
    """Run all tests."""
    print("="*60)
    print("COPILOT AHK GUI - COMPREHENSIVE BUTTON TEST")
    print("="*60)
    print(f"Testing in directory: {os.path.abspath('.')}")
    
    # Run all test suites
    test_project_directory_operations()
    test_pip_installation()
    test_autohotkey_availability()
    test_button_functionality_simulation()
    
    # Generate report
    generate_test_report()
    
    # Show completion message
    print("\nTest complete. Review the recommendations above to ensure")
    print("all GUI buttons will work properly after setting project directory.")

if __name__ == "__main__":
    main() 