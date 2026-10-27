@echo off
REM SafeCommute AI - Windows launcher (double-click)
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Creating the virtual environment...
    python -m venv .venv || (echo Python 3.11+ is required: https://www.python.org/downloads/ & pause & exit /b 1)
)
.venv\Scripts\python.exe -m pip install -q -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
pause
