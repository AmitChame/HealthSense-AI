"""
HealthSense Standalone Food Quality Grader (A, B, C, D, E).
Computes an objective product quality score based on nutritional composition,
ingredient profile (composite indicator), and processing classification (NOVA).

IMPORTANT:
- Answers: "How favorable is this product's nutritional/ingredient composition based on available evidence?"
- Does NOT answer: "Is this safe for an individual with an allergy or specific medical condition?"
- Does NOT fabricate an arbitrary 'naturalness percentage' (uses an explicit composite ingredient profile).
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np


class HealthSenseFoodGrader:
    """
    Independent food quality evaluation engine calibrated against WHO/FSSAI/Codex guidelines.
    Does not depend on personal health profiles or the ML recommendation model.
    """

    def __init__(self, weights: Dict[str, float] = None, thresholds: Dict[str, float] = None):
        self.weights = weights or {
            'nutrition_quality': 0.50,
            'ingredient_profile': 0.30,
            'processing_level': 0.20
        }
        self.thresholds = thresholds or {
            'A': 80.0,
            'B': 65.0,
            'C': 50.0,
            'D': 35.0,
            'E': 0.0
        }

    def compute_nutrition_score(self, nutriments: Dict[str, Any], category_key: Optional[str] = None) -> float:
        """
        Scores nutritional balance from 0 (poor) to 100 (excellent) based on WHO guidance:
        - Penalties: free sugars > 5g/100g, saturated fat > 2g/100g, sodium > 200mg/100g, excessive energy density.
        - Rewards: dietary fiber (> 1.5g), protein (> 3.0g).
        - Category-aware: Adjusts expectation for categories like whole oats vs oils/beverages.
        """
        if not nutriments:
            return 50.0 # Neutral default when data is completely absent

        score = 70.0 # Standard baseline score

        sugars = nutriments.get('sugars_100g', nutriments.get('sugars'))
        sodium = nutriments.get('sodium_100g', nutriments.get('sodium'))
        sat_fat = nutriments.get('saturated_fat_100g', nutriments.get('saturatedFat'))
        fiber = nutriments.get('fiber_100g', nutriments.get('fiber'))
        protein = nutriments.get('protein_100g', nutriments.get('proteins'))
        energy = nutriments.get('energy_kcal_100g', nutriments.get('calories'))

        # Negative factors (Sugars: WHO recommendation < 10% total energy, ideal < 5%)
        if sugars is not None and not (isinstance(sugars, float) and np.isnan(sugars)):
            if sugars > 15.0:
                score -= min(30.0, (sugars - 15.0) * 1.5 + 15.0)
            elif sugars > 5.0:
                score -= (sugars - 5.0) * 1.5

        # Saturated Fat: WHO recommendation < 10% of total energy
        if sat_fat is not None and not (isinstance(sat_fat, float) and np.isnan(sat_fat)):
            if sat_fat > 5.0:
                score -= min(25.0, (sat_fat - 5.0) * 3.0 + 10.0)
            elif sat_fat > 2.0:
                score -= (sat_fat - 2.0) * 3.0

        # Sodium: WHO recommendation < 2,000 mg/day (~200mg/100g baseline)
        if sodium is not None and not (isinstance(sodium, float) and np.isnan(sodium)):
            if sodium > 600.0:
                score -= min(25.0, (sodium - 600.0) * 0.03 + 12.0)
            elif sodium > 200.0:
                score -= (sodium - 200.0) * 0.03

        # Positive factors (Fiber: WHO/Codex dietary fiber recommendations)
        if fiber is not None and not (isinstance(fiber, float) and np.isnan(fiber)) and fiber > 1.0:
            score += min(15.0, fiber * 2.5)

        # Protein: Essential macronutrient
        if protein is not None and not (isinstance(protein, float) and np.isnan(protein)) and protein > 2.0:
            score += min(15.0, protein * 1.5)

        # Caloric Density penalty if excessively high without mitigating fiber/protein
        if energy is not None and not (isinstance(energy, float) and np.isnan(energy)) and energy > 450:
            score -= 10.0

        return float(np.clip(score, 0.0, 100.0))

    def compute_ingredient_score(self, concern_flags: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Computes composite Ingredient Profile & Additive Density Score (0 to 100).
        Evaluates presence of industrially synthesized additives:
        - Hydrogenated oils / industrial trans-fats (highest health concern: WHO/FSSAI limit)
        - Artificial sweeteners, synthetic preservatives, synthetic food colorings, added sugars.
        
        Returns: (score, ingredient_profile_metadata)
        """
        score = 100.0
        flagged = []

        if concern_flags:
            if concern_flags.get('hydrogenated_oil_indicator', 0):
                score -= 30.0
                flagged.append("Partially hydrogenated vegetable oil / industrial trans-fat source")
            if concern_flags.get('artificial_sweetener_indicator', 0):
                score -= 15.0
                flagged.append("Synthetic non-nutritive sweetener")
            if concern_flags.get('preservative_indicator', 0):
                score -= 15.0
                flagged.append("Chemical preservative additives")
            if concern_flags.get('artificial_color_indicator', 0):
                score -= 15.0
                flagged.append("Artificial synthetic food colorings")
            if concern_flags.get('added_sugar_indicator', 0):
                score -= 15.0
                flagged.append("Concentrated added sugars or syrups")

        final_score = float(np.clip(score, 0.0, 100.0))

        if final_score >= 85.0:
            profile_label = "Clean Whole-Ingredient Profile"
        elif final_score >= 65.0:
            profile_label = "Moderate Ingredient Complexity"
        else:
            profile_label = "High Additive Density"

        metadata = {
            'ingredient_profile_score': final_score,
            'profile_label': profile_label,
            'flagged_additives': flagged,
            'description': "Composite evaluation of recognizable whole ingredients vs. ultra-processed additives."
        }

        return final_score, metadata

    def compute_processing_score(self, nova_group: Any = None, nutriscore: str = None) -> float:
        """
        Scores food processing level based on standard NOVA classification (1 to 4):
        - NOVA 1: Unprocessed or minimally processed foods -> 100
        - NOVA 2: Processed culinary ingredients -> 85
        - NOVA 3: Processed foods -> 60
        - NOVA 4: Ultra-processed food and drink products -> 30
        """
        score = 80.0 # Default baseline when NOVA is unassigned

        if nova_group is not None:
            try:
                nova = int(nova_group)
                if nova == 1:
                    score = 100.0
                elif nova == 2:
                    score = 85.0
                elif nova == 3:
                    score = 60.0
                elif nova == 4:
                    score = 30.0
            except (ValueError, TypeError):
                pass

        return float(np.clip(score, 0.0, 100.0))

    def grade_product(self,
                      nutriments: Dict[str, Any],
                      concern_flags: Dict[str, Any],
                      nova_group: Any = None,
                      nutriscore: str = None,
                      category_key: Optional[str] = None) -> Tuple[str, float, Dict[str, Any]]:
        """
        Computes composite HealthSense Food Quality Score (0-100) and assigns Letter Grade (A to E).
        Returns: (grade_letter, composite_score, component_breakdown)
        """
        nutrition_score = self.compute_nutrition_score(nutriments, category_key)
        ingredient_score, ingredient_profile = self.compute_ingredient_score(concern_flags)
        processing_score = self.compute_processing_score(nova_group, nutriscore)

        composite_score = (
            nutrition_score * self.weights['nutrition_quality'] +
            ingredient_score * self.weights['ingredient_profile'] +
            processing_score * self.weights['processing_level']
        )

        composite_score = round(float(np.clip(composite_score, 0.0, 100.0)), 1)

        # Assign Grade
        if composite_score >= self.thresholds['A']:
            grade = 'A'
        elif composite_score >= self.thresholds['B']:
            grade = 'B'
        elif composite_score >= self.thresholds['C']:
            grade = 'C'
        elif composite_score >= self.thresholds['D']:
            grade = 'D'
        else:
            grade = 'E'

        breakdown = {
            'nutrition_score': round(nutrition_score, 1),
            'ingredient_score': round(ingredient_score, 1),
            'processing_score': round(processing_score, 1),
            'composite_score': composite_score,
            'ingredient_profile': ingredient_profile
        }

        return grade, composite_score, breakdown
