#!/usr/bin/env python3
"""
Ultimate CopilotAHK - Main Entry Point
Choose between Clean GUI or Ultimate AI Platform
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def show_launcher():
    """Show launcher to choose application mode"""
    root = tk.Tk()
    root.title("🤖 CopilotAHK Launcher")
    root.geometry("500x300")
    root.resizable(False, False)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    main_frame = tk.Frame(root, padx=30, pady=30)
    main_frame.pack(expand=True, fill='both')
    
    # Title
    title_label = tk.Label(main_frame, text="🤖 CopilotAHK", font=("Arial", 24, "bold"))
    title_label.pack(pady=(0, 10))
    
    subtitle_label = tk.Label(main_frame, text="Choose Your Experience", font=("Arial", 14))
    subtitle_label.pack(pady=(0, 30))
    
    # Option 1: Clean GUI
    clean_frame = tk.Frame(main_frame, relief='raised', bd=2, padx=20, pady=15)
    clean_frame.pack(fill='x', pady=10)
    
    tk.Label(clean_frame, text="🎯 Clean & Simple", font=("Arial", 16, "bold")).pack()
    tk.Label(clean_frame, text="Essential automation features\nFast startup, proven stability", 
             font=("Arial", 10), justify='center').pack(pady=5)
    
    def launch_clean():
        root.destroy()
        try:
            # Add proper path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, current_dir)
            
            from gui_clean import CleanGui
            clean_root = tk.Tk()
            CleanGui(clean_root)
            clean_root.mainloop()
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch Clean GUI:\n{e}")
            # Restart launcher
            show_launcher()
    
    tk.Button(clean_frame, text="🚀 Launch Clean GUI", command=launch_clean,
              font=("Arial", 12), bg='#4CAF50', fg='white', padx=20, pady=5).pack(pady=10)
    
    # Option 2: Ultimate AI
    ultimate_frame = tk.Frame(main_frame, relief='raised', bd=2, padx=20, pady=15)
    ultimate_frame.pack(fill='x', pady=10)
    
    tk.Label(ultimate_frame, text="🤖 Ultimate AI Platform", font=("Arial", 16, "bold")).pack()
    tk.Label(ultimate_frame, text="Full AI integration with multi-agent system\nAdvanced features, intelligent automation", 
             font=("Arial", 10), justify='center').pack(pady=5)
    
    def launch_ultimate():
        root.destroy()
        try:
            # Add proper path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, current_dir)
            
            from ultimate_copilot_ahk import UltimateCopilotGUI
            ultimate_root = tk.Tk()
            UltimateCopilotGUI(ultimate_root)
            ultimate_root.mainloop()
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to load Ultimate AI Platform:\n{e}")
            # Restart launcher
            show_launcher()
    
    tk.Button(ultimate_frame, text="🚀 Launch Ultimate AI", command=launch_ultimate,
              font=("Arial", 12), bg='#2196F3', fg='white', padx=20, pady=5).pack(pady=10)
    
    # Footer
    footer_label = tk.Label(main_frame, text="💡 Tip: Start with Clean GUI for first-time setup", 
                           font=("Arial", 9), fg='gray')
    footer_label.pack(side='bottom', pady=(20, 0))
    
    root.mainloop()

def main():
    """Main entry point"""
    # Check if we should show launcher or go direct
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'clean':
            # Launch clean GUI directly
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                sys.path.insert(0, current_dir)
                from gui_clean import CleanGui
                root = tk.Tk()
                CleanGui(root)
                root.mainloop()
            except Exception as e:
                print(f"Failed to launch Clean GUI: {e}")
                sys.exit(1)
            
        elif mode == 'ultimate':
            # Launch ultimate AI directly
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                sys.path.insert(0, current_dir)
                from ultimate_copilot_ahk import UltimateCopilotGUI
                root = tk.Tk()
                UltimateCopilotGUI(root)
                root.mainloop()
            except Exception as e:
                print(f"Failed to load Ultimate AI Platform: {e}")
                sys.exit(1)
                
        else:
            print("Usage: python main_ultimate.py [clean|ultimate]")
            sys.exit(1)
    else:
        # Show launcher
        show_launcher()

if __name__ == "__main__":
    main() 