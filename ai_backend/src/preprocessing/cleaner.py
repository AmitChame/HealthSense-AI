"""
Dataset Cleaning & Validation Module.
Preserves missingness, validates numerical nutritional ranges, and removes invalid/duplicate barcodes.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any


class DatasetCleaner:
    """
    Validates and cleans unified food product dataset.
    """

    def clean(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans the DataFrame and returns the cleaned DataFrame along with cleaning audit stats.
        """
        initial_count = len(df)
        stats: Dict[str, Any] = {
            'initial_rows': initial_count,
            'duplicate_barcodes_removed': 0,
            'invalid_barcodes_removed': 0,
            'out_of_range_nutrients_flagged': 0,
            'final_rows': 0
        }

        if df.empty:
            stats['final_rows'] = 0
            return df, stats

        cleaned_df = df.copy()

        # 1. Remove duplicate barcodes
        if 'barcode' in cleaned_df.columns:
            dups = cleaned_df.duplicated(subset=['barcode'], keep='first').sum()
            stats['duplicate_barcodes_removed'] = int(dups)
            cleaned_df = cleaned_df.drop_duplicates(subset=['barcode'], keep='first')

        # 2. Filter out products with invalid barcodes (empty or placeholder)
        if 'barcode' in cleaned_df.columns:
            valid_barcode_mask = cleaned_df['barcode'].astype(str).str.len() >= 3
            invalid_bc = (~valid_barcode_mask).sum()
            stats['invalid_barcodes_removed'] = int(invalid_bc)
            cleaned_df = cleaned_df[valid_barcode_mask]

        # 3. Validate nutrient bounds (replace impossible outliers with np.nan to preserve missingness)
        nutrient_bounds = {
            'sugars_100g': (0.0, 100.0),
            'fat_100g': (0.0, 100.0),
            'saturated_fat_100g': (0.0, 100.0),
            'carbohydrates_100g': (0.0, 100.0),
            'protein_100g': (0.0, 100.0),
            'fiber_100g': (0.0, 100.0),
            'energy_kcal_100g': (0.0, 1000.0),
            'sodium_100g': (0.0, 40000.0), # mg
        }

        out_of_range_count = 0
        for col, (lower, upper) in nutrient_bounds.items():
            if col in cleaned_df.columns:
                invalid_mask = (cleaned_df[col] < lower) | (cleaned_df[col] > upper)
                out_of_range_count += int(invalid_mask.sum())
                cleaned_df.loc[invalid_mask, col] = np.nan

        stats['out_of_range_nutrients_flagged'] = out_of_range_count
        stats['final_rows'] = len(cleaned_df)

        return cleaned_df, stats
