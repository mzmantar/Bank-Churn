# Bank Churn MLOps

Application complète pour prédire le churn bancaire avec FastAPI, Streamlit et MLflow.

## Architecture

```
bank-churn-mlops-azure/
├── api/                 # API FastAPI
├── app/                 # Frontend HTML/CSS
├── streamlit/          # Interface Streamlit
├── data/               # Données d'entrainement
├── model/              # Modèle sauvegardé
├── train.py            # Script d'entrainement
├── drift.py            # Détection de drift
├── Dockerfile          # API container
├── Dockerfile.mlflow   # MLflow container
├── Dockerfile.streamlit # Streamlit container
├── docker-compose.yml  # Orchestration
├── requirements.txt    # Dépendances Python
└── .env               # Variables d'environnement
```

## Services

### 1. API FastAPI (Port 8000)
- Endpoint POST `/predict` - Prédiction
- Endpoint GET `/health` - Santé du service
- Endpoint GET `/` - Interface web
- Documentation interactive: http://localhost:8000/docs

### 2. Streamlit (Port 8501)
- Interface utilisateur interactive
- Appelle l'API pour les prédictions
- URL: http://localhost:8501

### 3. MLflow (Port 5000)
- Tracking des expériences
- Gestion des artifacts
- URL: http://localhost:5000

## Installation & Utilisation

### Prérequis
- Docker & Docker Compose (Option 1)
- OU Python 3.12+ avec pip (Option 2)
- PowerShell ou Command Prompt pour Windows

### Option 1: Docker Compose (Recommandé)

```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Logs
docker-compose logs -f api
docker-compose logs -f streamlit
docker-compose logs -f mlflow
```

Services disponibles:
- API: http://localhost:8000
- Streamlit: http://localhost:8501
- MLflow: http://localhost:5000

### Option 2: Python Local

#### Étape 1 : Installation et entraînement
```bash
# Installer les dépendances
pip install -r requirements.txt

# Entrainer le modèle
python train.py
```

#### Étape 2 : Lancer tous les services à la fois

**PowerShell :**
```powershell
# Lancer le script (tous les services en parallèle)
.\start-all.ps1
```

**Command Prompt (batch) :**
```cmd
start-all.bat
```

#### Étape 3 (optionnel) : Lancer les services individuellement

**API FastAPI :**
```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Streamlit (dans un autre terminal) :**
```bash
streamlit run streamlit/streamlit_app.py --server.port 8501
```

**MLflow (dans un autre terminal) :**
```bash
mlflow server --host 0.0.0.0 --port 5000
```

## Configuration

Variables d'environnement dans `.env`:
```dotenv
# API Configuration
API_PORT=8000
API_URL=http://localhost:8000

# Streamlit Configuration
STREAMLIT_PORT=8501

# MLflow Configuration
MLFLOW_PORT=5000
MLFLOW_TRACKING_URI=http://localhost:5000
```

**Pour Azure :** Remplace les URLs locales par tes endpoints Azure :
```dotenv
API_URL=https://votre-api.azurewebsites.net
MLFLOW_TRACKING_URI=https://votre-mlflow.azurewebsites.net
```

**Important :** L'API injecte automatiquement `API_URL` dans le frontend HTML (`index.html`), ce qui permet au Streamlit et à la page web de connaître l'endpoint API, même en production.

## Workflow MLOps

1. **Entrainement**: `python train.py`
   - Charge les données depuis `data/churn.csv`
   - Entraine le modèle
   - Sauvegarde dans `model/model.pkl`
   - Log les métriques dans MLflow

2. **Prédiction**: API `/predict`
   - Charge le modèle
   - Fait les prédictions
   - Retourne churn + probabilité

3. **Monitoring**: Détection de drift
   - Script `drift.py` pour analyser
   - Comparer les distributions

## Données

Format attendu pour `data/churn.csv`:
```
age,credit_score,balance,tenure,products,is_active,churn
40,650,5000,5,2,1,0
35,720,10000,3,1,1,1
...
```

Features requis:
- age (int)
- credit_score (int)
- balance (float)
- tenure (int)
- products (int)
- is_active (0/1)
- churn (0/1) - target

## API Endpoints

### POST /predict
```json
{
  "age": 40,
  "credit_score": 650,
  "balance": 5000,
  "tenure": 5,
  "products": 2,
  "is_active": 1
}
```

Response:
```json
{
  "churn": 0,
  "churn_probability": 0.23,
  "features_order": ["age", "credit_score", "balance", "tenure", "products", "is_active"]
}
```

### GET /health
Response: `{"status": "ok", "message": "Churn API is running"}`

### GET /
Retourne l'interface web HTML

## Troubleshooting

### Modèle non trouvé
```bash
# Entrainer d'abord
python train.py

# Puis relancer les services
./start-all.ps1  # PowerShell
# ou
start-all.bat    # Command Prompt
```

### Port déjà utilisé
Modifie les ports dans `.env` :
```dotenv
API_PORT=8001
STREAMLIT_PORT=8502
MLFLOW_PORT=5001
```

### Logs d'erreur Docker
```bash
docker-compose logs -f [service_name]
```

### Erreurs lors du lancement des services
- Vérifie que le venv est activé : `.\venv\Scripts\Activate.ps1`
- Assure-toi que `requirements.txt` est à jour : `pip install -r requirements.txt`
- Vérifie que le port n'est pas occupé : `netstat -ano | findstr :8000`

## Notes

- Les modèles et données ne sont pas versionés (dans `.gitignore`)
- MLflow utilise SQLite local
- Les artifacts sont sauvegardés dans `/mlflow/artifacts`
- CORS activé pour l'API (développement)
- Dépendances Python : Pydantic v2, FastAPI 0.104.1, MLflow 2.14.3, Evidently 0.5.0 (compatible Python 3.12)

## Scripts de démarrage

- `start-all.ps1` : PowerShell script pour lancer tous les services en parallèle
- `start-all.bat` : Batch script pour lancer tous les services en parallèle (Windows)
