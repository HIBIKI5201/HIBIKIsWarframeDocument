@echo off
rem Story viewer: build, serve on http://localhost:8001/ (also reachable from phones on the same Wi-Fi) and open the browser.
rem Close this window (or press Ctrl+C) to stop.
cd /d "%~dp0"
where python >nul 2>nul || (echo Python 3.8+ is required. & pause & exit /b 1)
python scripts\serve.py --open --lan %*
if errorlevel 1 pause
