@echo off
echo Starting INTRACAPITAL Streamlit Frontend...

if "%BACKEND_URL%"=="" (
    set BACKEND_URL=http://127.0.0.1:8000
)
if "%FRONTEND_HOST%"=="" (
    set FRONTEND_HOST=127.0.0.1
)
if "%FRONTEND_PORT%"=="" (
    set FRONTEND_PORT=8501
)

:: Verify port availability
python -c "import os, socket, sys; host=os.getenv('FRONTEND_HOST', '127.0.0.1'); port=int(os.getenv('FRONTEND_PORT', '8501')); s=socket.socket(); s.bind((host, port)); s.close()" 2>nul
if %errorlevel% neq 0 (
    echo ==================================================
    echo ❌ ERROR: Frontend port %FRONTEND_PORT% is already occupied on %FRONTEND_HOST%!
    echo To resolve this, you can:
    echo 1. Kill the process occupying this port.
    echo 2. Set a different port using the FRONTEND_PORT environment variable.
    echo    Example: set FRONTEND_PORT=8510
    echo ==================================================
    pause
    exit /b 1
)

:: Activate virtual environment
if exist "D:\intracapital_venv\Scripts\activate.bat" (
    call "D:\intracapital_venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo [WARNING] Virtual environment not found. Using system python.
)

streamlit run app.py --server.address %FRONTEND_HOST% --server.port %FRONTEND_PORT% --server.headless true
pause
