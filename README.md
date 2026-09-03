# FraudGuard AI: Real-Time Fraud Detection System

FraudGuard AI is an end-to-end Machine Learning project designed to detect fraudulent financial transactions in real-time. It takes tabular transaction data and predicts the probability of fraud using a highly optimized XGBoost classifier served via a lightning-fast FastAPI REST API.

## 🚀 Key Features

* **Senior ML Engineering Preprocessing**: 
  * Implements `RobustScaler` for outlier immunity.
  * Replaces weak OneHotEncoding with `TargetEncoder` (Mean Encoding) to handle high-cardinality categorical features (like specific bank branches or email domains) by tracking their historical fraud rates.
  * Adds `MissingIndicator` signals to explicitly teach the model *when* data is missing, which is often a strong signal for fraud.
* **Optuna Hyperparameter Tuning**: 
  * The XGBoost model was mathematically optimized over 10 trials using the Optuna framework to maximize the **PR-AUC** (Precision-Recall Area Under Curve), which is the industry standard metric for highly imbalanced datasets like fraud.
* **Real-Time Gateway Architecture**: 
  * Designed to simulate a production "Payment Gateway". Features that require batch calculation or graph databases (like User Velocity metrics) were explicitly dropped in favor of a 25-feature payload that is instantly available at the time of the swipe.
* **FastAPI Serving**:
  * Pydantic schemas strictly validate the incoming JSON payloads to prevent pipeline crashes.
  * The model is cached in memory on startup, allowing predictions in <100 milliseconds.

## 📂 Project Structure

```
├── data/                  # Raw dataset (ignored by git due to size)
├── models/                # Serialized Champion Model (.pkl)
├── notebooks/             # EDA, Feature Selection, and MLflow/Optuna experiments
├── scripts/               # Utility scripts for executing pipeline steps
└── src/fraudguard/        # Core Python Package
    ├── api/               # FastAPI Application & Pydantic Schemas
    ├── data/              # Ingestion and split logic
    ├── features/          # Engineering pipeline (Imputers, Encoders, Scalers)
    └── models/            # XGBoost training wrapper
```

## 🛠️ Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/shubham-murtadak/Fraud-detection.git
cd Fraud-detection
```

2. **Create a virtual environment and install dependencies:**
```bash
python -m venv .venv
# Activate on Windows:
.\.venv\Scripts\activate
# Activate on Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 🌐 Running the FastAPI Server

To start the real-time inference server, run:
```bash
uvicorn src.fraudguard.api.main:app --reload
```
Once the server is running, navigate to `http://127.0.0.1:8000/docs` in your browser to interact with the Swagger UI and send test transactions!

## 🧪 Model Performance
The final deployed Champion Model achieved a **PR-AUC of 0.286** on a highly imbalanced testing dataset, significantly outperforming baseline tree models and complex Stacking Ensembles.
