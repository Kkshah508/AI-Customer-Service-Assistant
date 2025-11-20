@echo off
echo ========================================
echo Starting React Frontend Only
echo ========================================
echo.

echo Installing Frontend Dependencies...
cd frontend\react-app

if not exist node_modules (
    echo Installing npm packages...
    call npm install
    if %errorlevel% neq 0 (
        echo Error installing dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting React Development Server...
echo Backend API should be running at: http://localhost:5000
echo Frontend will start at: http://localhost:3000
echo.

call npm start

cd ..\..
