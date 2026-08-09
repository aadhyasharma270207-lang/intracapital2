@echo off
echo ==================================================
echo LAUNCHING INTRACAPITAL VENTURE INTELLIGENCE
echo ==================================================

start "INTRACAPITAL Backend Server" cmd /k run_backend.bat
start "INTRACAPITAL Streamlit Dashboard" cmd /k run_frontend.bat

echo BOTH SERVERS ARE LAUNCHING...
echo Backend: http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:8501
echo ==================================================
