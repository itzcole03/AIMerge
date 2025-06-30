# Unified AI Copilot Platform

A powerful integration of **AiSource** AI model management and **CopilotAHK** automation capabilities, creating the ultimate AI-powered development environment.

## 🚀 Features

### **🤖 AI Model Management (from AiSource)**

- **Multi-Provider Support**: Ollama, LM Studio, vLLM integration
- **8GB VRAM Optimization**: Intelligent model rotation and memory management
- **Advanced Model Search**: Powerful filtering and discovery capabilities
- **Real-time Monitoring**: Live provider status and model performance tracking
- **Resource Management**: Intelligent VRAM and CPU utilization

### **⚡ Automation & Orchestration (from CopilotAHK)**

- **AutoHotkey Integration**: Seamless Cursor editor automation
- **Dual-Agent Workflow**: Main agent + Supervisor agent coordination
- **Accept/Reject Automation**: Intelligent AI-driven decisions
- **Hotkey Controls**: F6-F12 keyboard shortcuts for manual control
- **Project Analysis**: GitIngest integration for context generation

### **🎯 Multi-Agent System**

- **Specialized Agents**: Architect, Frontend, Backend, QA, Orchestrator
- **Task Coordination**: Intelligent task assignment and tracking
- **Real-time Updates**: WebSocket-based live status monitoring
- **Workflow Automation**: End-to-end development process automation

## 📋 Requirements

### **System Requirements**

- Windows 10/11 (for AutoHotkey features)
- Python 3.8+
- Node.js 18+
- AutoHotkey v2.0 (for automation features)
- 8GB+ RAM (optimized for 8GB VRAM systems)

### **Optional Dependencies**

- CUDA-compatible GPU (for local model inference)
- Ollama, LM Studio, or vLLM (for AI model serving)
- Cursor Editor (for automation features)

## 🛠️ Installation

### **1. Quick Setup**

```bash
# Clone the repository
git clone <repository-url>
cd AiSource-main/frontend/model\ manager

# Install everything at once
npm run setup
```

### **2. Manual Setup**

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
npm run install-backend

# Install automation dependencies (optional)
npm run install-automation
```

### **3. AutoHotkey Setup (for automation)**

1. Download and install [AutoHotkey v2.0](https://www.autohotkey.com/)
2. Ensure the CopilotAHK directory is available at the project root
3. Verify the AHK script path in the configuration

## 🎮 Usage

### **🚀 Starting the Unified Platform**

**Option 1: Unified Launch (Recommended)**

```bash
npm run start-unified
```

This starts both the backend API server and the frontend development server.

**Option 2: Separate Components**

```bash
# Terminal 1: Backend
npm run start-backend

# Terminal 2: Frontend
npm run dev
```

### **🌐 Access the Platform**

- **Web Interface**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### **📱 Platform Tabs**

#### **1. AI Models Tab**

- Manage AI model providers (Ollama, LM Studio, vLLM)
- Start/stop model services
- Monitor resource usage and model performance
- Advanced model search and filtering

#### **2. Copilot Automation Tab**

- Control AutoHotkey automation for Cursor editor
- Configure autonomous vs manual decision modes
- Set accept/reject rates for different agent types
- View real-time automation logs and activity

#### **3. Agent Orchestra Tab**

- Manage multi-agent development workflows
- Create and assign tasks to specialized agents
- Monitor agent status and progress
- Coordinate complex development projects

### **⌨️ Hotkey Controls**

| Key   | Function                   |
| ----- | -------------------------- |
| `F6`  | Manual Accept              |
| `F7`  | Manual Reject              |
| `F8`  | Toggle Autonomous Mode     |
| `F9`  | Toggle Automation ON/OFF   |
| `F10` | Switch to Supervisor Agent |
| `F11` | Switch to Main Agent       |
| `F12` | Send Supervisor Prompt     |

## 🔧 Configuration

### **Backend Configuration**

The backend server can be configured via environment variables:

```bash
# Server settings
HOST=0.0.0.0
PORT=8000

# Model provider settings
OLLAMA_HOST=http://localhost:11434
LMSTUDIO_HOST=http://localhost:1234
VLLM_HOST=http://localhost:8000
```

### **Automation Settings**

Automation behavior can be configured through the web interface:

- **Autonomous Mode**: Enable AI-driven accept/reject decisions
- **Accept Rates**: Different rates for main agent (85%) vs supervisor (70%)
- **Cycle Time**: Interval between automation cycles (default: 180s)
- **Hotkeys**: Enable/disable keyboard shortcuts

### **Agent Configuration**

Each agent can be configured with:

- **Model Assignment**: Which LLM to use for the agent
- **Capabilities**: Specialized skills and focus areas
- **Priority**: Task assignment priority
- **Resource Limits**: Memory and processing constraints

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Unified AI Copilot Platform              │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript + Tailwind)                  │
│  ├── AI Models Tab (AiSource)                             │
│  ├── Copilot Automation Tab (CopilotAHK)                  │
│  └── Agent Orchestra Tab (Multi-Agent)                     │
├───────────────────────────────────────────────────────���─────┤
│  Backend (FastAPI + WebSocket)                             │
│  ├── Model Management API                                  │
│  ├── Automation Control API                               │
│  ├── Agent Orchestration API                              │
│  └── Real-time Updates (WebSocket)                        │
├─────────────────────────────────────────────────────────────┤
│  Integration Layer                                          │
│  ├── AiSource Components                                   │
│  │   ├── IntelligentModelManager                          │
│  │   ├── AgentManager                                     │
│  │   └── MemoryManager                                    │
│  ├── CopilotAHK Components                                │
│  │   ├── AutoHotkey Scripts                               │
│  │   ├── GitIngest Integration                            │
│  │   └── Automation Bridge                                │
│  └── Automation Layer                                      │
│      ├── PyAutoGUI                                        │
│      ├── AutoHotkey v2                                    │
│      └── Cursor Integration                               │
└─────────────────────────────────────────────────────────────┘
```

## 🤝 Integration Benefits

### **Why Merge AiSource + CopilotAHK?**

1. **🎯 Complete Workflow**: From model management to code automation
2. **🚀 Productivity Boost**: AI model optimization + development automation
3. **🧠 Intelligence**: Multi-agent coordination with smart automation
4. **⚡ Efficiency**: 8GB VRAM optimization + seamless editor integration
5. **🔄 Real-time**: Live monitoring and control of entire AI development stack

### **Synergistic Features**

- **Smart Model Selection**: Agents automatically choose optimal models for tasks
- **Resource Optimization**: Share VRAM efficiently between model inference and automation
- **Context Sharing**: Project analysis from GitIngest feeds into agent decision-making
- **Unified Monitoring**: Single interface for models, agents, and automation
- **Intelligent Automation**: AI agents control automation behavior based on context

## 🔍 API Reference

### **Model Management**

```bash
GET /api/models                     # Get all models and providers
POST /api/models/{provider}/start   # Start a model provider
POST /api/models/{provider}/stop    # Stop a model provider
```

### **Automation Control**

```bash
GET /api/automation/status          # Get automation status
POST /api/automation/start          # Start automation
POST /api/automation/stop           # Stop automation
POST /api/automation/accept         # Manual accept
POST /api/automation/reject         # Manual reject
```

### **Agent Management**

```bash
GET /api/agents                     # Get all agents
GET /api/agents/{id}                # Get specific agent
POST /api/agents/{id}/assign        # Assign task to agent
GET /api/agents/tasks               # Get all tasks
POST /api/agents/tasks              # Create new task
```

### **Real-time Updates**

```bash
WebSocket: ws://localhost:8000/ws   # Real-time updates
```

## 🚀 Development

### **Project Structure**

```
AiSource-main/frontend/model manager/
├── src/
│   ├── components/
│   │   ├── CopilotIntegration.tsx      # Automation controls
│   │   ├── AgentOrchestrator.tsx       # Multi-agent management
│   │   └── ...                         # Other AiSource components
│   ├── hooks/                          # React hooks
│   ├── services/                       # API services
│   └── types/                          # TypeScript types
├── backend/
│   ├── unified_server.py               # Main backend server
│   └── requirements.txt                # Python dependencies
├── automation_bridge.py               # CopilotAHK integration
└── package.json                       # Project configuration
```

### **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📈 Roadmap

### **Near Term**

- [ ] Enhanced AI model fine-tuning interface
- [ ] More automation providers (VS Code, JetBrains)
- [ ] Advanced agent specialization and training
- [ ] Cloud deployment and scaling options

### **Long Term**

- [ ] Machine learning for automation optimization
- [ ] Custom agent creation and marketplace
- [ ] Integration with more development tools
- [ ] Advanced analytics and performance insights

## 🐛 Troubleshooting

### **Common Issues**

**Automation not working:**

- Ensure AutoHotkey v2.0 is installed
- Check that Cursor editor is running
- Verify hotkeys are enabled in settings

**Models not loading:**

- Check if model providers (Ollama/LM Studio) are running
- Verify API endpoints in configuration
- Ensure sufficient VRAM for model loading

**Agents not responding:**

- Check backend server status
- Verify WebSocket connection
- Review agent logs for errors

### **Debugging**

```bash
# Backend logs
npm run start-backend

# Frontend logs
npm run dev

# Check automation bridge
python automation_bridge.py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AiSource**: AI model management and multi-agent orchestration
- **CopilotAHK**: Automation and editor integration capabilities
- **AutoHotkey Community**: Automation scripting foundation
- **React + FastAPI**: Modern web development stack

---

**The Unified AI Copilot Platform** - Where AI model management meets intelligent automation! 🚀🤖⚡
