"""
main_clean.py
Simple main entry point for testing the clean GUI.
"""

import tkinter as tk
from gui_clean import CleanGui

def main():
    """Initialize and run the clean GUI."""
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="arc")
    except ImportError:
        root = tk.Tk()
        print("ttkthemes not found, using default theme.")

    app = CleanGui(root)
    root.mainloop()

if __name__ == "__main__":
    main() 