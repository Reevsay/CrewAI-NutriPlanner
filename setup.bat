@echo off
REM CrewAI-NutriPlanner Setup Script for Windows

echo 🤖 CrewAI-NutriPlanner Setup
echo ============================

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Copy environment file
if not exist .env (
    echo ⚙️  Creating environment configuration...
    copy .env.example .env
    echo 📝 Please edit .env file and add your Google Gemini API key
    echo    Get your free API key from: https://makersuite.google.com/app/apikey
) else (
    echo ✅ Environment file already exists
)

REM Validate setup
echo 🧪 Validating setup...
python scripts\validate_setup.py

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file and add your Google Gemini API key
echo 2. Run: venv\Scripts\activate.bat
echo 3. Run: python -m src.main
echo.
echo 📚 Documentation: https://github.com/Reevsay/CrewAI-NutriPlanner
pause