"""
SHAP Explainability Module for HealthSense AI.
Computes local feature contributions, top risk-increasing factors, and protective factors.
"""

from typing import Dict, Any, List, Optional
import numpy as np
try:
    import shap
except (ImportError, OSError):
    shap = None
from ..models.base_model import BaseHealthSenseModel


class HealthSenseShapExplainer:
    """
    SHAP-based feature importance and local instance attribution.
    """

    def __init__(self, model: BaseHealthSenseModel):
        self.model = model
        self.explainer = None
        self._init_explainer()

    def _init_explainer(self):
        try:
            if shap is None:
                return
            underlying = getattr(self.model, 'model', None)
            if underlying is None:
                return

            mname = self.model.get_model_name()
            if mname in ['random_forest', 'xgboost', 'lightgbm']:
                self.explainer = shap.TreeExplainer(underlying)
        except Exception:
            self.explainer = None

    def explain_instance(self, feature_vector: np.ndarray, feature_names: List[str], top_k: int = 5) -> Dict[str, Any]:
        """
        Computes top contributing features for a given single observation.
        """
        if feature_vector.ndim == 1:
            X = feature_vector.reshape(1, -1)
        else:
            X = feature_vector

        top_positive_risk: List[Dict[str, Any]] = []
        top_protective: List[Dict[str, Any]] = []

        if self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(X)
                # If multiclass output list, pick the class with highest probability or AVOID class (class 2)
                if isinstance(shap_values, list) and len(shap_values) == 3:
                    class_shap = shap_values[2][0] # Focus on AVOID risk contribution
                elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
                    class_shap = shap_values[0, :, 2]
                else:
                    class_shap = shap_values[0]

                # Pair with feature names
                contributions = []
                for fname, val, shap_val in zip(feature_names, X[0], class_shap):
                    contributions.append({
                        'feature': fname,
                        'value': float(val),
                        'shap_value': float(shap_val)
                    })

                # Sort by SHAP contribution
                contributions.sort(key=lambda x: x['shap_value'], reverse=True)

                for c in contributions[:top_k]:
                    if c['shap_value'] > 0:
                        top_positive_risk.append(c)

                for c in sorted(contributions, key=lambda x: x['shap_value'])[:top_k]:
                    if c['shap_value'] < 0:
                        top_protective.append(c)

            except Exception:
                pass

        # Fallback to feature importance from model if SHAP calculation was unavailable
        if not top_positive_risk:
            importances = self.model.get_feature_importance()
            sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:top_k]
            top_positive_risk = [{'feature': k, 'importance': round(v, 4)} for k, v in sorted_imp]

        return {
            'top_risk_factors': top_positive_risk,
            'top_protective_factors': top_protective
        }
