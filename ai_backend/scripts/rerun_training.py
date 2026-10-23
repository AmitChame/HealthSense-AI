"""
Simplified Training Script for HealthSense AI.
Uses EXISTING exploratory sample from OpenFoodFacts, builds unified dataset,
and runs the improved training pipeline (Product-level split, Centralized thresholds).
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path

# Add ai_backend to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.data.dataset_builder import UnifiedDatasetBuilder
from src.preprocessing.cleaner import DatasetCleaner
from src.evaluation.trainer import ModelTrainingPipeline


def main():
    print("=" * 70)
    print("HealthSense AI — Rerunning Pipeline with Fixed Methodology")
    print("=" * 70)

    # 1. Load Existing Sample
    sample_file = project_root / "data" / "raw" / "openfoodfacts" / "off_exploratory_sample.json"
    if not sample_file.exists():
        print(f"Error: Sample file not found at {sample_file}")
        return

    with open(sample_file, 'r', encoding='utf-8') as f:
        raw_products = json.load(f)
    print(f"Loaded {len(raw_products)} raw product records from cache.")

    # 2. Build Unified Dataset
    print("\n[Step 1] Building unified internal dataset schema...")
    builder = UnifiedDatasetBuilder()
    df_unified = builder.build_dataframe(raw_products)
    print(f"Unified DataFrame shape: {df_unified.shape}")

    # 3. Clean Dataset
    print("\n[Step 2] Cleaning dataset and validating nutritional ranges...")
    cleaner = DatasetCleaner()
    df_cleaned, _ = cleaner.clean(df_unified)

    # 4. Train Models & Benchmark
    print("\n[Step 3] Executing Improved Model Training & Comparative Benchmark...")
    trainer = ModelTrainingPipeline(project_root=str(project_root))
    best_result, df_comparison = trainer.run_training_and_comparison(df_cleaned)

    print("\n" + "=" * 70)
    print("RE-EVALUATED MODEL COMPARISON RESULTS (Fixed Methodology):")
    print("=" * 70)
    print(df_comparison.to_string(index=False))
    print(f"\nEmpirical Best Model Selected: {best_result['model_name']} (F1-Macro: {best_result['f1_macro']:.4f})")
    print("=" * 70)


if __name__ == '__main__':
    main()
