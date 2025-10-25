@echo off
echo ========================================
echo AI Customer Service Assistant
echo Starting Backend + LiveKit + Frontend
echo ========================================
echo.

echo Step 1: Installing Backend Dependencies...
pip install flask flask-cors python-dotenv
if %errorlevel% neq 0 (
    echo Error installing backend dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Starting Backend API + LiveKit Agent...
echo (LiveKit will auto-start if ENABLE_LIVEKIT_AGENT=true in .env)
start "Backend API + LiveKit" cmd /k python start_backend.py

timeout /t 5 /nobreak > nul

echo.
echo Step 3: Installing Frontend Dependencies...
cd frontend\react-app
call npm install
if %errorlevel% neq 0 (
    echo Error installing frontend dependencies
    pause
    exit /b 1
)

echo.
echo Step 4: Starting React Frontend...
start "React Frontend" cmd /k npm start

cd ..\..

echo.
echo ========================================
echo All services are starting!
echo ========================================
echo Backend API:      http://localhost:5000
echo React Frontend:   http://localhost:3000
echo LiveKit Agent:    Auto-started with backend
echo ========================================
echo.
echo Press any key to exit this window...
echo (The servers will continue running in separate windows)
pause > nul
