from pathlib import Path
import pandas as pd
import numpy as np

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "data" / "churn.csv"
REPORTS_DIR = APP_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

FEATURES = ["age", "credit_score", "balance", "tenure", "products", "is_active"]

def load_reference(df: pd.DataFrame) -> pd.DataFrame:
    # On prend une partie comme référence (train)
    return df.sample(frac=0.6, random_state=42)[FEATURES].copy()

def load_current(df: pd.DataFrame) -> pd.DataFrame:
    # On prend une autre partie comme "current"
    # (tu peux aussi prendre un vrai fichier prod si tu en as)
    return df.sample(frac=0.4, random_state=7)[FEATURES].copy()

def simulate_drift(current: pd.DataFrame) -> pd.DataFrame:
    # ✅ Simulation simple de drift : on change les distributions
    drifted = current.copy()

    # exemple: age augmente
    drifted["age"] = drifted["age"] + 8

    # credit_score baisse un peu
    drifted["credit_score"] = drifted["credit_score"] - 50

    # balance augmente beaucoup (log-normal style)
    drifted["balance"] = drifted["balance"] * 1.5

    # is_active plus souvent 0
    drifted["is_active"] = np.where(np.random.rand(len(drifted)) < 0.7, 0, drifted["is_active"])

    # clamp (éviter valeurs négatives)
    drifted["credit_score"] = drifted["credit_score"].clip(lower=0)
    drifted["balance"] = drifted["balance"].clip(lower=0)
    drifted["age"] = drifted["age"].clip(lower=0)

    return drifted

def run_report(reference: pd.DataFrame, current: pd.DataFrame) -> dict:
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)

    html_path = REPORTS_DIR / "drift_report.html"
    json_path = REPORTS_DIR / "drift_report.json"

    report.save_html(str(html_path))
    report.save_json(str(json_path))

    # Résumé : drift detecté ?
    summary = report.as_dict()
    # Evidently met souvent un champ "dataset_drift" dans le résultat preset
    # On va essayer de le lire proprement :
    dataset_drift = None
    try:
        dataset_drift = summary["metrics"][0]["result"]["dataset_drift"]
    except Exception:
        pass

    return {
        "dataset_drift": dataset_drift,
        "html_report": str(html_path),
        "json_report": str(json_path),
    }

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)

    reference = load_reference(df)
    current = load_current(df)

    # ✅ Sans drift (normal)
    result_normal = run_report(reference, current)
    print("=== Drift normal (sans simulation) ===")
    print(result_normal)

    # ✅ Avec drift simulé
    current_drifted = simulate_drift(current)
    result_drifted = run_report(reference, current_drifted)
    print("=== Drift simulé (doit détecter) ===")
    print(result_drifted)
