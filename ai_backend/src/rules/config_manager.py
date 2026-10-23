"""
Centralized Configuration Manager for HealthSense AI.
Handles loading and serving threshold and safety rule parameters from YAML.
"""

from typing import Dict, Any, Optional
import os
import yaml
from pathlib import Path


class HealthSenseConfigManager:
    """
    Singleton-style manager for centralized access to nutritional thresholds and safety rules.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HealthSenseConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_dir: Optional[str] = None):
        if self._initialized:
            return

        if config_dir is None:
            self.root = Path(__file__).resolve().parent.parent.parent
            self.config_dir = self.root / "config"
        else:
            self.config_dir = Path(config_dir)

        self.rules_config = self._load_yaml("rules_config.yaml")
        self.nutrition_thresholds = self._load_yaml("nutrition_thresholds.yaml")
        self._initialized = True

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        path = self.config_dir / filename
        if not path.exists():
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def get_health_condition_rule(self, rule_key: str) -> Dict[str, Any]:
        """
        Returns rule parameters from health_condition_rules.
        """
        rules = self.rules_config.get('health_condition_rules', {})
        return rules.get(rule_key, {})

    def get_nutrition_thresholds(self) -> Dict[str, Any]:
        return self.nutrition_thresholds.get('nutrition_thresholds', {})

    def get_grading_config(self) -> Dict[str, Any]:
        return self.nutrition_thresholds.get('food_grading', {})
