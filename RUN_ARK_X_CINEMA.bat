@echo off
setlocal
cd /d "%~dp0"
python Engine\orchestrator.py
set "EXIT_CODE=%ERRORLEVEL%"
echo.
echo ARK X Cinema exited with code %EXIT_CODE%.
pause
exit /b %EXIT_CODE%
