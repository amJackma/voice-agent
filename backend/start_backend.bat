@echo off
set PATH=%PATH%;C:\Users\LP-043\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
