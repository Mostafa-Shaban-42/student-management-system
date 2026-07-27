@echo off
title Student Management System
echo ===================================================
echo     Launching Student Management System V2...
echo ===================================================
echo.

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install dependencies
echo Checking and installing requirements...
pip install -r requirements.txt --quiet

:: Run Streamlit App
echo.
echo Starting Application...
echo ===================================================
streamlit run app.py

pause