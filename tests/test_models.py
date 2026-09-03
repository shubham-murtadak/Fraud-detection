import numpy as np
from sklearn.datasets import make_classification
from fraudguard.models.training import train_logistic_regression, train_lightgbm
from fraudguard.models.evaluation import evaluate_model

def test_model_training_and_evaluation():
    """Test that models can train and evaluate on synthetic dummy data."""
    # Create synthetic data that is separable
    X_train, y_train = make_classification(
        n_samples=100, n_features=5, n_informative=3, n_redundant=0, 
        n_classes=2, weights=[0.9, 0.1], random_state=42
    )
    
    # 1. Test Logistic Regression
    lr_model = train_logistic_regression(X_train, y_train)
    assert lr_model is not None
    
    # Predict probabilities
    lr_probs = lr_model.predict_proba(X_train)[:, 1]
    
    # Evaluate
    lr_metrics = evaluate_model(y_train, lr_probs)
    assert 'roc_auc' in lr_metrics
    assert 'pr_auc' in lr_metrics
    assert 'f1_score' in lr_metrics
    
    # Simple synthetic data should be easily separable
    assert lr_metrics['roc_auc'] > 0.5
    
    # 2. Test LightGBM
    lgb_model = train_lightgbm(X_train, y_train, scale_pos_weight=1.0)
    assert lgb_model is not None
    
    lgb_probs = lgb_model.predict_proba(X_train)[:, 1]
    lgb_metrics = evaluate_model(y_train, lgb_probs)
    
    assert 'roc_auc' in lgb_metrics
    assert lgb_metrics['roc_auc'] > 0.5
