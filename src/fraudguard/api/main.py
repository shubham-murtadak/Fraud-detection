import uuid
import joblib
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging

from .schemas import TransactionRequest, FraudResponse

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FraudGuard AI Gateway",
    description="Real-time Machine Learning API for detecting fraudulent transactions.",
    version="1.0.0"
)

# Global variable to hold our machine learning pipeline
model_pipeline = None

# We use the lifespan/startup event to load the model ONCE when the server starts.
# Loading it inside the route would add a massive delay to every single request.
@app.on_event("startup")
async def load_model():
    global model_pipeline
    
    # Path to the absolute final Champion model saved in Notebook 6
    model_path = Path.cwd() / "models" / "gateway_champion.pkl"
    
    if not model_path.exists():
        logger.error(f"Model not found at {model_path}. Please run Notebook 6 first!")
        return
    
    try:
        logger.info(f"Loading Machine Learning pipeline from {model_path}...")
        model_pipeline = joblib.load(model_path)
        logger.info("Model pipeline loaded successfully! API is ready for real-time inference.")
    except Exception as e:
        logger.error(f"Failed to load the model: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to FraudGuard AI. The system is online. Visit /docs for the interactive API documentation."}

@app.post("/predict", response_model=FraudResponse)
async def predict_fraud(transaction: TransactionRequest):
    if model_pipeline is None:
        raise HTTPException(status_code=503, detail="Machine Learning model is not loaded or is currently unavailable.")
    
    # 1. Generate a unique ID for tracing (if not provided by frontend)
    tx_id = str(uuid.uuid4())
    
    try:
        # 2. Convert the Pydantic schema to a Python dictionary, then to a Pandas DataFrame.
        # Our scikit-learn pipeline expects a DataFrame with 1 row and 25 columns.
        tx_dict = transaction.model_dump()
        df_input = pd.DataFrame([tx_dict])
        
        # 3. Real-Time Inference!
        # predict_proba returns a 2D array: [[prob_class_0, prob_class_1]]
        # We only care about prob_class_1 (the probability of Fraud)
        probabilities = model_pipeline.predict_proba(df_input)
        fraud_prob = float(probabilities[0][1])
        
        # 4. Apply Business Logic Threshold
        # For our champion model, let's use a standard 0.5 threshold for now.
        threshold = 0.5
        action = "BLOCK" if fraud_prob >= threshold else "ALLOW"
        
        logger.info(f"Transaction {tx_id} processed: Prob={fraud_prob:.4f} -> {action}")
        
        # 5. Return JSON Response
        return FraudResponse(
            transaction_id=tx_id,
            fraud_probability=fraud_prob,
            action=action
        )
        
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error during model inference: {str(e)}")
