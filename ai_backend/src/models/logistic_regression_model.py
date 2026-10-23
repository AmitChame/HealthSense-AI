"""
Logistic Regression Classifier Model Adapter.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from .base_model import BaseHealthSenseModel


class LogisticRegressionModel(BaseHealthSenseModel):
    """
    Logistic Regression implementation for multi-class food recommendation.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name="logistic_regression", config=config)
        max_iter = self.config.get('max_iter', 1000)
        class_weight = self.config.get('class_weight', 'balanced')
        random_state = self.config.get('random_state', 42)

        self.model = LogisticRegression(
            max_iter=max_iter,
            class_weight=class_weight,
            random_state=random_state,
            solver='lbfgs'
        )

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> 'LogisticRegressionModel':
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
        if not self.is_trained or not hasattr(self.model, 'coef_'):
            return {}
        # Use mean absolute coefficient across classes as importance proxy
        mean_coef = np.mean(np.abs(self.model.coef_), axis=0)
        total = np.sum(mean_coef) + 1e-8
        normalized = mean_coef / total
        return {
            name: float(imp)
            for name, imp in zip(self.feature_names, normalized)
        }
