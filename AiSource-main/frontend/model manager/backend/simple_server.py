#!/usr/bin/env python3
"""
Simple Backend Server - Minimal version that works without external dependencies
"""

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class UnifiedBackendHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept, Authorization')
        self.send_header('Content-Type', 'application/json')
        
        if path == '/api/health' or path == '/health':
            self.send_response(200)
            self.end_headers()
            response = {
                "status": "healthy",
                "aisource_available": False,
                "automation_available": False,
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/models':
            self.send_response(200)
            self.end_headers()
            response = {
                "providers": [],
                "models": [],
                "message": "Backend running in minimal mode - install dependencies for full functionality"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/agents':
            self.send_response(200)
            self.end_headers()
            response = [
                {
                    "id": "architect",
                    "name": "Architect Agent",
                    "type": "architect",
                    "status": "offline",
                    "lastUpdate": datetime.now().isoformat(),
                    "capabilities": ["System Design", "Architecture Planning"],
                    "model": None
                }
            ]
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/agents/tasks':
            self.send_response(200)
            self.end_headers()
            response = []
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/automation/status':
            self.send_response(200)
            self.end_headers()
            response = {
                "isRunning": False,
                "agentStatus": {
                    "isActive": False,
                    "mode": "main",
                    "lastAction": "None",
                    "timestamp": datetime.now().isoformat()
                },
                "settings": {
                    "autonomousMode": False,
                    "acceptRate": 85,
                    "supervisorRate": 70,
                    "cycleTime": 180,
                    "hotkeysEnabled": True
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            response = {"error": "Not found", "path": path}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept, Authorization')
        self.send_header('Content-Type', 'application/json')
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            data = json.loads(post_data.decode()) if post_data else {}
        except:
            data = {}
            
        if path == '/api/automation/start':
            self.send_response(200)
            self.end_headers()
            response = {
                "status": "error",
                "message": "Automation requires full backend with dependencies installed"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/automation/stop':
            self.send_response(200)
            self.end_headers()
            response = {"status": "stopped", "message": "No automation was running"}
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/automation/accept' or path == '/api/automation/reject':
            action = path.split('/')[-1]
            self.send_response(200)
            self.end_headers()
            response = {
                "status": "error",
                "message": f"Manual {action} requires full backend with automation dependencies"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/agents/tasks':
            self.send_response(200)
            self.end_headers()
            response = {
                "id": str(int(time.time() * 1000)),
                "title": data.get("title", "New Task"),
                "description": data.get("description", ""),
                "status": "pending",
                "priority": data.get("priority", "medium"),
                "createdAt": datetime.now().isoformat(),
                "message": "Task created in minimal mode - agent orchestration requires full backend"
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            response = {"error": "Not found", "path": path}
            self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        if self.path != '/health' and self.path != '/api/health':
            super().log_message(format, *args)

def run_server(port=8000):
    """Run the simple backend server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, UnifiedBackendHandler)
    
    print(f"""
🚀 Simple Unified Backend Server Starting...
📊 Running in minimal mode (install FastAPI for full features)
🌐 Server: http://localhost:{port}
📡 Health: http://localhost:{port}/api/health
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
        httpd.server_close()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
