"""
Model Comparison and Selection Engine.
Empirically benchmarks trained models and selects the optimal model artifact based on safety-weighted criteria.
"""

from typing import List, Dict, Any, Tuple, Optional
import os
import json
import pandas as pd
from pathlib import Path


class ModelComparator:
    """
    Compares real evaluation metrics from multiple models and selects the best candidate.
    """

    def __init__(self, artifacts_dir: Optional[str] = None):
        if artifacts_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.artifacts_dir = base_dir / "artifacts"
        else:
            self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def compare_and_select(self, evaluation_results: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """
        Takes evaluation dicts from all models, creates comparison table,
        identifies the best model empirically, and saves comparison artifacts.
        """
        if not evaluation_results:
            raise ValueError("No evaluation results provided for comparison.")

        # Build comparison summary table
        rows = []
        for res in evaluation_results:
            rows.append({
                'model_name': res['model_name'],
                'accuracy': res['accuracy'],
                'f1_macro': res['f1_macro'],
                'precision_macro': res['precision_macro'],
                'recall_macro': res['recall_macro'],
                'fnr_avoid': res['false_negative_rate_avoid'],
                'roc_auc': res.get('roc_auc'),
                'avg_latency_ms': res['avg_latency_ms'],
                'avoid_recall': res.get('per_class', {}).get('AVOID', {}).get('recall', 0.0),
                'caution_f1': res.get('per_class', {}).get('CAUTION', {}).get('f1', 0.0)
            })

        df_comparison = pd.DataFrame(rows)

        # Selection Criterion:
        # 1. Primary: Highest F1-Macro
        # 2. Secondary (Safety): Lowest False Negative Rate on AVOID
        # 3. Tertiary: Lowest Latency
        df_sorted = df_comparison.sort_values(
            by=['f1_macro', 'avoid_recall', 'avg_latency_ms'],
            ascending=[False, False, True]
        )

        best_row = df_sorted.iloc[0].to_dict()
        best_model_name = best_row['model_name']

        # Find matching full result object
        best_result = next(r for r in evaluation_results if r['model_name'] == best_model_name)

        # Save artifacts
        csv_path = self.artifacts_dir / "model_comparison.csv"
        json_path = self.artifacts_dir / "model_comparison.json"
        metadata_path = self.artifacts_dir / "models" / "model_metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        df_comparison.to_csv(csv_path, index=False)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=2)

        metadata = {
            'best_model_name': best_model_name,
            'selection_criterion': "Highest F1-Macro with maximum AVOID class recall and low false negative rate",
            'metrics': best_row,
            'all_models_benchmarked': [r['model_name'] for r in evaluation_results]
        }

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        return best_result, df_comparison
