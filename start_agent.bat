@echo off
echo Starting Voice AI Agent...
echo ===================================

:: Start Backend in a new window
echo Starting FastAPI Backend...
start "Voice Agent Backend" cmd /k "cd /d "%~dp0backend" && set PATH=%%PATH%%;C:\Users\LP-043\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin && .venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000"

:: Start Frontend in a new window
echo Starting Vite Frontend...
start "Voice Agent Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Both servers are starting in separate windows.
echo Frontend should be available at: http://localhost:3000
echo Backend API at: http://127.0.0.1:8000
echo.
echo Note: Make sure the Ollama app is running on your computer!
pause
