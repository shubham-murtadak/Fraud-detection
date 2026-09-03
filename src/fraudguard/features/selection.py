import pandas as pd
import numpy as np
import logging
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import RandomForestClassifier

logger = logging.getLogger(__name__)

class RigorousFeatureSelector(BaseEstimator, TransformerMixin):
    """
    A production-grade feature selector that filters features through a strict funnel:
    1. Missingness Filter (drops columns with > X% missing values)
    2. Zero Variance Filter (drops constants)
    3. Tree-based Feature Importance (keeps the top N most predictive features)
    """
    
    def __init__(self, max_missing_ratio=0.90, top_n_features=50, random_state=42):
        self.max_missing_ratio = max_missing_ratio
        self.top_n_features = top_n_features
        self.random_state = random_state
        
        self.selected_features_ = None
        self._tree_model = RandomForestClassifier(
            n_estimators=50, 
            max_depth=5, 
            random_state=self.random_state, 
            n_jobs=-1
        )

    def fit(self, X: pd.DataFrame, y: np.ndarray = None):
        logger.info(f"Starting feature selection funnel. Initial features: {X.shape[1]}")
        
        # Step 1: Missingness Filter
        missing_ratios = X.isnull().mean()
        valid_missing_cols = missing_ratios[missing_ratios <= self.max_missing_ratio].index.tolist()
        logger.info(f"Features after Missingness Filter (<{self.max_missing_ratio*100}%): {len(valid_missing_cols)}")
        
        # Step 2: Zero Variance Filter
        # Only keep columns where the number of unique values > 1
        X_tmp = X[valid_missing_cols]
        nunique = X_tmp.nunique()
        valid_var_cols = nunique[nunique > 1].index.tolist()
        logger.info(f"Features after Zero-Variance Filter: {len(valid_var_cols)}")
        
        # Step 3: Tree-based Feature Importance
        # To run a tree, we need to temporarily impute NaNs in the remaining columns
        logger.info("Training shallow Random Forest to extract multivariate feature importance...")
        X_imputed = X_tmp[valid_var_cols].fillna(X_tmp[valid_var_cols].median())
        
        self._tree_model.fit(X_imputed, y)
        
        # Extract importances
        importances = self._tree_model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': valid_var_cols,
            'importance': importances
        }).sort_values(by='importance', ascending=False)
        
        # Keep top N
        self.selected_features_ = feature_importance_df.head(self.top_n_features)['feature'].tolist()
        logger.info(f"Selected Top {len(self.selected_features_)} highly predictive features.")
        
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.selected_features_ is None:
            raise ValueError("The selector has not been fitted yet!")
        
        # Drop columns not in selected_features_ (but keep those that might be missing in X but exist in selected? No, X should have them)
        # Handle case where X during inference might miss some columns (though it shouldn't)
        missing_cols = [c for c in self.selected_features_ if c not in X.columns]
        if missing_cols:
            logger.warning(f"Warning: {len(missing_cols)} selected features are missing in the input DataFrame.")
            
        cols_to_keep = [c for c in self.selected_features_ if c in X.columns]
        return X[cols_to_keep].copy()
