# Copilot Dual-Agent Hybrid Automation System

A sophisticated automation system that integrates Python, React, and AutoHotkey (AHK) to create an intelligent workflow between developer and supervisor agents in Cursor editor, with hybrid Accept/Reject automation capabilities.

## 🚀 Features

### **Hybrid Accept/Reject Automation**
- **Autonomous Mode**: AI-driven decisions based on agent/supervisor context
- **Manual Mode**: Direct control via GUI buttons or hotkeys
- **Smart Heuristics**: Different acceptance rates for main vs supervisor agents
- **Cursor Integration**: Uses cropped Accept/Reject button images for precise clicking

### **Dual-Agent Workflow**
- **Main Agent**: Development and implementation (left panel)
- **Supervisor Agent**: Code review and quality assurance (right panel)
- **Context Sharing**: Automatic GitIngest summary generation and distribution
- **Best Practices**: Integration principles from ForgeCode AI agent guide

### **Intelligent Automation**
- **Image Recognition**: Finds and clicks Accept/Reject buttons using screenshots
- **State Management**: Tracks agent modes, decision timing, and workflow states
- **Error Handling**: Robust fallbacks and debug tooltips
- **Configurable Timing**: Adjustable cycles and idle detection

## 📋 Requirements

### **System Requirements**
- Windows 10/11
- Python 3.8+
- AutoHotkey v2.0
- Cursor Editor

### **Python Dependencies**
```bash
pip install -r requirements.txt
```

**Required packages:**
- `pyautogui>=0.9.54` - For manual Accept/Reject controls
- `Pillow>=10.0.0` - For image processing

## 🛠️ Installation

1. **Clone/Download** the project files
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install AutoHotkey v2.0** from [autohotkey.com](https://www.autohotkey.com/)
4. **Ensure Cursor Editor** is installed and accessible

## 🎮 Usage

### **🚀 Quick Start (Guided Setup)**
1. **Launch the guided setup:**
   ```bash
   python copilot_dual_agent_gui.py
   ```
   Or use the batch file:
   ```bash
   start.bat
   ```

2. **Follow the 4-step wizard:**
   - **Step 1**: Select your project directory
   - **Step 2**: Automatic dependency check & installation
   - **Step 3**: Automatic project analysis & AI context generation
   - **Step 4**: Start/stop automation controls

3. **Start automation** with the big green button
4. **Open Cursor** and press F9 to enable automation

### **⚙️ Advanced Mode (Power Users)**
For experienced users who want full control:
```bash
python copilot_dual_agent_gui_advanced.py
```
Or click "Advanced Mode" in the guided setup.

### **Hotkeys**

| Key | Function |
|-----|----------|
| `F9` | Toggle automation ON/OFF |
| `F8` | Toggle autonomous mode ON/OFF |
| `F6` | Manual Accept |
| `F7` | Manual Reject |
| `F10` | Switch to supervisor chat |
| `F11` | Switch to main chat |
| `F12` | Send supervisor prompt |

### **GUI Controls**

#### **Project Directory**
- Set the working directory for your project
- Used for GitIngest summary generation

#### **AHK Automation**
- **Start Copilot AHK Script**: Launches the automation
- **Stop All AHK Scripts**: Terminates all AutoHotkey processes

#### **Accept/Reject Controls**
- **Manual Accept (F6)**: Green button to manually accept changes
- **Manual Reject (F7)**: Red button to manually reject changes  
- **Toggle Autonomous (F8)**: Blue button to switch automation modes

#### **GitIngest Project Summary**
- **Generate Project Summary**: Creates up-to-date codebase context
- **Open Summary File**: Reviews the context being sent to agents

## 🔧 Configuration

### **AHK Script Settings**
Edit `CopilotAFK_Toggle_Assistant.ahk` to customize:

```autohotkey
; Timing Configuration
cycleTime := 180000        ; 3 minutes between supervisor interventions
supervisorIdleTime := 300000  ; 5 minutes before supervisor becomes active

; Autonomous Decision Rates
; Main agent: 85% accept rate
; Supervisor: 70% accept rate (more conservative)
```

### **Image Files**
- `accept.png` - Screenshot of Cursor's Accept button
- `reject.png` - Screenshot of Cursor's Reject button
- Update these if Cursor's UI changes

### **Integration Principles**
The system follows these best practices:
1. No mock data - Use real API calls
2. No placeholders or TODOs - Complete implementations
3. Use real database/Redis instances
4. Create concrete interfaces matching FastAPI models
5. Implement proper error boundaries
6. Favor integration tests over unit tests with mocks
7. Create regression tests for bugs
8. Only mock time-based operations or external APIs when necessary

## 🤖 How It Works

### **Autonomous Decision Logic**
The system makes Accept/Reject decisions based on:

1. **Current Agent Mode**:
   - Main Agent: 85% accept rate (more trusting)
   - Supervisor Agent: 70% accept rate (more conservative)

2. **Timing Constraints**:
   - 10-second minimum between decisions
   - Prevents rapid-fire clicking

3. **Context Awareness**:
   - Considers recent chat activity
   - Evaluates agent/supervisor workflow state

### **Dual-Agent Workflow**
1. **Main Agent** works on implementation tasks
2. **Supervisor Agent** reviews and provides feedback
3. **Context Sharing** ensures both agents have project knowledge
4. **Quality Gates** enforce best practices and standards

### **Image Recognition**
- Uses `ImageSearch` to locate Accept/Reject buttons
- Adjusts mouse position for accurate clicking
- Provides debug tooltips for visibility

## 🧪 Testing

Run the test suite to verify your setup:

```bash
python test_accept_reject.py
```

This will check:
- ✅ Accept/Reject image files
- ✅ AHK script availability
- ✅ GUI script functionality
- ✅ pyautogui installation

## 📁 File Structure

```
CopilotAHK/
├── CopilotAFK_Toggle_Assistant.ahk  # Main automation script
├── copilot_dual_agent_gui.py        # GUI control panel
├── generate_gitingest_summary.py    # Project context generator
├── test_accept_reject.py            # System test suite
├── requirements.txt                 # Python dependencies
├── start.bat                       # Quick launch script
├── accept.png                      # Accept button image
├── reject.png                      # Reject button image
├── gitingest_summary.txt           # Generated project context
└── README.md                       # This file
```

## 🔍 Troubleshooting

### **Common Issues**

**AutoHotkey not found:**
- Install AutoHotkey v2.0 from the official website
- Ensure it's added to your system PATH

**Images not found:**
- Verify `accept.png` and `reject.png` exist
- Update images if Cursor's UI has changed

**pyautogui not working:**
- Install with: `pip install pyautogui`
- Check if antivirus is blocking automation

**Buttons not being clicked:**
- Adjust mouse offset in AHK script
- Verify screen resolution and scaling
- Check if Cursor window is active

### **Debug Mode**
Enable debug tooltips in the AHK script:
```autohotkey
debugMode := true  ; Set to true for debugging tooltips
```

## 🚀 Advanced Usage

### **Custom Decision Logic**
Modify the `MakeAutonomousDecision()` function in the AHK script to implement your own heuristics:

```autohotkey
MakeAutonomousDecision() {
    ; Add your custom logic here
    ; Consider chat content, file changes, etc.
    return "accept" or "reject"
}
```

### **Integration with CI/CD**
The system can be integrated with continuous integration pipelines:
- Use GitIngest summaries for automated code review
- Trigger supervisor interventions based on commit patterns
- Generate automated quality reports

### **Multi-Project Support**
- Set different working directories for different projects
- Generate project-specific GitIngest summaries
- Maintain separate agent contexts per project

## 📈 Best Practices

1. **Regular Context Updates**: Generate new GitIngest summaries after major changes
2. **Monitor Autonomous Decisions**: Review tooltips to understand automation behavior
3. **Balance Automation**: Use manual mode for critical decisions
4. **Keep Images Updated**: Refresh Accept/Reject screenshots when Cursor updates
5. **Test Thoroughly**: Run the test suite before deploying to production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Run the test suite
3. Review debug tooltips
4. Check AutoHotkey and Python logs

## Quick Wins (Implemented)

These features are implemented for immediate value and user experience:

- **Auto-test-on-save**: Automatically runs tests when files change in the project directory, ensuring rapid feedback and reliability.
- **One-click bug report**: Packages logs and context into a report for easy troubleshooting and support.
- **Dark mode**: Toggle between dark and light UI themes for comfort and accessibility.
- **Quick action tray menu**: Right-click the system tray icon for fast access to key features (AFK Mode, Setup, Diagnose, etc.).

See the Deployment Readiness Checklist for the full roadmap.

---

**Happy automating! 🎉** 