@echo off
echo ===================================================
echo Starting PredixAI Industrial Monitoring Platform...
echo ===================================================

start "PredixAI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak > nul

start "PredixAI Frontend" cmd /k "cd /d %~dp0frontend && npm.cmd run dev"

echo.
echo [BACKEND]  Running at: http://localhost:8000
echo [SWAGGER]  Docs at:    http://localhost:8000/docs
echo [FRONTEND] Running at: http://localhost:5173
echo.
echo Press any key to launch the live telemetry simulator...
pause > nul

python "%~dp0simulator\sensor_simulator.py" --engine 1 --interval 1.0 --cycles 50
