import pandas as pd
import numpy as np
from fraudguard.features.engineering import build_feature_pipeline, CustomFeatureEngineer

def test_custom_feature_engineer():
    """Test that our custom features are correctly engineered."""
    df = pd.DataFrame({
        'id_01': [10.0, np.nan, 20.0],
        'TransactionDT': [86400, 3600, 172800] # 1 day, 1 hour, 2 days
    })
    
    engineer = CustomFeatureEngineer()
    df_out = engineer.transform(df)
    
    assert 'Has_Identity_Data' in df_out.columns
    assert df_out['Has_Identity_Data'].tolist() == [1, 0, 1]
    
    assert 'Days' in df_out.columns
    assert df_out['Days'].tolist() == [1.0, 0.0, 2.0]
    
    assert 'Hour' in df_out.columns
    assert df_out['Hour'].tolist() == [0.0, 1.0, 0.0]

def test_build_feature_pipeline():
    """Test that the pipeline correctly imputes, scales, and encodes."""
    # Note: custom engineer adds Days and Hour, so we can include them in numeric_features
    df_train = pd.DataFrame({
        'TransactionAmt': [100.0, np.nan, 300.0],
        'TransactionDT': [0, 86400, 172800],
        'ProductCD': ['W', 'H', np.nan]
    })
    
    numeric_features = ['TransactionAmt', 'Days', 'Hour']
    categorical_features = ['ProductCD']
    
    pipeline = build_feature_pipeline(numeric_features, categorical_features)
    
    # Fit and transform
    X_out = pipeline.fit_transform(df_train)
    
    # 3 rows, should have features for:
    # TransactionAmt (scaled), Days (scaled), Hour (scaled), ProductCD (OHE: H, W, Missing)
    # Number of columns = 3 + 3 = 6
    assert X_out.shape == (3, 6)
    
    # Check that median imputation worked for TransactionAmt (median of 100, 300 is 200)
    # The scaled value of the imputed 200 should be the middle value (0.0)
    # The standard deviation of [100, 200, 300] is 100.
    # Scaled values should be [-1.22, 0, 1.22]
    # Check the second row (imputed)
    assert np.isclose(X_out[1, 0], 0.0)
