@echo off
REM Start the AI Pair Programming Assistant - Guided Setup
cd /d %~dp0

echo.
echo 🤖 AI Pair Programming Assistant
echo ================================

REM Check if debug mode is requested
if "%1"=="debug" (
    echo Starting in DEBUG mode with visible terminal...
    echo.
    goto debug_mode
)

echo Starting guided setup wizard...
echo.

REM Normal mode - hidden terminal for clean UX
where python >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Starting application...
    pythonw src/main.py
    goto :end
)

REM Try common Python installation paths
for %%p in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\pythonw.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\pythonw.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\pythonw.exe"
    "C:\Python313\pythonw.exe"
    "C:\Python312\pythonw.exe"
    "C:\Python311\pythonw.exe"
) do (
    if exist %%p (
        echo ✓ Found Python at %%p
        %%p src/main.py
        goto :end
    )
)

REM If all else fails, show helpful error
echo.
echo ❌ ERROR: Python not found!
echo.
echo Please install Python 3.8+ from: https://python.org/downloads
echo Make sure to check "Add Python to PATH" during installation.
echo.
echo Or run manually with: python src/main.py
echo.
echo To run in debug mode: start.bat debug
echo.
pause
goto :end

:debug_mode
REM Debug mode - visible terminal for troubleshooting
where python >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Starting with python in debug mode...
    python src/main.py
    pause
    goto :end
)

REM Try common Python installation paths for debug
for %%p in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
) do (
    if exist %%p (
        echo ✓ Found Python at %%p
        %%p src/main.py
        pause
        goto :end
    )
)

:end
echo.
echo Application should be running.
echo If you need to debug issues, run: start.bat debug
timeout /t 2 >nul
