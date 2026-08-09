@echo off
title INTRACAPITAL - IBM Cloud Code Engine Deployer
echo =============================================================
echo        INTRACAPITAL IBM Cloud Code Engine Deployment
echo =============================================================
echo.

:: Step 1: Check for IBM Cloud CLI installation
where ibmcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] IBM Cloud CLI (ibmcloud) is not installed or not in system PATH.
    echo Please install the IBM Cloud CLI from: https://clis.cloud.ibm.com
    echo.
    pause
    exit /b 1
)

:: Step 2: User Authentication input
echo [1/5] Authentication Setup
echo -------------------------------------------------------------
set /p API_KEY="Enter your IBM Cloud API Key: "
if "%API_KEY%"=="" (
    echo [ERROR] API Key is required.
    pause
    exit /b 1
)

set /p REGION="Enter IBM Cloud target region [us-south]: "
if "%REGION%"=="" set REGION=us-south

set /p ResourceGroup="Enter target Resource Group [Default]: "
if "%ResourceGroup%"=="" set ResourceGroup=Default
echo.

:: Step 3: Logging into IBM Cloud
echo [2/5] Connecting to IBM Cloud...
call ibmcloud login --apikey "%API_KEY%" -r "%REGION%" -g "%ResourceGroup%"
if %errorlevel% neq 0 (
    echo [ERROR] IBM Cloud login failed. Verify your API Key, region and resource group.
    pause
    exit /b 1
)
echo.

:: Step 4: Ensure Code Engine Plugin is installed
echo [3/5] Installing Code Engine plugin if missing...
call ibmcloud plugin install code-engine -f
echo.

:: Step 5: Setup Code Engine Project
echo [4/5] Setting up Code Engine Project...
set PROJECT_NAME=intracapital-proj
call ibmcloud ce project create --name "%PROJECT_NAME%" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Project "%PROJECT_NAME%" already exists. Selecting it...
)
call ibmcloud ce project select --name "%PROJECT_NAME%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to select project "%PROJECT_NAME%".
    pause
    exit /b 1
)
echo.

:: Step 6: Deploy Backend API Gateway
echo [5/5] Deploying Backend Application...
echo Build Source: GitHub repository context directory "backend"
call ibmcloud ce app create --name intracapital-backend --src https://github.com/aadhyasharma270207-lang/intracapital2 --subpath backend --port 8000 --min 1 --max 2 --cpu 1 --memory 2G
if %errorlevel% neq 0 (
    echo [ERROR] Failed to deploy backend application.
    pause
    exit /b 1
)

:: Retrieve backend URL
echo.
echo [INFO] Retrieving Backend URL...
for /f "tokens=*" %%i in ('ibmcloud ce app get --name intracapital-backend --output url') do set BACKEND_URL=%%i
echo Backend URL resolved: %BACKEND_URL%
echo.

:: Deploy Frontend Dashboard
echo Deploying Frontend Application...
echo Build Source: GitHub repository context directory "frontend"
call ibmcloud ce app create --name intracapital-frontend --src https://github.com/aadhyasharma270207-lang/intracapital2 --subpath frontend --port 80 --env VITE_API_BASE_URL=%BACKEND_URL%
if %errorlevel% neq 0 (
    echo [ERROR] Failed to deploy frontend application.
    pause
    exit /b 1
)

:: Retrieve frontend URL
echo.
echo [INFO] Retrieving Frontend URL...
for /f "tokens=*" %%i in ('ibmcloud ce app get --name intracapital-frontend --output url') do set FRONTEND_URL=%%i
echo.
echo =============================================================
echo        DEPLOYMENT COMPLETED SUCCESSFULLY!
echo =============================================================
echo.
echo Frontend Live: %FRONTEND_URL%
echo Backend API Docs: %BACKEND_URL%/docs
echo.
pause
