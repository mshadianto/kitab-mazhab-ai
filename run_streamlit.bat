@echo off
echo ========================================
echo  Kitab Imam Mazhab AI - Web Version
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if streamlit is installed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check .env file
if not exist ".env" (
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo WARNING: Please edit .env file and add your GROQ_API_KEY!
    echo.
    pause
    exit /b 1
)

echo.
echo Starting Streamlit server...
echo.
echo Open browser: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo.

streamlit run streamlit_app.py --server.port 8501 --server.address localhost