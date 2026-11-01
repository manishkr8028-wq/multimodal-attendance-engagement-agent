@echo off
echo =====================================================================
echo    MULTIMODAL ATTENDANCE ^& ENGAGEMENT AGENT
echo    Generative AI with Google Cloud - Privacy Preserving System
echo =====================================================================
echo.
echo [1/3] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH! Please install Python 3.10+
    pause
    exit /b
)

echo.
echo [2/3] Initializing SQLite database and default demo records...
python -c "import database; database.init_db(); print('SQLite Database verified!')"

echo.
echo [3/3] Launching Live Classroom Monitor...
echo Opening your web browser to http://localhost:5000...
start http://localhost:5000?autostart=true

echo.
echo =====================================================================
echo  Application is running!
echo  Open your camera, verify your attendance, and explore the AI HUD.
echo  Press Ctrl+C in this window to stop the server when done.
echo =====================================================================
echo.
python app.py
pause
