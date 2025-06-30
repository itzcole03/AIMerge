"""
main.py
The main entry point for the AI Pair Programming Assistant application.
"""

import tkinter as tk
from gui_clean import CleanGui

def main():
    """
    Initializes and runs the main application window.
    """
    # Create root window
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="arc")
    except ImportError:
        root = tk.Tk()
        print("ttkthemes not found, using default theme.")

    # Launch the clean GUI
    app = CleanGui(root)
    root.mainloop()

if __name__ == "__main__":
    main() 