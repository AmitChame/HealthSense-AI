"""
LightGBM Classifier Model Adapter.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import lightgbm as lgb
from .base_model import BaseHealthSenseModel


class LightGBMModel(BaseHealthSenseModel):
    """
    LightGBM Gradient Boosting Framework adapter.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name="lightgbm", config=config)
        n_estimators = self.config.get('n_estimators', 100)
        num_leaves = self.config.get('num_leaves', 31)
        learning_rate = self.config.get('learning_rate', 0.1)
        random_state = self.config.get('random_state', 42)
        n_jobs = self.config.get('n_jobs', -1)
        verbose = self.config.get('verbose', -1)

        self.model = lgb.LGBMClassifier(
            n_estimators=n_estimators,
            num_leaves=num_leaves,
            learning_rate=learning_rate,
            random_state=random_state,
            n_jobs=n_jobs,
            objective='multiclass',
            num_class=3,
            verbose=verbose
        )

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> 'LightGBMModel':
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
        total = np.sum(self.model.feature_importances_) + 1e-8
        normalized = self.model.feature_importances_ / total
        return {
            name: float(imp)
            for name, imp in zip(self.feature_names, normalized)
        }
