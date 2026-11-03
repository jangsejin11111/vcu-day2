@echo off
cd /d "%~dp0"
python "%~dp0scripts\launch_workshop.py"
if errorlevel 1 (
  echo.
  echo Startup failed. Read the error above.
  pause
)
