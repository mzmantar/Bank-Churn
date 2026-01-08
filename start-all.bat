@echo off
REM Bank Churn MLOps - Start All Services (batch version)
REM Démarre l'API FastAPI, Streamlit et MLflow en parallèle

setlocal enabledelayedexpansion

set venvPath=C:\Users\moham\bank-churn-mlops-azure\.venv\Scripts
set projectRoot=C:\Users\moham\bank-churn-mlops-azure

color 0B
cls
echo.
echo ========================================
echo Bank Churn MLOps - Starting All Services
echo ========================================
echo.

REM Vérifier le venv
if not exist "%venvPath%" (
    color 0C
    echo ERROR: Virtual environment not found at %venvPath%
    pause
    exit /b 1
)

REM Charger .env (optionnel)
if exist "%projectRoot%\.env" (
    echo Loading environment variables from .env...
    for /f "delims==" %%A in (type "%projectRoot%\.env") do (
        set %%A
    )
)

REM Ports par défaut
if not defined API_PORT set API_PORT=8000
if not defined STREAMLIT_PORT set STREAMLIT_PORT=8501
if not defined MLFLOW_PORT set MLFLOW_PORT=5000

REM 1. API FastAPI
echo.
echo Starting API FastAPI (port %API_PORT%)...
start "FastAPI - Port %API_PORT%" /D "%projectRoot%" "%venvPath%\python.exe" -m uvicorn api.main:app --host 0.0.0.0 --port %API_PORT%
timeout /t 2 /nobreak

REM 2. Streamlit
echo Starting Streamlit (port %STREAMLIT_PORT%)...
start "Streamlit - Port %STREAMLIT_PORT%" /D "%projectRoot%" "%venvPath%\streamlit.exe" run streamlit/streamlit_app.py --server.port %STREAMLIT_PORT%
timeout /t 2 /nobreak

REM 3. MLflow
echo Starting MLflow (port %MLFLOW_PORT%)...
start "MLflow - Port %MLFLOW_PORT%" /D "%projectRoot%" "%venvPath%\mlflow.exe" server --host 0.0.0.0 --port %MLFLOW_PORT%
timeout /t 2 /nobreak

REM Afficher les URLs
echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo URLs:
echo   API FastAPI: http://localhost:%API_PORT%
echo   Docs: http://localhost:%API_PORT%/docs
echo   Streamlit: http://localhost:%STREAMLIT_PORT%
echo   MLflow: http://localhost:%MLFLOW_PORT%
echo.
echo.
echo Press any key to exit this launcher (services will keep running)...
pause >nul
