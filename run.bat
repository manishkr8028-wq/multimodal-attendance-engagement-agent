@echo off
echo =====================================================================
echo    MULTIMODAL ATTENDANCE & ENGAGEMENT AGENT
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
echo [3/3] Starting Flask Application Server on http://localhost:5000...
echo Open your web browser to: http://localhost:5000
echo.
python app.py
pause
