@echo off
title Vyapar App Runner

echo Starting all services for Vyapar App...

REM This script assumes you have run 'npm install' in the 'frontend' directory at least once.

REM Activate virtual environment and start backend services in new windows
echo Starting Backend Services...
start "HF Server" cmd /k "call .\.venv\Scripts\activate.bat && echo Starting HF Server... && python backend/hf_server.py"
start "ASR Service" cmd /k "call .\.venv\Scripts\activate.bat && echo Starting ASR Service... && python backend/asr_service.py"
start "Intent Classifier" cmd /k "call .\.venv\Scripts\activate.bat && echo Starting Intent Classifier... && python backend/intent_classifier.py"
start "Backend Main" cmd /k "call .\.venv\Scripts\activate.bat && echo Starting Backend Main... && uvicorn backend.main:app --reload --port 8000"

REM Wait a few seconds for backend services to initialize before launching the frontend
echo Waiting for backend services to start...
timeout /t 5 /nobreak > NUL

REM Start frontend in the current window
echo Starting Frontend...
cd frontend
call npm start

echo All services initiated.
