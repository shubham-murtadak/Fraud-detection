import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys

sys.path.append(str(Path.cwd().parent / "src"))

from fraudguard.data.ingestion import load_bank_data, split_temporal
from fraudguard.features.engineering import build_feature_pipeline
from fraudguard.models.training import train_xgboost
from sklearn.pipeline import Pipeline

print("1. Loading Data...")
data_dir = Path.cwd() / "data" / "raw"
df = load_bank_data(data_dir)

df_train, df_test = split_temporal(df, test_ratio=0.2)
X_train = df_train.drop(columns=['isFraud'])
y_train = df_train['isFraud'].values
X_test = df_test.drop(columns=['isFraud'])
y_test = df_test['isFraud'].values

gateway_numeric_features = ['TransactionAmt', 'dist1', 'dist2']
gateway_categorical_features = [
    'ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6',
    'addr1', 'addr2', 'P_emaildomain', 'R_emaildomain',
    'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9',
    'DeviceType', 'DeviceInfo'
]

gateway_numeric_features = [f for f in gateway_numeric_features if f in X_train.columns]
gateway_categorical_features = [f for f in gateway_categorical_features if f in X_train.columns]

print("2. Fitting Preprocessing Pipeline...")
pipeline = build_feature_pipeline(gateway_numeric_features, gateway_categorical_features)
X_train_processed = pipeline.fit_transform(X_train, y_train)
X_test_processed = pipeline.transform(X_test)

print("3. Training Champion XGBoost Model...")
# The absolute best hyperparameters found by Optuna in Trial 7
best_params = {
    'max_depth': 9, 
    'learning_rate': 0.2307895196484926, 
    'subsample': 0.9675615702591527, 
    'colsample_bytree': 0.8045779978175522, 
    'min_child_weight': 7
}

final_model = train_xgboost(
    X_train_processed, y_train, 
    X_val=X_test_processed, y_val=y_test,
    **best_params
)

print("4. Packaging and Saving Full Model...")
full_deployable_model = Pipeline(steps=[
    ('preprocessor', pipeline),
    ('classifier', final_model)
])

models_dir = Path.cwd() / "models"
models_dir.mkdir(exist_ok=True)
champion_path = models_dir / "gateway_champion.pkl"
joblib.dump(full_deployable_model, champion_path)

print(f"\\nSUCCESS! True Champion Model saved to: {champion_path}")
