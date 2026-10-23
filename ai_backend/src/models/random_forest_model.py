"""
Random Forest Classifier Model Adapter.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from .base_model import BaseHealthSenseModel


class RandomForestModel(BaseHealthSenseModel):
    """
    Random Forest ensemble model adapter.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name="random_forest", config=config)
        n_estimators = self.config.get('n_estimators', 100)
        max_depth = self.config.get('max_depth', 12)
        class_weight = self.config.get('class_weight', 'balanced')
        random_state = self.config.get('random_state', 42)
        n_jobs = self.config.get('n_jobs', -1)

        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            class_weight=class_weight,
            random_state=random_state,
            n_jobs=n_jobs
        )

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> 'RandomForestModel':
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
