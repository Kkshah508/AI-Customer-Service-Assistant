@echo off
echo ========================================
echo AI Customer Service Assistant
echo Starting with LiveKit Voice Agent
echo ========================================
echo.

echo Checking LiveKit Configuration...
if not exist .env (
    echo ERROR: .env file not found
    echo Please copy .env.example to .env and configure your credentials
    pause
    exit /b 1
)

echo.
echo Step 1: Installing Backend Dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Starting Backend API + LiveKit Agent...
start "Backend + LiveKit" cmd /k python start_backend.py

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
echo All services started successfully!
echo ========================================
echo Backend API:      http://localhost:5000
echo React Frontend:   http://localhost:3000
echo LiveKit Agent:    Running in backend window
echo ========================================
echo.
echo Make sure your .env file has:
echo - ENABLE_LIVEKIT_AGENT=true
echo - LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
echo - OPENAI_API_KEY
echo.
echo Press any key to exit this window...
pause > nul
