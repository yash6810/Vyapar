@echo off
title Vyapar AI - Startup
color 0A

:: Ensure Python uses UTF-8 for encoding/decoding (important for ₹ symbol)
set PYTHONUTF8=1

echo.
echo  ╔══════════════════════════════════════╗
echo  ║        VYAPAR AI - Starting...       ║
echo  ╚══════════════════════════════════════╝
echo.

:: Check .env exists
if not exist ".env" (
    echo [ERROR] .env file not found! Copy .env.example to .env and add your GEMINI_API_KEY.
    pause
    exit /b 1
)

:: Start backend in a new window
echo [1/2] Starting Backend on http://localhost:8000 ...
start "Vyapar Backend" cmd /k "call .venv\Scripts\activate.bat && uvicorn backend.main:app --reload --port 8000"

:: Wait for backend to be ready
echo      Waiting for backend...
timeout /t 3 /nobreak > NUL

:: Start frontend in a new window
echo [2/2] Starting Frontend on http://localhost:3000 ...
start "Vyapar Frontend" cmd /k "cd frontend && npm start"

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   Backend:  http://localhost:8000    ║
echo  ║   API Docs: http://localhost:8000/docs ║
echo  ║   Frontend: http://localhost:3000    ║
echo  ╚══════════════════════════════════════╝
echo.
echo  Close both terminal windows to stop.
echo.
