"""
Dataset Pipeline & Model Training Script for HealthSense AI.
Downloads exploratory sample from OpenFoodFacts, builds unified dataset,
cleans data, generates data quality report, trains all 4 models, and selects the empirical winner.
"""

import os
import sys
from pathlib import Path

# Add ai_backend to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.data.openfoodfacts_downloader import OpenFoodFactsDownloader
from src.data.dataset_builder import UnifiedDatasetBuilder
from src.preprocessing.cleaner import DatasetCleaner
from src.preprocessing.quality_reporter import DataQualityReporter
from src.evaluation.trainer import ModelTrainingPipeline
import json


def main():
    print("=" * 70)
    print("HealthSense AI — Dataset Ingestion & Model Training Pipeline")
    print("=" * 70)

    # 1. Check disk space
    downloader = OpenFoodFactsDownloader()
    disk_info = downloader.check_disk_space(required_mb=50.0)
    print(f"[Disk Audit] Free space: {disk_info['free_gb']} GB ({disk_info['free_mb']} MB). Required: {disk_info['required_mb']} MB")

    # 2. Fetch Exploratory Sample
    print("\n[Step 1] Fetching exploratory Open Food Facts sample...")
    sample_file = downloader.fetch_exploratory_sample(page_size=50, num_pages=10)

    with open(sample_file, 'r', encoding='utf-8') as f:
        raw_products = json.load(f)
    print(f"Loaded {len(raw_products)} raw product records.")

    # 3. Build Unified Dataset
    print("\n[Step 2] Building unified internal dataset schema...")
    builder = UnifiedDatasetBuilder()
    df_unified = builder.build_dataframe(raw_products)
    print(f"Unified DataFrame shape: {df_unified.shape}")

    # 4. Clean Dataset
    print("\n[Step 3] Cleaning dataset and validating nutritional ranges...")
    cleaner = DatasetCleaner()
    df_cleaned, clean_stats = cleaner.clean(df_unified)
    print(f"Cleaning Stats: {clean_stats}")

    # Save processed dataset
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    df_cleaned.to_csv(processed_dir / "unified_food_dataset.csv", index=False)
    print(f"Saved cleaned dataset to: {processed_dir / 'unified_food_dataset.csv'}")

    # 5. Data Quality Report
    print("\n[Step 4] Generating Data Quality Audit Report...")
    reporter = DataQualityReporter()
    report = reporter.generate_report(df_cleaned)
    report_md = reporter.format_markdown_report(report)

    report_path = project_root / "data" / "data_quality_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
    print(f"Data Quality Report written to: {report_path}")

    # 6. Train Models & Benchmark
    print("\n[Step 5] Executing Model Training & Comparative Benchmark...")
    trainer = ModelTrainingPipeline(project_root=str(project_root))
    best_result, df_comparison = trainer.run_training_and_comparison(df_cleaned)

    print("\n" + "=" * 70)
    print("FINAL MODEL COMPARISON RESULTS:")
    print("=" * 70)
    print(df_comparison.to_string(index=False))
    print(f"\nEmpirical Best Model Selected: {best_result['model_name']} (F1-Macro: {best_result['f1_macro']:.4f})")
    print("=" * 70)


if __name__ == '__main__':
    main()
