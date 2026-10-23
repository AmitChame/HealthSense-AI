"""
Model Factory for HealthSense AI.
Instantiates and loads active recommendation models configured in model_config.yaml.
"""

from typing import Dict, Any, Optional
import os
import yaml
from pathlib import Path
from .base_model import BaseHealthSenseModel
from .model_registry import ModelRegistry


class ModelFactory:
    """
    Factory creating pluggable model instances based on configuration.
    """

    @staticmethod
    def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
        if config_path is None:
            # Default to config/model_config.yaml relative to project root
            base_dir = Path(__file__).resolve().parent.parent.parent
            config_path = str(base_dir / "config" / "model_config.yaml")

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}

    @classmethod
    def create_model(cls, model_name: Optional[str] = None, config: Optional[Dict[str, Any]] = None, config_path: Optional[str] = None) -> BaseHealthSenseModel:
        """
        Instantiates a model instance. If model_name is omitted, uses the active model from config.
        """
        full_config = cls.load_config(config_path)

        if not model_name:
            model_name = full_config.get('active', 'xgboost')

        model_cls = ModelRegistry.get(model_name)
        model_specific_config = config or full_config.get('models', {}).get(model_name, {})

        return model_cls(config=model_specific_config)

    @classmethod
    def load_active_model(cls, config_path: Optional[str] = None, project_root: Optional[str] = None) -> BaseHealthSenseModel:
        """
        Instantiates and loads the active model artifact configured in model_config.yaml.
        If artifact does not exist on disk, returns the un-fitted model instance.
        """
        if project_root is None:
            project_root = str(Path(__file__).resolve().parent.parent.parent)

        full_config = cls.load_config(config_path)
        active_name = full_config.get('active', 'xgboost')

        model = cls.create_model(active_name, config_path=config_path)

        model_conf = full_config.get('models', {}).get(active_name, {})
        rel_artifact_path = model_conf.get('artifact_path', f"artifacts/models/{active_name}.joblib")
        abs_artifact_path = os.path.join(project_root, rel_artifact_path)

        if os.path.exists(abs_artifact_path):
            model.load(abs_artifact_path)

        return model
