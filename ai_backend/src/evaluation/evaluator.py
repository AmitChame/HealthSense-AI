"""
Model Evaluation Metrics Suite.
Calculates Accuracy, Macro & Per-class Precision/Recall/F1, False Negative Rate for High-Risk categories, and Inference Latency.
"""

from typing import Dict, Any, List
import time
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_auc_score
)
from ..models.base_model import BaseHealthSenseModel


class ModelEvaluator:
    """
    Evaluates classification models with specific focus on clinical safety (minimizing False Negatives).
    """

    CLASS_NAMES = ["RECOMMENDED", "CAUTION", "AVOID"]

    def evaluate_model(self, model: BaseHealthSenseModel, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Executes evaluation on test dataset and returns dictionary of metrics.
        """
        # Inference time benchmark
        start_time = time.perf_counter()
        y_pred = model.predict(X_test)
        inference_time_total = time.perf_counter() - start_time
        avg_latency_ms = (inference_time_total / len(X_test)) * 1000.0 if len(X_test) > 0 else 0.0

        # Predict probabilities if supported
        try:
            y_proba = model.predict_proba(X_test)
            # Multiclass ROC-AUC (One-vs-Rest)
            if len(np.unique(y_test)) == len(self.CLASS_NAMES):
                roc_auc = float(roc_auc_score(y_test, y_proba, multi_class='ovr', average='macro'))
            else:
                roc_auc = None
        except Exception:
            y_proba = None
            roc_auc = None

        # Metrics
        acc = float(accuracy_score(y_test, y_pred))
        prec_macro = float(precision_score(y_test, y_pred, average='macro', zero_division=0))
        rec_macro = float(recall_score(y_test, y_pred, average='macro', zero_division=0))
        f1_macro = float(f1_score(y_test, y_pred, average='macro', zero_division=0))

        # Per-class metrics
        prec_per_class = precision_score(y_test, y_pred, average=None, zero_division=0)
        rec_per_class = recall_score(y_test, y_pred, average=None, zero_division=0)
        f1_per_class = f1_score(y_test, y_pred, average=None, zero_division=0)

        per_class_metrics = {}
        for i, cname in enumerate(self.CLASS_NAMES):
            per_class_metrics[cname] = {
                'precision': float(prec_per_class[i]) if i < len(prec_per_class) else 0.0,
                'recall': float(rec_per_class[i]) if i < len(rec_per_class) else 0.0,
                'f1': float(f1_per_class[i]) if i < len(f1_per_class) else 0.0
            }

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2]).tolist()

        # False Negative Rate for AVOID (Class 2): Actual was AVOID but predicted RECOMMENDED or CAUTION
        avoid_total = sum(cm[2]) if len(cm) > 2 else 0
        avoid_missed = (cm[2][0] + cm[2][1]) if len(cm) > 2 else 0
        fnr_avoid = float(avoid_missed / avoid_total) if avoid_total > 0 else 0.0

        return {
            'model_name': model.get_model_name(),
            'accuracy': round(acc, 4),
            'precision_macro': round(prec_macro, 4),
            'recall_macro': round(rec_macro, 4),
            'f1_macro': round(f1_macro, 4),
            'roc_auc': round(roc_auc, 4) if roc_auc is not None else None,
            'false_negative_rate_avoid': round(fnr_avoid, 4),
            'avg_latency_ms': round(avg_latency_ms, 3),
            'per_class': per_class_metrics,
            'confusion_matrix': cm
        }
