@echo off
setlocal

:: Check if Python is installed
echo Checking for Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python is already installed.
) else (
    echo Python not found. Downloading installer
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.14.4/python-3.14.4-amd64.exe' -OutFile '%TEMP%\python-installer.exe'"

    echo Installing Python (please wait 1-2 minutes)
    "%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    del "%TEMP%\python-installer.exe" >nul 2>&1
    echo Python installed successfully.
)

echo.
echo Checking for Flask
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask
    python -m pip install flask --quiet
    echo Flask installed successfully.
) else (
    echo Flask is already installed.
)

echo.
echo ================================================
echo Starting Flask server on http://localhost:80
echo Press Ctrl + C to stop the server
echo ================================================
echo.

python main.py

pause