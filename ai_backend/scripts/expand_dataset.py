"""
Large-Scale Dataset Expansion Script for HealthSense AI.
Fetches high-quality products from OpenFoodFacts, applies strict nutritional filters,
processes data through the validated pipeline, and generates a quality audit report.
"""

import os
import sys
import json
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Add ai_backend to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.data.openfoodfacts_downloader import OpenFoodFactsDownloader
from src.data.dataset_builder import UnifiedDatasetBuilder
from src.preprocessing.cleaner import DatasetCleaner
from src.evaluation.trainer import ModelTrainingPipeline


def main():
    print("=" * 80)
    print(f"HealthSense AI — Dataset Expansion Phase (Target: 5,000-10,000 Products)")
    print("=" * 80)

    # 1. Disk Audit
    downloader = OpenFoodFactsDownloader()
    disk = downloader.check_disk_space(required_mb=500.0)
    print(f"[1/6] Disk Audit: {disk['free_gb']} GB free. Required: 0.5 GB. Sufficient: {disk['is_sufficient']}")
    if not disk['is_sufficient']:
        print("Error: Insufficient disk space.")
        return

    # 2. Fetch Large Sample
    categories = [
        "cereals", "beverages", "snacks", "dairy", "plant-based-foods",
        "sauces", "breads", "biscuits", "chocolates", "prepared-meals",
        "frozen-foods", "cheeses", "meats", "desserts", "spreads",
        "canned-foods", "seafood", "confectionery", "pastas", "pizzas",
        "yogurts", "fruit-juices", "chips-and-fries", "cakes", "jams",
        "legumes", "nuts", "soups", "oils", "ice-creams"
    ]

    raw_file = project_root / "data" / "raw" / "openfoodfacts" / "off_expanded_raw.json"
    all_raw_products = []

    print(f"\n[2/6] Fetching raw products from OpenFoodFacts API...")

    # Selection Strategy: 400 products per category across 30 categories = ~12,000 raw
    page_size = 100
    pages_per_cat = 4

    headers = {'User-Agent': 'HealthSenseAI-Expansion/1.0 (contact@healthsenseai.edu)'}

    start_time = time.time()
    for cat in categories:
        cat_count = 0
        for page in range(1, pages_per_cat + 1):
            try:
                params = {
                    'action': 'process',
                    'tagtype_0': 'categories',
                    'tag_contains_0': 'contains',
                    'tag_0': cat,
                    'page_size': page_size,
                    'page': page,
                    'json': 'true'
                }
                resp = requests.get(downloader.OFF_SEARCH_API, params=params, headers=headers, timeout=20)
                if resp.status_code == 200:
                    products = resp.json().get('products', [])
                    all_raw_products.extend(products)
                    cat_count += len(products)
                    if len(products) < page_size:
                        break # No more products in this category
                elif resp.status_code == 503:
                    print(f"  Warning: 503 (Busy) for {cat} page {page}. Skipping page.")
                else:
                    print(f"  Warning: HTTP {resp.status_code} for {cat} page {page}")
            except Exception as e:
                print(f"  Error fetching {cat} page {page}: {e}")

            # Small delay to be polite to OFF API
            time.sleep(0.5)

        print(f"  Category '{cat}': {cat_count} records")

    # Save raw for audit if needed (not tracked by git)
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(all_raw_products, f, indent=2)

    total_raw = len(all_raw_products)
    print(f"Total raw records fetched: {total_raw}")

    # 3. Build & Filter Unified Dataset
    print(f"\n[3/6] Building unified dataset and applying quality filters...")
    builder = UnifiedDatasetBuilder()

    valid_records = []
    invalid_counts = {
        'missing_barcode': 0,
        'missing_ingredients': 0,
        'missing_energy': 0,
        'missing_macros': 0, # sugar, fat, protein, carbs
        'missing_sodium_salt': 0
    }

    for raw in all_raw_products:
        # Initial fast filters
        if not raw.get('code') and not raw.get('barcode'):
            invalid_counts['missing_barcode'] += 1
            continue

        ing = raw.get('ingredients_text', raw.get('ingredients_text_en', ''))
        if not ing or len(ing.split()) < 3:
            invalid_counts['missing_ingredients'] += 1
            continue

        nutr = raw.get('nutriments', {})

        # Energy check
        has_energy = any(k in nutr for k in ['energy-kcal_100g', 'energy_kcal_100g', 'energy-kcal', 'energy-kj_100g', 'energy_kj_100g', 'energy-kj'])
        if not has_energy:
            invalid_counts['missing_energy'] += 1
            continue

        # Macros check
        has_macros = all(any(k in nutr for k in keys) for keys in [
            ['sugars_100g', 'sugars'],
            ['fat_100g', 'fat'],
            ['proteins_100g', 'proteins'],
            ['carbohydrates_100g', 'carbohydrates']
        ])
        if not has_macros:
            invalid_counts['missing_macros'] += 1
            continue

        # Sodium/Salt check
        has_salt_sodium = any(k in nutr for k in ['sodium_100g', 'sodium', 'salt_100g', 'salt'])
        if not has_salt_sodium:
            invalid_counts['missing_sodium_salt'] += 1
            continue

        # Passes hard requirements -> process through pipeline
        record = builder.process_product_record(raw)
        valid_records.append(record)

    print(f"Records passing quality filters: {len(valid_records)}")
    print(f"Filter rejections: {invalid_counts}")

    # 4. Cleaning & Deduplication
    print(f"\n[4/6] Cleaning and deduplicating...")
    df_unified = pd.DataFrame(valid_records)
    cleaner = DatasetCleaner()
    df_cleaned, clean_stats = cleaner.clean(df_unified)

    final_count = len(df_cleaned)
    print(f"Final unique products: {final_count}")
    print(f"Cleaning Stats: {clean_stats}")

    # Save processed dataset
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = processed_dir / "unified_food_dataset.csv"
    df_cleaned.to_csv(dataset_path, index=False)

    # 5. Label Distribution Analysis
    print(f"\n[5/6] Inspecting class/label distribution across health profiles...")
    trainer = ModelTrainingPipeline(project_root=str(project_root))
    # use is_training=True to allow fitting TF-IDF and Scaler on the NEW expanded dataset
    _, y = trainer.prepare_data(df_cleaned, is_training=True)

    # y is a flat array of all observations (8 per product)
    total_obs = len(y)
    unique_labels, counts = np.unique(y, return_counts=True)
    label_map = {0: 'RECOMMENDED', 1: 'CAUTION', 2: 'AVOID'}

    dist = {}
    for label, count in zip(unique_labels, counts):
        name = label_map[label]
        pct = (count / total_obs) * 100
        dist[name] = {'count': int(count), 'percentage': round(pct, 2)}
        print(f"  {name}: {count} ({pct:.2f}%)")

    # Per profile distribution
    profile_dist = {}
    obs_per_prod = len(trainer.PROFILE_SCENARIOS)
    for i, scenario in enumerate(trainer.PROFILE_SCENARIOS):
        # Slice y for this profile
        profile_y = y[i::obs_per_prod]
        p_labels, p_counts = np.unique(profile_y, return_counts=True)
        p_res = {label_map[l]: int(c) for l, c in zip(p_labels, p_counts)}
        profile_dist[scenario['name']] = p_res
        print(f"    Profile '{scenario['name']}': {p_res}")

    # 6. Generate Data Quality Report
    print(f"\n[6/6] Generating Data Quality Report and Dataset Summary...")

    missingness = df_cleaned.isnull().mean() * 100

    summary = {
        'dataset_version': 'OFF_HEALTHSENSE_v1',
        'creation_date': datetime.now().isoformat(),
        'source': 'OpenFoodFacts API (Search)',
        'total_raw_processed': total_raw,
        'unique_products': final_count,
        'features_count': len(df_cleaned.columns),
        'label_distribution': dist,
        'profile_distribution': profile_dist,
        'missingness': missingness.to_dict(),
        'cleaning_stats': clean_stats
    }

    with open(processed_dir / "dataset_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    report_md = f"""# HealthSense AI Data Quality Report

**Dataset Version:** OFF_HEALTHSENSE_v1
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Ingestion Overview
- **Raw Records Processed:** {total_raw}
- **Unique Products (Final):** {final_count}
- **Duplicates Removed:** {clean_stats['duplicate_barcodes_removed']}
- **Invalid Barcodes Removed:** {clean_stats['invalid_barcodes_removed']}

## Quality Filter Rejections
- **Missing Barcode:** {invalid_counts['missing_barcode']}
- **Insufficient Ingredients:** {invalid_counts['missing_ingredients']}
- **Missing Energy Data:** {invalid_counts['missing_energy']}
- **Missing Core Macros:** {invalid_counts['missing_macros']}
- **Missing Sodium/Salt:** {invalid_counts['missing_sodium_salt']}

## Feature Coverage & Missingness
| Feature | Coverage % | Missingness % |
| :--- | :---: | :---: |
| Barcode | 100.0% | 0.0% |
| Product Name | {100.0 - missingness.get('product_name', 0):.1f}% | {missingness.get('product_name', 0):.1f}% |
| Ingredients | 100.0% | 0.0% |
| Energy (kcal/100g) | 100.0% | 0.0% |
| Sugars | 100.0% | 0.0% |
| Fat | 100.0% | 0.0% |
| Saturated Fat | {100.0 - missingness.get('saturated_fat_100g', 0):.1f}% | {missingness.get('saturated_fat_100g', 0):.1f}% |
| Protein | 100.0% | 0.0% |
| Carbohydrates | 100.0% | 0.0% |
| Sodium (mg/100g) | 100.0% | 0.0% |
| Fiber | {100.0 - missingness.get('fiber_100g', 0):.1f}% | {missingness.get('fiber_100g', 0):.1f}% |
| NOVA Group | {100.0 - missingness.get('nova_group', 0):.1f}% | {missingness.get('nova_group', 0):.1f}% |
| Nutri-Score | {100.0 - missingness.get('nutriscore', 0):.1f}% | {missingness.get('nutriscore', 0):.1f}% |

## Label Distribution (Unified)
- **RECOMMENDED:** {dist.get('RECOMMENDED', {}).get('count')} ({dist.get('RECOMMENDED', {}).get('percentage')}%)
- **CAUTION:** {dist.get('CAUTION', {}).get('count')} ({dist.get('CAUTION', {}).get('percentage')}%)
- **AVOID:** {dist.get('AVOID', {}).get('count')} ({dist.get('AVOID', {}).get('percentage')}%)

## Distribution by Health Profile
"""
    for profile, p_dist in profile_dist.items():
        report_md += f"- **{profile}:** {p_dist}\n"

    with open(project_root / "data" / "data_quality_report.md", 'w', encoding='utf-8') as f:
        f.write(report_md)

    print(f"\n[DONE] Dataset expanded and saved to {dataset_path}")
    print(f"Data Quality Report written to data/data_quality_report.md")
    print(f"Dataset Summary written to data/processed/dataset_summary.json")
    print(f"Total processing time: {time.time() - start_time:.1f} seconds")


if __name__ == '__main__':
    main()
