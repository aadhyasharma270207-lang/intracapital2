@echo off
echo Starting INTRACAPITAL Backend Server...

:: Check environment variables
if "%FASTAPI_INTERNAL_API_KEY%"=="" (
    set FASTAPI_INTERNAL_API_KEY=hackathon_secret_token_2026
)
if "%BACKEND_HOST%"=="" (
    set BACKEND_HOST=127.0.0.1
)
if "%BACKEND_PORT%"=="" (
    set BACKEND_PORT=8000
)

:: Verify port availability
python -c "import os, socket, sys; host=os.getenv('BACKEND_HOST', '127.0.0.1'); port=int(os.getenv('BACKEND_PORT', '8000')); s=socket.socket(); s.bind((host, port)); s.close()" 2>nul
if %errorlevel% neq 0 (
    echo ==================================================
    echo ❌ ERROR: Backend port %BACKEND_PORT% is already occupied on %BACKEND_HOST%!
    echo To resolve this, you can:
    echo 1. Kill the process occupying this port.
    echo 2. Set a different port using the BACKEND_PORT environment variable.
    echo    Example: set BACKEND_PORT=8002
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

python -m uvicorn backend.api:app --host %BACKEND_HOST% --port %BACKEND_PORT%
pause
