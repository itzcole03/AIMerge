@echo off
cd /d "%~dp0"
echo Starting Unified Backend Server...
echo Installing dependencies...
pip install fastapi uvicorn websockets pydantic python-multipart aiofiles pyautogui Pillow
echo Starting server on port 8000...
cd backend
python unified_server.py
pause
