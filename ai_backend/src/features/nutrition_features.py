"""
Nutrition Feature Extraction & Transformation Pipeline.
Extracts normalized numerical features, nutrient density ratios, and preserves missingness indicators.
"""

from typing import Dict, Any
import numpy as np


class NutritionFeaturePipeline:
    """
    Computes nutritional density features, ratios, and risk flags per 100g.
    """

    CORE_NUTRIENTS = [
        'energy_kcal_100g',
        'sugars_100g',
        'sodium_100g',
        'fat_100g',
        'saturated_fat_100g',
        'carbohydrates_100g',
        'protein_100g',
        'fiber_100g'
    ]

    def extract_features(self, nutriments: Dict[str, Any]) -> Dict[str, float]:
        """
        Extracts standardized nutritional features and calculated ratios from a product nutriments map.
        Missing values are represented as np.nan (preserving missingness).
        """
        feats: Dict[str, float] = {}

        if not nutriments:
            nutriments = {}

        # 1. Extract core nutrients
        energy = nutriments.get('energy_kcal_100g', nutriments.get('calories'))
        sugars = nutriments.get('sugars_100g', nutriments.get('sugars'))
        sodium = nutriments.get('sodium_100g', nutriments.get('sodium'))
        fat = nutriments.get('fat_100g', nutriments.get('fats'))
        sat_fat = nutriments.get('saturated_fat_100g', nutriments.get('saturatedFat'))
        carbs = nutriments.get('carbohydrates_100g', nutriments.get('carbohydrates'))
        protein = nutriments.get('protein_100g', nutriments.get('proteins'))
        fiber = nutriments.get('fiber_100g', nutriments.get('fiber'))

        # Standardize types and track missingness
        feats['energy_kcal_100g'] = float(energy) if energy is not None else np.nan
        feats['sugars_100g'] = float(sugars) if sugars is not None else np.nan
        feats['sodium_100g'] = float(sodium) if sodium is not None else np.nan
        feats['fat_100g'] = float(fat) if fat is not None else np.nan
        feats['saturated_fat_100g'] = float(sat_fat) if sat_fat is not None else np.nan
        feats['carbohydrates_100g'] = float(carbs) if carbs is not None else np.nan
        feats['protein_100g'] = float(protein) if protein is not None else np.nan
        feats['fiber_100g'] = float(fiber) if fiber is not None else np.nan

        # Missingness indicator flags (crucial for model transparency)
        feats['is_sugar_missing'] = 1.0 if np.isnan(feats['sugars_100g']) else 0.0
        feats['is_sodium_missing'] = 1.0 if np.isnan(feats['sodium_100g']) else 0.0
        feats['is_sat_fat_missing'] = 1.0 if np.isnan(feats['saturated_fat_100g']) else 0.0

        # Safe values for ratio calculation (using 0.0 fallback only inside ratio computation)
        safe_energy = feats['energy_kcal_100g'] if not np.isnan(feats['energy_kcal_100g']) else 0.0
        safe_sugars = feats['sugars_100g'] if not np.isnan(feats['sugars_100g']) else 0.0
        safe_sodium = feats['sodium_100g'] if not np.isnan(feats['sodium_100g']) else 0.0
        safe_fat = feats['fat_100g'] if not np.isnan(feats['fat_100g']) else 0.0
        safe_sat_fat = feats['saturated_fat_100g'] if not np.isnan(feats['saturated_fat_100g']) else 0.0
        safe_carbs = feats['carbohydrates_100g'] if not np.isnan(feats['carbohydrates_100g']) else 0.0
        safe_protein = feats['protein_100g'] if not np.isnan(feats['protein_100g']) else 0.0
        safe_fiber = feats['fiber_100g'] if not np.isnan(feats['fiber_100g']) else 0.0

        # 2. Nutrient Ratios & Densities
        # Sugar-to-Carbohydrate Ratio (indicates refined simplicity of carbs)
        feats['sugar_to_carb_ratio'] = safe_sugars / (safe_carbs + 1e-4) if safe_carbs > 0 else 0.0

        # Saturated Fat to Total Fat Ratio
        feats['sat_fat_to_total_fat_ratio'] = safe_sat_fat / (safe_fat + 1e-4) if safe_fat > 0 else 0.0

        # Sodium Density (mg sodium per kcal)
        feats['sodium_per_kcal'] = safe_sodium / (safe_energy + 1.0) if safe_energy > 0 else 0.0

        # Protein-to-Carbohydrate Ratio
        feats['protein_to_carb_ratio'] = safe_protein / (safe_carbs + 1e-4) if safe_carbs > 0 else 0.0

        # Fiber-to-Carbohydrate Ratio (Quality of carbs)
        feats['fiber_to_carb_ratio'] = safe_fiber / (safe_carbs + 1e-4) if safe_carbs > 0 else 0.0

        return feats
