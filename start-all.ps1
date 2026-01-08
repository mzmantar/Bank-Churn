# Bank Churn MLOps - Start All Services
# Démarre l'API FastAPI, Streamlit et MLflow en parallèle

$venvPath = "C:/Users/moham/bank-churn-mlops-azure/.venv/Scripts"
$projectRoot = "C:\Users\moham\bank-churn-mlops-azure"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Bank Churn MLOps - Starting All Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que le venv existe
if (-not (Test-Path $venvPath)) {
    Write-Host "[ERROR] Virtual environment not found at $venvPath" -ForegroundColor Red
    exit 1
}

# Charger les variables d'environnement depuis .env
$envFile = Join-Path $projectRoot ".env"
if (Test-Path $envFile) {
    Write-Host "[INFO] Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Ports par défaut
$apiPort = if ($env:API_PORT) { $env:API_PORT } else { "8000" }
$streamlitPort = if ($env:STREAMLIT_PORT) { $env:STREAMLIT_PORT } else { "8501" }
$mlflowPort = if ($env:MLFLOW_PORT) { $env:MLFLOW_PORT } else { "5000" }

# 1. Lancer l'API FastAPI
Write-Host "[START] API FastAPI on port $apiPort..." -ForegroundColor Green
Start-Process -FilePath "$venvPath/python.exe" `
    -ArgumentList "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", $apiPort `
    -WorkingDirectory $projectRoot `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# 2. Lancer Streamlit
Write-Host "[START] Streamlit on port $streamlitPort..." -ForegroundColor Green
Start-Process -FilePath "$venvPath/streamlit.exe" `
    -ArgumentList "run", "streamlit/streamlit_app.py", "--server.port", $streamlitPort `
    -WorkingDirectory $projectRoot `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# 3. Lancer MLflow
Write-Host "[START] MLflow on port $mlflowPort..." -ForegroundColor Green
Start-Process -FilePath "$venvPath/mlflow.exe" `
    -ArgumentList "server", "--host", "0.0.0.0", "--port", $mlflowPort `
    -WorkingDirectory $projectRoot `
    -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] All services started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  [API]      http://localhost:$apiPort" -ForegroundColor Blue
Write-Host "  [Docs]     http://localhost:$apiPort/docs" -ForegroundColor Blue
Write-Host "  [Streamlit] http://localhost:$streamlitPort" -ForegroundColor Blue
Write-Host "  [MLflow]   http://localhost:$mlflowPort" -ForegroundColor Blue
Write-Host ""
Write-Host "[INFO] Windows can be closed individually. Use Ctrl+C to stop a service." -ForegroundColor Yellow
Write-Host ""

