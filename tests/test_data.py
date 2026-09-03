import pytest
import pandas as pd
import pandera as pa
from fraudguard.data.validation import validate_raw_data
from fraudguard.data.ingestion import split_temporal

def test_validate_raw_data_success():
    """Test that a valid dataframe passes validation."""
    valid_df = pd.DataFrame({
        "TransactionID": [1, 2],
        "isFraud": [0, 1],
        "TransactionDT": [1000, 2000],
        "TransactionAmt": [50.0, 150.0],
        "ProductCD": ["W", "H"],
        "card4": ["visa", "mastercard"],
        "card6": ["debit", "credit"],
        "DeviceType": ["desktop", "mobile"]
    })
    
    # Should not raise any exceptions
    validated_df = validate_raw_data(valid_df)
    assert len(validated_df) == 2

def test_validate_raw_data_failure():
    """Test that an invalid dataframe fails validation."""
    invalid_df = pd.DataFrame({
        "TransactionID": [-1],  # Invalid: negative
        "isFraud": [2],         # Invalid: not 0 or 1
        "TransactionDT": [1000],
        "TransactionAmt": [-50.0], # Invalid: negative amount
        "ProductCD": ["W"]
    })
    
    with pytest.raises(pa.errors.SchemaError):
        validate_raw_data(invalid_df)

def test_split_temporal():
    """Test that temporal split works correctly and prevents leakage."""
    df = pd.DataFrame({
        "TransactionID": [3, 1, 2, 4],
        "TransactionDT": [3000, 1000, 2000, 4000],
        "isFraud": [0, 1, 0, 0]
    })
    
    train_df, test_df = split_temporal(df, test_ratio=0.5)
    
    # Should be sorted by time
    assert train_df.iloc[0]["TransactionDT"] == 1000
    assert train_df.iloc[1]["TransactionDT"] == 2000
    assert test_df.iloc[0]["TransactionDT"] == 3000
    assert test_df.iloc[1]["TransactionDT"] == 4000
    
    # Check shapes
    assert len(train_df) == 2
    assert len(test_df) == 2
