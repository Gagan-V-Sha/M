@echo off
setlocal
set "ROOT=%~dp0..\.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"

echo      eTD Builder Launcher


REM --- Backend Setup ---
echo.
echo [1/4] Checking Backend Configuration...
cd /d "%ROOT%\backend"

if not exist ".env" (
    echo Creating .env from example...
    copy "..\.env.example" ".env" >nul
)

set "ACTIVATE_CMD="
if exist "venv\Scripts\activate.bat" (
    echo Using local virtual environment - venv...
    set "ACTIVATE_CMD=venv\Scripts\activate.bat"
) else if exist "C:\gspr_env\Scripts\activate.bat" (
    echo Using virtual environment at C:\gspr_env...
    set "ACTIVATE_CMD=C:\gspr_env\Scripts\activate.bat"
) else (
    echo Creating Python Virtual Environment at venv...
    python -m venv venv
    if not exist "venv\Scripts\activate.bat" (
        echo ERROR: Failed to create virtual environment. Please check if Python is installed and in your PATH.
        pause
        exit /b 1
    )
    set "ACTIVATE_CMD=venv\Scripts\activate.bat"
    echo Installing backend dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

echo Activating Virtual Environment...
call %ACTIVATE_CMD%

echo Verifying dependencies and ensuring MinerU is installed...
pip install -r requirements.txt

echo Creating admin user if it does not exist...
python scripts\setup\create_admin.py

REM --- Playwright Chromium for PDF export ---
echo.
echo Ensuring Playwright Chromium is available for PDF export...
set "PLAYWRIGHT_BROWSERS_PATH=%CD%\.playwright-browsers"
if not exist "%PLAYWRIGHT_BROWSERS_PATH%" mkdir "%PLAYWRIGHT_BROWSERS_PATH%"
set "PLAYWRIGHT_CHROMIUM_USE_HEADLESS_SHELL=0"

REM Only download if full Chromium (chrome.exe) is missing — skip on later launches
set "CHROME_FOUND="
for /d %%D in ("%PLAYWRIGHT_BROWSERS_PATH%\chromium-*") do (
    if exist "%%D\chrome-win64\chrome.exe" set "CHROME_FOUND=1"
)
if defined CHROME_FOUND (
    echo Playwright Chromium already installed.
) else (
    echo Installing Playwright Chromium into %PLAYWRIGHT_BROWSERS_PATH% ...
    python -m playwright install chromium
    if errorlevel 1 (
        echo WARNING: Playwright Chromium install failed. PDF export may not work until you run:
        echo   backend\scripts\install_playwright_chromium.bat
    ) else (
        echo Playwright Chromium installed.
    )
)


REM --- Frontend Setup ---
echo.
echo [2/4] Checking Frontend Configuration...
cd /d "%ROOT%\frontend"

if not exist "node_modules" (
    echo Installing Node Modules...
    call npm install
)

REM --- Start Services ---
echo.
echo [3/4] Starting Services...
cd /d "%ROOT%"

start "eTD Backend" /D "%ROOT%\backend" cmd /k "call %ACTIVATE_CMD% && set PLAYWRIGHT_BROWSERS_PATH=%ROOT%\backend\.playwright-browsers&& set PLAYWRIGHT_CHROMIUM_USE_HEADLESS_SHELL=0&& python -m uvicorn app.main:app --host 0.0.0.0 --reload --port 8000"
timeout /t 5 >nul
start "eTD Frontend" /D "%ROOT%\frontend" cmd /k "npm run dev -- --host"

echo.
echo ==========================================
echo      Services Started!
echo ==========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop the services (closes windows)...
pause >nul

taskkill /FI "WINDOWTITLE eq eTD Backend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq eTD Frontend" /F >nul 2>&1
