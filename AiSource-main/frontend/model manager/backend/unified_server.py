#!/usr/bin/env python3
"""
Unified Backend Server
Combines AiSource AI model management with CopilotAHK automation capabilities
"""

import os
import sys
import json
import time
import asyncio
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Add parent directories to path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent))
sys.path.append(str(current_dir.parent.parent.parent))

# Import AiSource components
try:
    from intelligent_model_manager import IntelligentModelManager
    from agents.base_agent import BaseAgent
    from core.agent_manager import AgentManager
    AISOURCE_AVAILABLE = True
except ImportError as e:
    print(f"AiSource components not available: {e}")
    AISOURCE_AVAILABLE = False

# Import CopilotAHK components
try:
    import pyautogui
    import PIL
    AUTOMATION_AVAILABLE = True
except ImportError:
    print("Automation components not available")
    AUTOMATION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unified AI Copilot Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class AutomationSettings(BaseModel):
    autonomousMode: bool
    acceptRate: int
    supervisorRate: int
    cycleTime: int
    hotkeysEnabled: bool

class AgentStatus(BaseModel):
    isActive: bool
    mode: str
    lastAction: str
    timestamp: datetime

class Task(BaseModel):
    id: str
    title: str
    description: str
    assignedTo: Optional[str] = None
    status: str = 'pending'
    priority: str = 'medium'
    createdAt: datetime
    estimatedTime: Optional[int] = None

class Agent(BaseModel):
    id: str
    name: str
    type: str
    status: str
    currentTask: Optional[str] = None
    progress: Optional[int] = None
    lastUpdate: datetime
    capabilities: List[str]
    model: Optional[str] = None

# Global state
class UnifiedState:
    def __init__(self):
        self.model_manager = None
        self.agent_manager = None
        self.automation_settings = AutomationSettings(
            autonomousMode=False,
            acceptRate=85,
            supervisorRate=70,
            cycleTime=180,
            hotkeysEnabled=True
        )
        self.agent_status = AgentStatus(
            isActive=False,
            mode='main',
            lastAction='None',
            timestamp=datetime.now()
        )
        self.is_automation_running = False
        self.agents = {}
        self.tasks = {}
        self.websocket_connections = []
        self.ahk_process = None

    async def initialize(self):
        """Initialize all components"""
        if AISOURCE_AVAILABLE:
            try:
                self.model_manager = IntelligentModelManager()
                await self.model_manager.initialize()
                logger.info("Intelligent Model Manager initialized")
                
                self.agent_manager = AgentManager()
                await self.agent_manager.initialize()
                logger.info("Agent Manager initialized")
                
                # Initialize default agents
                self.agents = {
                    'architect': Agent(
                        id='architect',
                        name='Architect Agent',
                        type='architect',
                        status='idle',
                        lastUpdate=datetime.now(),
                        capabilities=['System Design', 'Architecture Planning', 'Technology Selection'],
                        model='llama3.1-70b'
                    ),
                    'frontend': Agent(
                        id='frontend',
                        name='Frontend Agent',
                        type='frontend',
                        status='idle',
                        lastUpdate=datetime.now(),
                        capabilities=['React Development', 'UI/UX Design', 'Component Creation'],
                        model='codellama-34b'
                    ),
                    'backend': Agent(
                        id='backend',
                        name='Backend Agent',
                        type='backend',
                        status='idle',
                        lastUpdate=datetime.now(),
                        capabilities=['API Development', 'Database Design', 'Server Architecture'],
                        model='codellama-34b'
                    ),
                    'qa': Agent(
                        id='qa',
                        name='QA Agent',
                        type='qa',
                        status='idle',
                        lastUpdate=datetime.now(),
                        capabilities=['Test Creation', 'Code Review', 'Quality Assurance'],
                        model='llama3.1-8b'
                    ),
                    'orchestrator': Agent(
                        id='orchestrator',
                        name='Orchestrator Agent',
                        type='orchestrator',
                        status='idle',
                        lastUpdate=datetime.now(),
                        capabilities=['Task Coordination', 'Resource Management', 'Planning'],
                        model='llama3.1-70b'
                    )
                }
            except Exception as e:
                logger.error(f"Failed to initialize AiSource components: {e}")

state = UnifiedState()

# WebSocket connection manager
async def broadcast_update(data: Dict[str, Any]):
    """Broadcast updates to all connected WebSocket clients"""
    if state.websocket_connections:
        message = json.dumps(data)
        for websocket in state.websocket_connections[:]:  # Copy list to avoid modification during iteration
            try:
                await websocket.send_text(message)
            except:
                state.websocket_connections.remove(websocket)

# API Routes

@app.on_event("startup")
async def startup_event():
    """Initialize the unified system on startup"""
    await state.initialize()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "aisource_available": AISOURCE_AVAILABLE,
        "automation_available": AUTOMATION_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# Model Management Endpoints (from AiSource)
@app.get("/api/models")
async def get_models():
    """Get available AI models"""
    if not state.model_manager:
        return {"providers": [], "models": []}
    
    try:
        status = await state.model_manager.get_model_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        return {"providers": [], "models": [], "error": str(e)}

@app.post("/api/models/{provider}/start")
async def start_provider(provider: str):
    """Start a model provider"""
    if not state.model_manager:
        raise HTTPException(status_code=503, detail="Model manager not available")
    
    try:
        result = await state.model_manager.start_provider(provider)
        await broadcast_update({"type": "provider_started", "provider": provider, "result": result})
        return result
    except Exception as e:
        logger.error(f"Failed to start provider {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/models/{provider}/stop")
async def stop_provider(provider: str):
    """Stop a model provider"""
    if not state.model_manager:
        raise HTTPException(status_code=503, detail="Model manager not available")
    
    try:
        result = await state.model_manager.stop_provider(provider)
        await broadcast_update({"type": "provider_stopped", "provider": provider, "result": result})
        return result
    except Exception as e:
        logger.error(f"Failed to stop provider {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent Management Endpoints
@app.get("/api/agents")
async def get_agents():
    """Get all available agents"""
    return list(state.agents.values())

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    if agent_id not in state.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return state.agents[agent_id]

@app.post("/api/agents/{agent_id}/assign")
async def assign_task_to_agent(agent_id: str, task_data: Dict[str, str]):
    """Assign a task to an agent"""
    if agent_id not in state.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    task_id = task_data.get("taskId")
    if not task_id or task_id not in state.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update agent status
    state.agents[agent_id].status = 'working'
    state.agents[agent_id].currentTask = state.tasks[task_id].title
    state.agents[agent_id].lastUpdate = datetime.now()
    
    # Update task status
    state.tasks[task_id].assignedTo = agent_id
    state.tasks[task_id].status = 'in-progress'
    
    await broadcast_update({
        "type": "task_assigned",
        "agentId": agent_id,
        "taskId": task_id
    })
    
    return {"status": "success", "message": f"Task assigned to {agent_id}"}

@app.get("/api/agents/tasks")
async def get_tasks():
    """Get all tasks"""
    return list(state.tasks.values())

@app.post("/api/agents/tasks")
async def create_task(task: Task):
    """Create a new task"""
    task.id = str(int(time.time() * 1000))  # Generate unique ID
    task.createdAt = datetime.now()
    state.tasks[task.id] = task
    
    await broadcast_update({
        "type": "task_created",
        "task": task.dict()
    })
    
    return task

# Automation Endpoints (from CopilotAHK)
@app.get("/api/automation/status")
async def get_automation_status():
    """Get current automation status"""
    return {
        "isRunning": state.is_automation_running,
        "agentStatus": state.agent_status.dict(),
        "settings": state.automation_settings.dict()
    }

@app.post("/api/automation/start")
async def start_automation(settings: AutomationSettings):
    """Start the automation system"""
    if not AUTOMATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Automation not available")
    
    state.automation_settings = settings
    state.is_automation_running = True
    state.agent_status.isActive = True
    state.agent_status.timestamp = datetime.now()
    
    # Start AutoHotkey script if available
    try:
        ahk_script_path = current_dir.parent.parent.parent / "CopilotAHK" / "CopilotAFK_Toggle_Assistant.ahk"
        if ahk_script_path.exists():
            state.ahk_process = subprocess.Popen(
                ["autohotkey.exe", str(ahk_script_path)],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
    except Exception as e:
        logger.warning(f"Failed to start AHK script: {e}")
    
    await broadcast_update({
        "type": "automation_started",
        "settings": settings.dict()
    })
    
    return {"status": "started", "message": "Automation system started"}

@app.post("/api/automation/stop")
async def stop_automation():
    """Stop the automation system"""
    state.is_automation_running = False
    state.agent_status.isActive = False
    state.agent_status.timestamp = datetime.now()
    
    # Stop AutoHotkey process if running
    if state.ahk_process:
        try:
            state.ahk_process.terminate()
            state.ahk_process = None
        except Exception as e:
            logger.warning(f"Failed to stop AHK process: {e}")
    
    await broadcast_update({"type": "automation_stopped"})
    return {"status": "stopped", "message": "Automation system stopped"}

@app.post("/api/automation/accept")
async def manual_accept():
    """Trigger manual accept"""
    if AUTOMATION_AVAILABLE:
        try:
            # Use pyautogui to simulate F6 key (or click accept button)
            pyautogui.press('f6')
            state.agent_status.lastAction = 'Accept'
            state.agent_status.timestamp = datetime.now()
            
            await broadcast_update({
                "type": "manual_action",
                "action": "accept"
            })
            
            return {"status": "success", "action": "accept"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to trigger accept: {e}")
    else:
        raise HTTPException(status_code=503, detail="Automation not available")

@app.post("/api/automation/reject")
async def manual_reject():
    """Trigger manual reject"""
    if AUTOMATION_AVAILABLE:
        try:
            # Use pyautogui to simulate F7 key (or click reject button)
            pyautogui.press('f7')
            state.agent_status.lastAction = 'Reject'
            state.agent_status.timestamp = datetime.now()
            
            await broadcast_update({
                "type": "manual_action",
                "action": "reject"
            })
            
            return {"status": "success", "action": "reject"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to trigger reject: {e}")
    else:
        raise HTTPException(status_code=503, detail="Automation not available")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    state.websocket_connections.append(websocket)
    
    try:
        # Send initial state
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "automation": {
                "isRunning": state.is_automation_running,
                "agentStatus": state.agent_status.dict(),
                "settings": state.automation_settings.dict()
            },
            "agents": [agent.dict() for agent in state.agents.values()],
            "tasks": [task.dict() for task in state.tasks.values()]
        }))
        
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in state.websocket_connections:
            state.websocket_connections.remove(websocket)

# Serve static files
@app.mount("/", StaticFiles(directory=current_dir.parent / "dist", html=True), name="static")

if __name__ == "__main__":
    # Configuration
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"""
🚀 Unified AI Copilot Platform Starting...
📊 Features Available:
   - AiSource Integration: {AISOURCE_AVAILABLE}
   - Automation: {AUTOMATION_AVAILABLE}
   - Multi-Agent Orchestration: {AISOURCE_AVAILABLE}
   - Model Management: {AISOURCE_AVAILABLE}

🌐 Server: http://{host}:{port}
📡 WebSocket: ws://{host}:{port}/ws
    """)
    
    uvicorn.run(app, host=host, port=port, log_level="info")
