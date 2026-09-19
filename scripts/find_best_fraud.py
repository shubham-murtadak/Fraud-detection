import sys
from pathlib import Path
sys.path.append(str(Path.cwd() / 'src'))
from fraudguard.data.ingestion import load_bank_data
import joblib, pandas as pd, json

df = load_bank_data(Path.cwd() / 'data' / 'raw')
fraud_df = df[df['isFraud'] == 1].copy()

features = ['TransactionAmt', 'dist1', 'dist2', 'ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6', 'addr1', 'addr2', 'P_emaildomain', 'R_emaildomain', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'DeviceType', 'DeviceInfo']

model = joblib.load('models/gateway_champion.pkl')
probs = model.predict_proba(fraud_df[features])[:, 1]
fraud_df['prob'] = probs

best_fraud = fraud_df.sort_values('prob', ascending=False).iloc[0]
sample = best_fraud[features].to_dict()

print(f"Best Prob: {best_fraud['prob']}")
print(json.dumps({k: (None if pd.isna(v) else v) for k, v in sample.items()}, indent=2))
