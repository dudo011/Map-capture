@echo off
title Map Capture Web Server v4.1
echo ==================================================
echo   Starting Map Capture web server...
echo   Your browser will open automatically.
echo   (To close server: Close this window or Ctrl+C)
echo ==================================================
echo.
start http://localhost:3000/index.html
python server.py
if %errorlevel% neq 0 (
    echo.
    echo   [ERROR] Failed to start server.
    echo   Please make sure Python is installed.
    echo.
    pause
)
