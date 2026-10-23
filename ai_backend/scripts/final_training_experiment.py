"""
Final Model Training Experiment for HealthSense AI.
Performs product-level split, consistent preprocessing, model training,
benchmarking, and artifact persistence.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import logging
import joblib
from pathlib import Path
from datetime import datetime

# Add ai_backend to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.evaluation.trainer import ModelTrainingPipeline
from src.models.model_registry import ModelRegistry
from src.rules.config_manager import HealthSenseConfigManager
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=" * 80)
    print("HealthSense AI — Final Model Training Experiment")
    print("=" * 80)

    # 1. Data Validation
    dataset_path = project_root / "data" / "processed" / "unified_food_dataset.csv"
    if not dataset_path.exists():
        print(f"Error: Dataset not found at {dataset_path}")
        return

    df = pd.read_csv(dataset_path)
    unique_products = df['barcode'].nunique()
    print(f"[1] Data Validation:")
    print(f"    - Unique Products: {unique_products}")
    print(f"    - Feature Columns: {len(df.columns)}")

    # 2. Training Execution
    trainer = ModelTrainingPipeline(project_root=str(project_root))
    best_result, df_comparison = trainer.run_training_and_comparison(df)

    print("\n" + "=" * 80)
    print("FINAL EXPERIMENT RESULTS:")
    print("=" * 80)
    print(df_comparison.to_string(index=False))

    winner = best_result['model_name']
    print(f"\n[2] Model Selection Outcome:")
    print(f"    - Selected Winner: {winner}")
    print(f"    - F1-Macro: {best_result['f1_macro']:.4f}")
    # Note: Metrics dict structure based on evaluator output
    print(f"    - AVOID Recall: {best_result['per_class']['AVOID']['recall']:.4f}")

    # 3. Update active model in config
    config_path = project_root / "config" / "model_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    config['active'] = winner

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f)

    print(f"\n[3] Config Updated: Active model set to '{winner}' in config/model_config.yaml")

    # 4. Generate Metadata Artifact
    metadata = {
        'dataset_version': 'OFF_HEALTHSENSE_v1',
        'training_date': datetime.now().isoformat(),
        'unique_products': int(unique_products),
        'total_observations': int(unique_products * 8),
        'active_model': winner,
        'metrics': best_result,
        'feature_count': int(len(trainer.feature_names))
    }

    with open(project_root / "artifacts" / "models" / "model_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    df_comparison.to_csv(project_root / "artifacts" / "model_comparison.csv", index=False)

    print(f"[4] Artifacts saved to artifacts/models/")
    print("=" * 80)

if __name__ == '__main__':
    main()
