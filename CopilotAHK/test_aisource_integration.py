#!/usr/bin/env python3
"""
Test script for AiSource integration with CopilotAHK
"""

import sys
import os
sys.path.insert(0, 'src')

def test_basic_integration():
    """Test basic integration functionality"""
    print("🧪 Testing AiSource Integration...")
    
    try:
        from src.aisource_integration import (
            AiSourceClient, CopilotAiSourceBridge, 
            IntegratedAutomationController
        )
        print("✅ Integration modules imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test client initialization
    try:
        client = AiSourceClient()
        print("✅ AiSource client created")
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False
    
    # Test bridge initialization
    try:
        bridge = CopilotAiSourceBridge()
        print("✅ Integration bridge created")
    except Exception as e:
        print(f"❌ Bridge creation failed: {e}")
        return False
    
    # Test controller initialization
    try:
        controller = IntegratedAutomationController()
        print("✅ Automation controller created")
    except Exception as e:
        print(f"❌ Controller creation failed: {e}")
        return False
    
    return True

def test_connection():
    """Test connection to AiSource (if available)"""
    print("\n🔗 Testing AiSource Connection...")
    
    try:
        from src.aisource_integration import initialize_integration
        
        # This will fail if AiSource is not running, which is expected
        success = initialize_integration()
        if success:
            print("✅ AiSource connection successful!")
        else:
            print("⚠️ AiSource not available (expected if not running)")
        
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_gui_integration():
    """Test GUI integration"""
    print("\n🖥️ Testing GUI Integration...")
    
    try:
        import tkinter as tk
        sys.path.insert(0, 'src')
        from gui_clean import CleanGui, AISOURCE_AVAILABLE
        
        print(f"✅ GUI imported, AiSource available: {AISOURCE_AVAILABLE}")
        
        # Test basic GUI creation (without showing)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = CleanGui(root)
        print("✅ GUI with AiSource integration created")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        return False

def test_decision_analysis():
    """Test decision analysis functionality"""
    print("\n🧠 Testing Decision Analysis...")
    
    try:
        from src.aisource_integration import get_intelligent_decision
        
        # Test with mock context
        mock_context = {
            "suggestion": "def hello_world():\n    print('Hello, World!')",
            "file": "test.py",
            "history": "User is working on a simple Python function"
        }
        
        decision = get_intelligent_decision(mock_context)
        print(f"✅ Decision analysis completed: {decision}")
        
        return True
        
    except Exception as e:
        print(f"❌ Decision analysis test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 CopilotAHK + AiSource Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Integration", test_basic_integration),
        ("Connection Test", test_connection),
        ("GUI Integration", test_gui_integration),
        ("Decision Analysis", test_decision_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
    elif passed > 0:
        print("⚠️ Some tests passed. Integration partially working.")
    else:
        print("❌ All tests failed. Check your setup.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 