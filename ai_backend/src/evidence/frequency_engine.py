"""
Frequency Intelligence Engine for HealthSense AI.
Evaluates dietary consumption frequency (REGULAR, OCCASIONAL, LIMIT, AVOID)
using multi-factorial clinical evidence: nutritional density, free sugars, sodium,
saturated fat, processing level, food category, life stage, and personal health profiles.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class FrequencyIntelligenceEngine:
    """
    Determines evidence-backed consumption frequency guidance.
    Ensures non-misleading clinical explanations:
    - REGULAR: Generally suitable for regular inclusion in a balanced diet.
    - OCCASIONAL: Better suited for occasional enjoyment within moderate portions.
    - LIMIT: Recommended to limit intake due to high concentration of risk nutrients or processing.
    - AVOID: Not recommended due to hard safety constraints, allergens, or contraindications.
    """

    FREQUENCY_EXPLANATIONS: Dict[str, str] = {
        'REGULAR': "Generally suitable for regular inclusion in a balanced, varied diet based on favorable nutrient density and whole-ingredient composition.",
        'OCCASIONAL': "Better suited for occasional consumption with portion mindfulness due to concentrated free sugars, saturated fats, or caloric density.",
        'LIMIT': "Recommended to strictly limit frequency and portion sizes due to elevated sodium, refined sugars, or high degree of processing.",
        'AVOID': "Avoid consumption: conflicts with documented health restrictions, diagnosed allergies, or pediatric safety contraindications."
    }

    @classmethod
    def determine_frequency(cls,
                            food_grade: str,
                            product_nutrients: Dict[str, Any],
                            concern_flags: Dict[str, Any],
                            category_key: Optional[str] = None,
                            life_stage: Optional[str] = None,
                            has_hard_block: bool = False,
                            risk_level: str = "LOW",
                            data_confidence: str = "HIGH") -> Dict[str, Any]:
        """
        Calculates multi-dimensional frequency recommendation and associated clinical explanation.
        """
        # 1. Absolute safety override
        if has_hard_block or risk_level == "HIGH":
            freq = "AVOID"
            return {
                'frequency': freq,
                'explanation': cls.FREQUENCY_EXPLANATIONS[freq],
                'rationale': "Safety rule trigger or elevated personal risk requires avoidance."
            }

        sugars = product_nutrients.get('sugars')
        sodium = product_nutrients.get('sodium')
        sat_fat = product_nutrients.get('saturated_fat')

        # 2. Category-based baseline
        # Whole grains (oats), plain yogurt -> REGULAR
        if category_key in ['oats', 'plain_yogurt'] and food_grade in ['A', 'B']:
            base_freq = "REGULAR"
        # Confectionery, chocolates, soft drinks -> OCCASIONAL or LIMIT
        elif category_key in ['chocolate', 'milk_chocolate']:
            base_freq = "OCCASIONAL"
        elif category_key in ['general_confectionery', 'soft_drink']:
            base_freq = "LIMIT"
        elif category_key == 'energy_drink':
            base_freq = "LIMIT"
        else:
            # General nutrient density calculation
            if food_grade == 'A':
                base_freq = "REGULAR"
            elif food_grade == 'B':
                base_freq = "REGULAR" if (sugars is not None and sugars <= 10.0 and sodium is not None and sodium <= 300.0) else "OCCASIONAL"
            elif food_grade == 'C':
                base_freq = "OCCASIONAL"
            elif food_grade == 'D':
                base_freq = "LIMIT"
            else:
                base_freq = "LIMIT"

        # 3. Adjust for Life Stage
        if life_stage == 'YOUNG_CHILD':
            if sugars is not None and sugars > 10.0:
                base_freq = "LIMIT"
            if category_key in ['chocolate', 'milk_chocolate', 'general_confectionery']:
                base_freq = "LIMIT"

        elif life_stage == 'CHILD':
            if sugars is not None and sugars > 25.0:
                base_freq = "LIMIT"

        # 4. Adjust for Personal Health Risk Level
        if risk_level == "MODERATE":
            if base_freq == "REGULAR":
                base_freq = "OCCASIONAL"
            elif base_freq == "OCCASIONAL":
                base_freq = "LIMIT"

        # 5. Ultra-processing modifier
        if concern_flags.get('hydrogenated_oil_indicator') or concern_flags.get('artificial_sweetener_indicator'):
            if base_freq == "REGULAR":
                base_freq = "OCCASIONAL"

        return {
            'frequency': base_freq,
            'explanation': cls.FREQUENCY_EXPLANATIONS[base_freq],
            'rationale': f"Determined from Grade {food_grade}, category ({category_key or 'general'}), life stage ({life_stage or 'ADULT'}), and risk profile ({risk_level})."
        }
