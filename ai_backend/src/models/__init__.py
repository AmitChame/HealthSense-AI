# Models package
from .base_model import BaseHealthSenseModel
from .model_registry import ModelRegistry
from .model_factory import ModelFactory

try:
    from .lightgbm_model import LightGBMModel
except Exception:
    LightGBMModel = None

try:
    from .xgboost_model import XGBoostModel
except Exception:
    XGBoostModel = None

try:
    from .random_forest_model import RandomForestModel
except Exception:
    RandomForestModel = None

try:
    from .logistic_regression_model import LogisticRegressionModel
except Exception:
    LogisticRegressionModel = None

__all__ = [
    'BaseHealthSenseModel',
    'LogisticRegressionModel',
    'RandomForestModel',
    'XGBoostModel',
    'LightGBMModel',
    'ModelRegistry',
    'ModelFactory',
]
