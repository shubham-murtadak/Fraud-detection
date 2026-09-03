import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin

class CustomFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    A custom transformer to build specific domain features, 
    such as capturing the missingness of identity data.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_out = X.copy()
        
        # 1. Missing Identity Data Signal
        if 'id_01' in X_out.columns:
            X_out['Has_Identity_Data'] = X_out['id_01'].notnull().astype(int)
        
        # 2. Extract basic time features from TransactionDT (which is in seconds)
        # Assuming the reference time starts at 0, we can extract day and hour proxies.
        if 'TransactionDT' in X_out.columns:
            # Days since start
            X_out['Days'] = np.floor(X_out['TransactionDT'] / (60*60*24))
            # Hour of day (assuming midnight start)
            X_out['Hour'] = np.floor((X_out['TransactionDT'] % (60*60*24)) / (60*60))
        # 3. Log1p Transform for heavily skewed financial data
        if 'TransactionAmt' in X_out.columns:
            X_out['TransactionAmt_Log'] = np.log1p(X_out['TransactionAmt'])
            X_out = X_out.drop(columns=['TransactionAmt'])
            
        return X_out

def cast_to_string(x):
    """Helper function to cast categorical columns to string (avoids lambda PicklingError)"""
    return x.astype(str)

def build_feature_pipeline(numeric_features: list[str], categorical_features: list[str]) -> Pipeline:
    """
    Builds a robust, production-grade scikit-learn preprocessing pipeline.
    """
    
    # If the user passed 'TransactionAmt', replace it with 'TransactionAmt_Log' because CustomFeatureEngineer renamed it
    numeric_features = [f if f != 'TransactionAmt' else 'TransactionAmt_Log' for f in numeric_features]
    
    from sklearn.preprocessing import RobustScaler, TargetEncoder, FunctionTransformer
    
    # 1. Pipeline for numeric features: Impute missing with median (add missing indicator!), then Robust scale (immune to outliers)
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median', add_indicator=True)),
        ('scaler', RobustScaler())
    ])

    # 2. Pipeline for categorical features: Impute with 'Missing' (add indicator), cast to string, then TargetEncode
    # TargetEncoder replaces categories (like Bank IDs) with their historical fraud rate. Massive predictive boost over OrdinalEncoder.
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Missing', add_indicator=True)),
        ('cast_string', FunctionTransformer(cast_to_string)),
        ('target_encode', TargetEncoder(target_type='binary', smooth="auto"))
    ])

    # 3. Combine them using ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop' # Drop any columns not explicitly specified (e.g. TransactionID)
    )

    # 4. Full Pipeline: Custom Features -> Preprocessor
    full_pipeline = Pipeline(steps=[
        ('custom_features', CustomFeatureEngineer()),
        ('preprocessor', preprocessor)
    ])
    
    return full_pipeline
