"""
Nutrient Normalization and Serving Size Intelligence Engine for HealthSense AI.
Handles standard unit conversions, serving size parsing, per-serving nutrient derivation,
and daily reference contribution calculations without inventing missing values.
"""

from typing import Dict, Any, Optional, Tuple
import re
import numpy as np
import logging

logger = logging.getLogger(__name__)


class NutrientNormalizer:
    """
    Standardizes nutritional parameters across different reporting bases:
    - PER_100G (grams or solid food)
    - PER_100ML (milliliters or liquid food)
    - PER_SERVING (discrete portion)

    Computes reference intake contributions while explicitly maintaining data provenance.
    """

    # Authoritative daily reference values for an average adult diet (2,000 kcal baseline)
    # References: WHO (2015, 2023), US FDA 21 CFR 101.9, ICMR-NIN 2024
    ADULT_DAILY_REFERENCES: Dict[str, Dict[str, Any]] = {
        'energy_kcal': {'value': 2000.0, 'unit': 'kcal', 'source': 'WHO/FDA Daily Reference Intake'},
        'sugars': {'value': 50.0, 'unit': 'g', 'source': 'WHO 10% energy / FDA Daily Value (50g)'},
        'sodium': {'value': 2000.0, 'unit': 'mg', 'source': 'WHO Recommended Limit (<2,000 mg)'},
        'saturated_fat': {'value': 20.0, 'unit': 'g', 'source': 'WHO 10% energy / FDA Daily Value (20g)'},
        'fat': {'value': 78.0, 'unit': 'g', 'source': 'FDA Daily Value (78g / 35% of 2,000 kcal)'},
        'carbohydrates': {'value': 275.0, 'unit': 'g', 'source': 'FDA Daily Value (275g)'},
        'protein': {'value': 50.0, 'unit': 'g', 'source': 'FDA Daily Value (50g / ICMR 54g)'},
        'fiber': {'value': 28.0, 'unit': 'g', 'source': 'FDA Daily Value (28g / WHO 25g)'},
    }

    @staticmethod
    def parse_serving_size(serving_text: Optional[str]) -> Tuple[Optional[float], Optional[str]]:
        """
        Parses raw serving size strings (e.g. '30 g', '1 bar (45g)', '250 ml', '1 pack (50 g)')
        into a numeric quantity and standardized unit ('g' or 'ml').
        Returns (amount, unit) or (None, None) if unavailable or invalid.
        """
        if not serving_text or not isinstance(serving_text, str):
            return None, None

        cleaned = serving_text.strip()
        if not cleaned:
            return None, None

        # Regex to match patterns like "45 g", "45g", "250 ml", "30 grams", "(35 g)"
        # Try finding the weight inside parentheses first, e.g. "1 pouch (45 g)"
        paren_match = re.search(r'\(([\d\.]+)\s*(g|grams|ml|milliliters)\b\)', cleaned, re.IGNORECASE)
        if paren_match:
            try:
                amt = float(paren_match.group(1))
                u = paren_match.group(2).lower()
                unit = 'ml' if 'ml' in u or 'milli' in u else 'g'
                return amt, unit
            except (ValueError, TypeError):
                pass

        # Standard pattern: number followed by unit
        match = re.search(r'([\d\.]+)\s*(g|grams|ml|milliliters)\b', cleaned, re.IGNORECASE)
        if match:
            try:
                amt = float(match.group(1))
                u = match.group(2).lower()
                unit = 'ml' if 'ml' in u or 'milli' in u else 'g'
                return amt, unit
            except (ValueError, TypeError):
                pass

        return None, None

    @classmethod
    def normalize_nutrients(cls, raw_nutriments: Dict[str, Any], serving_size_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Normalizes a raw product nutriments map into structured per-100g and per-serving profiles.
        Never fabricates missing values (distinguishes measured 0.0 from None/NaN).
        """
        if not raw_nutriments:
            raw_nutriments = {}

        serving_amount, serving_unit = cls.parse_serving_size(serving_size_text)

        # Standard nutrient keys
        core_keys = {
            'energy_kcal': ['energy_kcal_100g', 'calories', 'energy-kcal_100g'],
            'sugars': ['sugars_100g', 'sugars'],
            'sodium': ['sodium_100g', 'sodium'],
            'saturated_fat': ['saturated_fat_100g', 'saturatedFat', 'saturated-fat_100g'],
            'fat': ['fat_100g', 'fats', 'fat'],
            'carbohydrates': ['carbohydrates_100g', 'carbohydrates'],
            'protein': ['protein_100g', 'proteins', 'protein'],
            'fiber': ['fiber_100g', 'fiber']
        }

        per_100g: Dict[str, Optional[float]] = {}
        per_serving: Dict[str, Optional[float]] = {}
        data_status: Dict[str, str] = {}
        reference_contributions: Dict[str, Optional[float]] = {}

        for param, aliases in core_keys.items():
            val = None
            for alias in aliases:
                raw_val = raw_nutriments.get(alias)
                if raw_val is not None and not (isinstance(raw_val, float) and np.isnan(raw_val)):
                    try:
                        val = float(raw_val)
                        break
                    except (ValueError, TypeError):
                        continue

            if val is not None:
                per_100g[param] = val
                data_status[param] = "KNOWN"

                # Calculate per-serving if valid serving amount exists
                if serving_amount is not None and serving_amount > 0:
                    serving_val = round((val * serving_amount) / 100.0, 2)
                    per_serving[param] = serving_val

                    # Calculate contribution to adult daily reference
                    ref_info = cls.ADULT_DAILY_REFERENCES.get(param)
                    if ref_info and ref_info['value'] > 0:
                        pct = round((serving_val / ref_info['value']) * 100.0, 1)
                        reference_contributions[param] = pct
                    else:
                        reference_contributions[param] = None
                else:
                    per_serving[param] = None
                    reference_contributions[param] = None
            else:
                per_100g[param] = None
                per_serving[param] = None
                data_status[param] = "UNKNOWN"
                reference_contributions[param] = None

        return {
            'per_100g': per_100g,
            'per_serving': per_serving,
            'serving_size': {
                'raw': serving_size_text,
                'amount': serving_amount,
                'unit': serving_unit,
                'is_available': serving_amount is not None
            },
            'reference_contributions': reference_contributions,
            'data_status': data_status,
            'reference_framework': 'WHO/FDA/ICMR 2,000 kcal Adult Standard'
        }
