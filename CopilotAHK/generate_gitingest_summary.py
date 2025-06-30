"""
generate_gitingest_summary.py
A simple script and GUI to generate and view a GitIngest project summary for LLM agents.
"""

import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox

from gitingest import ingest  # type: ignore

REPO_PATH = os.path.abspath(".")
SUMMARY_FILE = "gitingest_summary.txt"


def generate_summary():
    """Generate the GitIngest summary and show a message box on completion or error."""
    try:
        summary, tree, content = ingest(REPO_PATH)
        with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
            f.write(f"{summary}\n\n{tree}\n\n{content}")
        messagebox.showinfo("Success", f"Summary generated as {SUMMARY_FILE}")  # type: ignore
    except (OSError, RuntimeError, ValueError) as e:
        messagebox.showerror("Error", str(e))  # type: ignore


def open_summary():
    """Open the generated summary file with the default application."""
    if os.path.exists(SUMMARY_FILE):
        try:
            if os.name == "nt":
                os.startfile(SUMMARY_FILE)
            else:
                subprocess.call(["open", SUMMARY_FILE])
        except OSError as e:
            messagebox.showerror("Error", str(e))  # type: ignore
    else:
        messagebox.showwarning("Not found", f"{SUMMARY_FILE} does not exist.")  # type: ignore


def run_generate_thread():
    """Run the summary generation in a background thread for GUI responsiveness."""
    threading.Thread(target=generate_summary, daemon=True).start()


def main():
    """Launch the simple GitIngest summary GUI."""
    root = tk.Tk()
    root.title("GitIngest Summary GUI")
    root.geometry("300x120")

    btn_generate = tk.Button(
        root, text="Generate Summary", command=run_generate_thread, width=25
    )
    btn_generate.pack(pady=10)

    btn_open = tk.Button(root, text="Open Summary File", command=open_summary, width=25)
    btn_open.pack(pady=5)

    btn_exit = tk.Button(root, text="Exit", command=root.destroy, width=25)
    btn_exit.pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
