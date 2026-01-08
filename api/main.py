import os
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from pathlib import Path
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import sys

# allow importing project-level modules (e.g., drift.py)
APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from drift import (
    load_reference,
    load_current,
    simulate_drift,
    run_report,
    DATA_PATH,
)

MODEL_PATH = APP_DIR / "model" / "model.pkl"
FRONTEND_DIR = APP_DIR / "app"
REPORTS_DIR = APP_DIR / "reports"

app = FastAPI(title="Bank Churn Prediction API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
if REPORTS_DIR.exists():
    # Serve drift reports so you can open the HTML output in browser
    app.mount("/reports", StaticFiles(directory=str(REPORTS_DIR), html=True), name="reports")

class ChurnFeatures(BaseModel):
    age: float
    credit_score: float
    balance: float
    tenure: float
    products: float
    is_active: float

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run: python train.py")
    return joblib.load(MODEL_PATH)

try:
    model = load_model()
except FileNotFoundError as e:
    print(f"Warning: {e}")
    model = None

FEATURES_ORDER = ["age", "credit_score", "balance", "tenure", "products", "is_active"]

@app.post("/predict")
def predict(features: ChurnFeatures):
    if model is None:
        return {"error": "Model not loaded. Run train.py first"}
    
    x = [[
        features.age,
        features.credit_score,
        features.balance,
        features.tenure,
        features.products,
        features.is_active
    ]]
    pred = model.predict(x)[0]
    proba = float(model.predict_proba(x)[0][1])
    return {"churn": int(pred), "churn_probability": proba, "features_order": FEATURES_ORDER}

@app.get("/health")
def health():
    return {"status": "ok", "message": "Churn API is running"}

@app.get("/", response_class=HTMLResponse)
def home():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return "<h1>Bank Churn Prediction API</h1><p>API is running. Use /docs for API docs.</p>"
    api_url = os.getenv("API_URL", "https://bank-churn.proudhill-33366174.germanywestcentral.azurecontainerapps.io").rstrip("/")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Inject API_URL into the front HTML by replacing the placeholder
    return html.replace("__API_URL__", api_url)


@app.get("/drift")
def drift(simulate: bool = False):
    """Run a data drift report.
    - Set simulate=true to apply synthetic drift on current data.
    Returns JSON summary and paths to HTML/JSON reports.
    """
    df = pd.read_csv(DATA_PATH)
    reference = load_reference(df)
    current = load_current(df)
    if simulate:
        current = simulate_drift(current)

    result = run_report(reference, current)
    return result
