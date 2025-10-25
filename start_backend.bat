@echo off
echo ========================================
echo Starting Backend API + LiveKit Agent
echo ========================================
echo.
echo Installing Python dependencies...
pip install flask flask-cors python-dotenv
echo.
echo Starting backend server (with auto LiveKit agent)...
echo.
echo Note: LiveKit agent will auto-start if configured in .env
echo       Set ENABLE_LIVEKIT_AGENT=true to enable voice
echo.
python start_backend.py
