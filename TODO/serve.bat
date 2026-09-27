@echo off
rem TODO list viewer: build, serve on http://localhost:8000/ and open the browser.
rem Close this window (or press Ctrl+C) to stop.
cd /d "%~dp0"
where python >nul 2>nul || (echo Python 3.11+ is required. & pause & exit /b 1)
python scripts\serve.py --open %*
if errorlevel 1 pause
