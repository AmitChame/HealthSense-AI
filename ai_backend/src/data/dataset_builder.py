"""
Unified Dataset Builder for HealthSense AI.
Transforms raw Open Food Facts (and USDA) JSON/CSV records into the unified internal schema.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from ..ingredient_engine.normalizer import IngredientNormalizer
from ..ingredient_engine.allergen_detector import AllergenDetector
from ..ingredient_engine.concern_detector import ConcernDetector
from ..features.food_grader import HealthSenseFoodGrader


class UnifiedDatasetBuilder:
    """
    Constructs unified pandas DataFrame from raw product objects.
    """

    def __init__(self):
        self.normalizer = IngredientNormalizer()
        self.allergen_detector = AllergenDetector()
        self.concern_detector = ConcernDetector()
        self.grader = HealthSenseFoodGrader()

    def process_product_record(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses a single raw OpenFoodFacts JSON record into unified schema.
        Preserves missing values as None / np.nan.
        All internal nutritional weights are normalized to MILLIGRAMS (for sodium) or GRAMS (others) per 100g.
        """
        barcode = str(raw.get('code', raw.get('barcode', ''))).strip()
        product_name = raw.get('product_name', raw.get('product_name_en', 'Unknown Product'))
        brand = raw.get('brands', raw.get('brand', ''))
        categories = raw.get('categories', '')
        serving_size = raw.get('serving_size', '')

        # Ingredients
        ingredients_raw = raw.get('ingredients_text', raw.get('ingredients_text_en', ''))
        normalized_ing = self.normalizer.normalize(ingredients_raw)
        allergen_tags = raw.get('allergens_tags', [])

        # Allergen detection
        allergen_flags = self.allergen_detector.detect_allergens(ingredients_raw, allergen_tags)

        # Concern detection
        additives_tags = raw.get('additives_tags', [])
        concern_flags = self.concern_detector.detect_concerns(ingredients_raw, additives_tags)

        # Nutriments
        nutriments = raw.get('nutriments', {})

        def get_nutrient_val(keys: List[str]) -> Optional[float]:
            for k in keys:
                val = nutriments.get(k)
                if val is not None:
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        pass
            return np.nan

        # 1. energy-kcal priority (explicit kcal fields only)
        energy_kcal = get_nutrient_val(['energy-kcal_100g', 'energy_kcal_100g', 'energy-kcal'])

        # 2. energy-kj fallback (explicit conversion)
        if np.isnan(energy_kcal):
            energy_kj = get_nutrient_val(['energy-kj_100g', 'energy_kj_100g', 'energy-kj'])
            if not np.isnan(energy_kj):
                energy_kcal = energy_kj / 4.184

        sugars = get_nutrient_val(['sugars_100g', 'sugars'])

        # --- Sodium & Salt Normalization ---
        # OpenFoodFacts returns sodium and salt in GRAMS per 100g.
        # We normalize internal sodium_100g to MILLIGRAMS.
        sodium_raw_g = get_nutrient_val(['sodium_100g', 'sodium'])
        salt_raw_g = get_nutrient_val(['salt_100g', 'salt'])

        sodium = np.nan
        if not np.isnan(sodium_raw_g):
            # Explicitly assume grams and convert to mg
            sodium = sodium_raw_g * 1000.0
        elif not np.isnan(salt_raw_g):
            # Fallback: Sodium (mg) = Salt (g) / 2.5 * 1000 = Salt (g) * 400
            sodium = salt_raw_g * 400.0

        fat = get_nutrient_val(['fat_100g', 'fat'])
        sat_fat = get_nutrient_val(['saturated-fat_100g', 'saturated_fat_100g', 'saturated-fat'])
        carbs = get_nutrient_val(['carbohydrates_100g', 'carbohydrates'])
        protein = get_nutrient_val(['proteins_100g', 'protein_100g', 'proteins'])
        fiber = get_nutrient_val(['fiber_100g', 'fiber'])

        nova_group = raw.get('nova_group', raw.get('nova_groups'))
        nutriscore = raw.get('nutriscore_grade', raw.get('nutrition_grades'))

        # Standalone Food Grade calculation
        nutr_map = {
            'energy_kcal_100g': energy_kcal,
            'sugars_100g': sugars,
            'sodium_100g': sodium, # now in mg
            'fat_100g': fat,
            'saturated_fat_100g': sat_fat,
            'fiber_100g': fiber,
            'protein_100g': protein
        }
        grade, score, _ = self.grader.grade_product(nutr_map, concern_flags, nova_group, nutriscore)

        record = {
            'barcode': barcode,
            'product_name': product_name,
            'brand': brand,
            'categories': categories,
            'serving_size': serving_size,
            'ingredients_text': ingredients_raw,
            'normalized_ingredients': normalized_ing,
            'energy_kcal_100g': energy_kcal,
            'sugars_100g': sugars,
            'sodium_100g': sodium,
            'fat_100g': fat,
            'saturated_fat_100g': sat_fat,
            'carbohydrates_100g': carbs,
            'protein_100g': protein,
            'fiber_100g': fiber,
            'nova_group': nova_group,
            'nutriscore': nutriscore,
            'healthsense_grade': grade,
            'healthsense_score': score,
            **allergen_flags,
            'added_sugar_indicator': concern_flags['added_sugar_indicator'],
            'artificial_sweetener_indicator': concern_flags['artificial_sweetener_indicator'],
            'preservative_indicator': concern_flags['preservative_indicator'],
            'artificial_color_indicator': concern_flags['artificial_color_indicator'],
            'hydrogenated_oil_indicator': concern_flags['hydrogenated_oil_indicator'],
            'high_concern_ingredient_count': concern_flags['high_concern_ingredient_count'],
            'contains_animal_derived': concern_flags['contains_animal_derived'],
            'contains_meat_or_gelatin': concern_flags['contains_meat_or_gelatin'],
        }
        return record

    def build_dataframe(self, raw_products: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Transforms a list of raw product dicts into a unified pandas DataFrame.
        """
        records = [self.process_product_record(p) for p in raw_products]
        df = pd.DataFrame(records)
        return df
