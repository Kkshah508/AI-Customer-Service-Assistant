@echo off
echo ============================================================
echo LiveKit Model Downloader
echo ============================================================
echo.
echo This script will download required models for the LiveKit agent
echo Download size: ~200MB
echo.

if exist "Venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call Venv\Scripts\activate.bat
)

echo Starting download...
echo.

python download_livekit_models.py

echo.
echo ============================================================
pause
