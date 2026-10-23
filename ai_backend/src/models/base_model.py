"""
Base Machine Learning Model Interface for HealthSense AI.
All pluggable ML models must implement this standard interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import numpy as np
import os
import joblib


class BaseHealthSenseModel(ABC):
    """
    Abstract base class providing a uniform interface for all recommendation ML models.
    """

    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.config = config or {}
        self.model = None
        self.is_trained = False
        self.feature_names: List[str] = []
        self.classes: List[str] = ["RECOMMENDED", "CAUTION", "AVOID"]

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> 'BaseHealthSenseModel':
        """
        Trains the model on feature matrix X and target labels y.
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predicts discrete target labels (0=RECOMMENDED, 1=CAUTION, 2=AVOID).
        """
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predicts class probabilities shape (N, 3).
        """
        pass

    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Returns a dictionary mapping feature names to their relative importance scores.
        """
        pass

    def save(self, filepath: str):
        """
        Serializes the model, feature names, and metadata to disk.
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        payload = {
            'model_name': self.model_name,
            'model': self.model,
            'config': self.config,
            'is_trained': self.is_trained,
            'feature_names': self.feature_names,
            'classes': self.classes
        }
        joblib.dump(payload, filepath)

    def load(self, filepath: str) -> 'BaseHealthSenseModel':
        """
        Loads a serialized model artifact from disk.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model artifact not found at {filepath}")
        payload = joblib.load(filepath)
        self.model_name = payload.get('model_name', self.model_name)
        self.model = payload.get('model')
        self.config = payload.get('config', {})
        self.is_trained = payload.get('is_trained', True)
        self.feature_names = payload.get('feature_names', [])
        self.classes = payload.get('classes', self.classes)
        return self

    def get_model_name(self) -> str:
        return self.model_name

    def get_hyperparameters(self) -> Dict[str, Any]:
        return self.config
