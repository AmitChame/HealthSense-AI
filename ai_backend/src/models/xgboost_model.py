"""
XGBoost Classifier Model Adapter.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import xgboost as xgb
from .base_model import BaseHealthSenseModel


class XGBoostModel(BaseHealthSenseModel):
    """
    XGBoost Gradient Boosting Classifier adapter.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name="xgboost", config=config)
        n_estimators = self.config.get('n_estimators', 100)
        max_depth = self.config.get('max_depth', 6)
        learning_rate = self.config.get('learning_rate', 0.1)
        subsample = self.config.get('subsample', 0.8)
        colsample_bytree = self.config.get('colsample_bytree', 0.8)
        random_state = self.config.get('random_state', 42)
        n_jobs = self.config.get('n_jobs', -1)

        self.model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=random_state,
            n_jobs=n_jobs,
            objective='multi:softprob',
            num_class=3,
            eval_metric='mlogloss'
        )

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> 'XGBoostModel':
        self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
        self.model.fit(X, y)
        self.is_trained = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model is not trained.")
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model is not trained.")
        return self.model.predict_proba(X)

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}
        return {
            name: float(imp)
            for name, imp in zip(self.feature_names, self.model.feature_importances_)
        }
