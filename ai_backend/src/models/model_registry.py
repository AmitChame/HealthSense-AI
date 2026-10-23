"""
Central Model Registry for HealthSense AI.
"""

from typing import Dict, Type, List, Optional
from .base_model import BaseHealthSenseModel


class ModelRegistry:
    """
    Registry for dynamic model discovery and instantiation.
    """

    _REGISTRY: Dict[str, Type[BaseHealthSenseModel]] = {}
    _RESOLVERS = {
        'lightgbm': lambda: __import__('src.models.lightgbm_model', fromlist=['LightGBMModel']).LightGBMModel,
        'xgboost': lambda: __import__('src.models.xgboost_model', fromlist=['XGBoostModel']).XGBoostModel,
        'random_forest': lambda: __import__('src.models.random_forest_model', fromlist=['RandomForestModel']).RandomForestModel,
        'logistic_regression': lambda: __import__('src.models.logistic_regression_model', fromlist=['LogisticRegressionModel']).LogisticRegressionModel,
    }

    @classmethod
    def register(cls, name: str, model_cls: Type[BaseHealthSenseModel]):
        """
        Registers a new custom model class.
        """
        cls._REGISTRY[name.lower()] = model_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseHealthSenseModel]:
        """
        Retrieves model class by key.
        """
        key = name.lower()
        if key in cls._REGISTRY:
            return cls._REGISTRY[key]
        if key in cls._RESOLVERS:
            cls._REGISTRY[key] = cls._RESOLVERS[key]()
            return cls._REGISTRY[key]
        raise KeyError(f"Unknown model '{name}'. Registered models: {cls.list_models()}")

    @classmethod
    def list_models(cls) -> List[str]:
        """
        Lists all available registered model keys.
        """
        all_keys = set(cls._REGISTRY.keys()).union(cls._RESOLVERS.keys())
        return sorted(list(all_keys))
