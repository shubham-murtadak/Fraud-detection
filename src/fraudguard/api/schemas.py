from pydantic import BaseModel, Field
from typing import Optional

class TransactionRequest(BaseModel):
    """
    Pydantic schema defining the exact 25 features required by the Gateway Model.
    All fields (except TransactionAmt) are optional because our robust pipeline handles missing data.
    """
    # Numeric Features
    TransactionAmt: float = Field(..., description="Transaction amount in USD")
    dist1: Optional[float] = Field(None, description="Distance feature 1")
    dist2: Optional[float] = Field(None, description="Distance feature 2")
    
    # Categorical Features (Cards & Addresses)
    ProductCD: Optional[str] = None
    card1: Optional[float] = None  # card1 is high cardinality, but often parsed as numeric ID
    card2: Optional[float] = None
    card3: Optional[float] = None
    card4: Optional[str] = None
    card5: Optional[float] = None
    card6: Optional[str] = None
    addr1: Optional[float] = None
    addr2: Optional[float] = None
    
    # Emails
    P_emaildomain: Optional[str] = None
    R_emaildomain: Optional[str] = None
    
    # M-Features (Matches)
    M1: Optional[str] = None
    M2: Optional[str] = None
    M3: Optional[str] = None
    M4: Optional[str] = None
    M5: Optional[str] = None
    M6: Optional[str] = None
    M7: Optional[str] = None
    M8: Optional[str] = None
    M9: Optional[str] = None
    
    # Device Features
    DeviceType: Optional[str] = None
    DeviceInfo: Optional[str] = None

class FraudResponse(BaseModel):
    """
    Pydantic schema for the API output.
    """
    transaction_id: str = Field(..., description="A unique ID for this transaction request")
    fraud_probability: float = Field(..., description="Calculated probability of fraud (0.0 to 1.0)")
    action: str = Field(..., description="'BLOCK' or 'ALLOW' based on the decision threshold")
