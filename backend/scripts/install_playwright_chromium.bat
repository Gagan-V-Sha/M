@echo off
REM Install Playwright Chromium into backend\.playwright-browsers (used by PDF export)
cd /d "%~dp0.."
set PLAYWRIGHT_BROWSERS_PATH=%CD%\.playwright-browsers
if not exist "%PLAYWRIGHT_BROWSERS_PATH%" mkdir "%PLAYWRIGHT_BROWSERS_PATH%"
echo Installing Chromium to %PLAYWRIGHT_BROWSERS_PATH%
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo Failed. Activate your venv first, e.g. C:\gspr_env\Scripts\activate
    pause
    exit /b 1
)
echo Done. Restart the backend, then try Export PDF again.
pause
