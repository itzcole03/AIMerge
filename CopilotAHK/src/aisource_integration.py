"""
AiSource Integration Bridge
Connects CopilotAHK automation with AiSource multi-agent system
"""

import requests
import json
import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import sys

class AiSourceClient:
    """Client for communicating with AiSource API"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.connected = False
        
    def test_connection(self) -> bool:
        """Test connection to AiSource system"""
        try:
            response = self.session.get(f"{self.base_url}/status", timeout=5)
            self.connected = response.status_code == 200
            return self.connected
        except Exception as e:
            print(f"AiSource connection failed: {e}")
            self.connected = False
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get AiSource system status"""
        try:
            response = self.session.get(f"{self.base_url}/api/system/status")
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def analyze_code_suggestion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code suggestion using AiSource agents"""
        try:
            payload = {
                "task_type": "code_analysis",
                "context": context,
                "agents": ["architect", "qa_analyst"],
                "priority": "high"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/agents/analyze",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            return {"recommendation": "manual", "confidence": 0, "reason": f"API error: {response.status_code}"}
            
        except Exception as e:
            return {"recommendation": "manual", "confidence": 0, "reason": f"Analysis failed: {e}"}
    
    def start_orchestrated_task(self, task_description: str, project_context: str) -> str:
        """Start an orchestrated task with multiple agents"""
        try:
            payload = {
                "task": task_description,
                "context": project_context,
                "mode": "autonomous",
                "max_iterations": 5
            }
            
            response = self.session.post(
                f"{self.base_url}/api/orchestrator/start",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("task_id", "unknown")
            return None
            
        except Exception as e:
            print(f"Failed to start orchestrated task: {e}")
            return None
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of an orchestrated task"""
        try:
            response = self.session.get(f"{self.base_url}/api/orchestrator/status/{task_id}")
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "message": "Task not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class CopilotAiSourceBridge:
    """Main integration bridge between CopilotAHK and AiSource"""
    
    def __init__(self):
        self.aisource = AiSourceClient()
        self.integration_active = False
        self.decision_history = []
        self.current_project_context = ""
        self.learning_mode = True
        
    def initialize(self) -> bool:
        """Initialize the integration bridge"""
        print("🔗 Initializing CopilotAHK ↔ AiSource Integration Bridge...")
        
        # Test AiSource connection
        if self.aisource.test_connection():
            print("✅ AiSource connection established")
            
            # Get system status
            status = self.aisource.get_system_status()
            print(f"📊 AiSource Status: {status.get('status', 'unknown')}")
            
            self.integration_active = True
            return True
        else:
            print("❌ AiSource connection failed - running in standalone mode")
            self.integration_active = False
            return False
    
    def enhanced_decision_analysis(self, suggestion_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced decision making using AiSource agents"""
        if not self.integration_active:
            return {"recommendation": "manual", "confidence": 0, "reason": "AiSource not available"}
        
        print("🧠 Analyzing suggestion with AiSource agents...")
        
        # Prepare context for analysis
        analysis_context = {
            "code_suggestion": suggestion_context.get("suggestion", ""),
            "file_path": suggestion_context.get("file", ""),
            "project_context": self.current_project_context,
            "conversation_history": suggestion_context.get("history", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        # Get analysis from AiSource
        analysis = self.aisource.analyze_code_suggestion(analysis_context)
        
        # Store decision for learning
        if self.learning_mode:
            self.decision_history.append({
                "timestamp": datetime.now().isoformat(),
                "context": analysis_context,
                "analysis": analysis,
                "final_decision": None  # Will be updated when user makes decision
            })
        
        return analysis
    
    def update_project_context(self, context: str):
        """Update current project context"""
        self.current_project_context = context
        print(f"📝 Project context updated ({len(context)} characters)")
    
    def start_autonomous_development(self, task_description: str) -> Optional[str]:
        """Start autonomous development task using AiSource orchestration"""
        if not self.integration_active:
            print("❌ Cannot start autonomous development - AiSource not available")
            return None
        
        print(f"🚀 Starting autonomous development: {task_description}")
        
        task_id = self.aisource.start_orchestrated_task(
            task_description, 
            self.current_project_context
        )
        
        if task_id:
            print(f"✅ Autonomous task started with ID: {task_id}")
            return task_id
        else:
            print("❌ Failed to start autonomous task")
            return None
    
    def monitor_autonomous_task(self, task_id: str) -> Dict[str, Any]:
        """Monitor progress of autonomous development task"""
        if not self.integration_active:
            return {"status": "error", "message": "AiSource not available"}
        
        return self.aisource.get_task_status(task_id)
    
    def record_decision_outcome(self, decision_index: int, actual_decision: str, outcome: str):
        """Record the outcome of a decision for learning purposes"""
        if self.learning_mode and decision_index < len(self.decision_history):
            self.decision_history[decision_index]["final_decision"] = actual_decision
            self.decision_history[decision_index]["outcome"] = outcome
            
            # Save learning data
            self.save_learning_data()
    
    def save_learning_data(self):
        """Save decision history for machine learning"""
        try:
            learning_file = "data/decision_learning.json"
            os.makedirs("data", exist_ok=True)
            
            with open(learning_file, "w") as f:
                json.dump(self.decision_history, f, indent=2)
                
            print(f"💾 Learning data saved ({len(self.decision_history)} decisions)")
        except Exception as e:
            print(f"❌ Failed to save learning data: {e}")
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        if not self.integration_active:
            return {"status": "disconnected", "decisions": 0, "accuracy": 0}
        
        total_decisions = len(self.decision_history)
        correct_decisions = len([d for d in self.decision_history 
                               if d.get("final_decision") == d.get("analysis", {}).get("recommendation")])
        
        accuracy = (correct_decisions / total_decisions * 100) if total_decisions > 0 else 0
        
        return {
            "status": "connected",
            "aisource_status": self.aisource.get_system_status(),
            "total_decisions": total_decisions,
            "correct_decisions": correct_decisions,
            "accuracy": round(accuracy, 1),
            "learning_mode": self.learning_mode
        }


class IntegratedAutomationController:
    """Enhanced automation controller with AiSource integration"""
    
    def __init__(self):
        self.bridge = CopilotAiSourceBridge()
        self.autonomous_mode = False
        self.current_task_id = None
        
    def initialize(self) -> bool:
        """Initialize the integrated automation system"""
        print("🎯 Initializing Integrated Automation Controller...")
        return self.bridge.initialize()
    
    def enhanced_afk_mode(self, project_context: str = "") -> bool:
        """Start enhanced AFK mode with AiSource integration"""
        if project_context:
            self.bridge.update_project_context(project_context)
        
        if not self.bridge.integration_active:
            print("⚠️ Running in basic AFK mode (AiSource not available)")
            return False
        
        print("🚀 Starting Enhanced AFK Mode with AI Agent Integration")
        
        # Start autonomous development task
        task_description = "Monitor and enhance the current development session with intelligent code suggestions and automated decision making"
        self.current_task_id = self.bridge.start_autonomous_development(task_description)
        
        if self.current_task_id:
            self.autonomous_mode = True
            print("✅ Enhanced AFK Mode active - AI agents are monitoring and assisting")
            return True
        else:
            print("❌ Failed to start enhanced AFK mode")
            return False
    
    def make_intelligent_decision(self, suggestion_context: Dict[str, Any]) -> str:
        """Make intelligent accept/reject decision using AiSource analysis"""
        if not self.bridge.integration_active:
            return "manual"  # Fall back to manual decision
        
        analysis = self.bridge.enhanced_decision_analysis(suggestion_context)
        
        recommendation = analysis.get("recommendation", "manual")
        confidence = analysis.get("confidence", 0)
        reason = analysis.get("reason", "No reason provided")
        
        print(f"🤖 AI Analysis: {recommendation} (confidence: {confidence}%)")
        print(f"💭 Reason: {reason}")
        
        # Only auto-decide if confidence is high enough
        if confidence >= 80:
            return recommendation
        else:
            print("⚠️ Low confidence - deferring to manual decision")
            return "manual"
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the integrated system"""
        status = {
            "integration_bridge": self.bridge.get_integration_stats(),
            "autonomous_mode": self.autonomous_mode,
            "current_task": self.current_task_id
        }
        
        if self.current_task_id:
            task_status = self.bridge.monitor_autonomous_task(self.current_task_id)
            status["task_status"] = task_status
        
        return status


# Global integration instance
integration_controller = IntegratedAutomationController()

def initialize_integration() -> bool:
    """Initialize the AiSource integration"""
    return integration_controller.initialize()

def get_intelligent_decision(suggestion_context: Dict[str, Any]) -> str:
    """Get intelligent decision for code suggestion"""
    return integration_controller.make_intelligent_decision(suggestion_context)

def start_enhanced_afk(project_context: str = "") -> bool:
    """Start enhanced AFK mode with AI integration"""
    return integration_controller.enhanced_afk_mode(project_context)

def get_integration_status() -> Dict[str, Any]:
    """Get integration status"""
    return integration_controller.get_status() 