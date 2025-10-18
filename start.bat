@echo off
echo 🤖 Multi-Tool Chat App - Quick Start
echo ====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\Lib\site-packages\fastapi\" (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found!
    echo Please create a .env file with your OpenAI API key.
    echo Example: OPENAI_API_KEY=your_api_key_here
    pause
    exit /b 1
)

REM Start the application
echo 🚀 Starting Multi-Tool Chat App...
echo Server will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python run.py

pause
