# Dependency Installation Guide

This guide provides detailed instructions for installing all dependencies required by the CopilotAHK automation system.

## Quick Installation

Run the following command in the project directory:

```bash
pip install -r requirements.txt
```

## Required Dependencies

### Core Dependencies
- **pyautogui** (≥0.9.54) - GUI automation and screen interaction
- **Pillow** (≥10.0.0) - Image processing for screenshot capabilities
- **gitingest** - Project analysis and context generation
- **psutil** (≥5.9.0) - Process and system utilities
- **pytest** - Testing framework
- **pyperclip** - Clipboard operations
- **watchdog** (≥3.0.0) - File system monitoring for auto-refresh
- **plyer** (≥2.1) - Cross-platform notifications
- **pystray** (≥0.19.5) - System tray integration

### Optional Dependencies
- **ttkthemes** - Enhanced UI themes (install with `pip install ttkthemes`)

## Manual Installation

If you prefer to install dependencies individually:

```bash
# Core automation
pip install pyautogui>=0.9.54
pip install Pillow>=10.0.0

# Project analysis
pip install gitingest

# System utilities
pip install psutil>=5.9.0

# Testing
pip install pytest

# Clipboard
pip install pyperclip

# File monitoring
pip install watchdog>=3.0.0

# Notifications and tray
pip install plyer>=2.1
pip install pystray>=0.19.5
```

## Verification

To verify all dependencies are installed correctly:

1. Open the CopilotAHK GUI
2. Navigate to the Setup tab
3. Click "Check & Install Dependencies"
4. Verify all packages show as "✓ Installed"

## Troubleshooting

### Permission Errors
If you encounter permission errors, try:
```bash
pip install --user -r requirements.txt
```

### Network Issues
If behind a proxy or firewall:
```bash
pip install --proxy [proxy_address] -r requirements.txt
```

### Version Conflicts
If you have version conflicts with existing packages:
```bash
pip install --upgrade --force-reinstall -r requirements.txt
```

## External Dependencies

### AutoHotkey v2
- Download from: https://www.autohotkey.com/
- Required for hotkey automation features
- Default installation path: `C:\Program Files\AutoHotkey\v2\AutoHotkey.exe`

## Notes

- All Python dependencies are automatically checked and can be installed through the GUI
- The watchdog dependency enables automatic context refresh when project files change
- The plyer and pystray dependencies enable system notifications and tray icon features
- AutoHotkey must be installed separately as it's not a Python package 