"""
Life-Stage Personalization Engine for HealthSense AI.
Evaluates nutritional suitability, risk thresholds, and dietary considerations
across evidence-backed life stages: Young Child, Child, Adolescent, Adult, and Older Adult.

Based on guidance from WHO, American Academy of Pediatrics (AAP), ICMR-NIN (2024),
and European Society for Clinical Nutrition and Metabolism (ESPEN).
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class LifeStageEngine:
    """
    Maps biological age to evidence-based life-stage profiles with specific reference standards,
    sensitivities, and safety constraints. Never assumes older age equates to disease.
    """

    LIFE_STAGES: Dict[str, Dict[str, Any]] = {
        'YOUNG_CHILD': {
            'name': 'Young Child / Toddler',
            'age_min': 1,
            'age_max': 4,
            'reference_energy_kcal': 1200.0,
            'daily_sugar_max_g': 0.0, # WHO / AAP recommendation: zero added sugars under 2; strictly minimized for 2-4
            'daily_sodium_max_mg': 1000.0,
            'caffeine_permitted': False,
            'special_considerations': [
                "Zero added sugar recommended by WHO/AAP to protect metabolic health and taste development.",
                "Strict sodium limit to protect immature renal function.",
                "Stimulants and artificial caffeine are strictly not recommended.",
                "High nutrient density requirement relative to small stomach capacity."
            ],
            'evidence_source': 'WHO Guideline on Sugars (2015) / AAP Pediatric Guidance'
        },
        'CHILD': {
            'name': 'School-Age Child',
            'age_min': 5,
            'age_max': 11,
            'reference_energy_kcal': 1600.0,
            'daily_sugar_max_g': 25.0, # WHO < 10% energy (~25g free sugar)
            'daily_sodium_max_mg': 1500.0,
            'caffeine_permitted': False,
            'special_considerations': [
                "Limit free sugars to under 25g/day to prevent dental caries and obesity.",
                "Sodium maximum scaled down based on energy requirement (<1,500 mg).",
                "High caffeine energy drinks contraindicated (EFSA / FSSAI).",
                "Caution with artificial food colors linked to behavioral sensitivities."
            ],
            'evidence_source': 'WHO Sodium & Sugar Guidelines for Children (2012/2015)'
        },
        'ADOLESCENT': {
            'name': 'Adolescent',
            'age_min': 12,
            'age_max': 17,
            'reference_energy_kcal': 2200.0,
            'daily_sugar_max_g': 35.0,
            'daily_sodium_max_mg': 2000.0,
            'caffeine_permitted': True,
            'caffeine_max_mg_day': 100.0, # EFSA recommendation: max 3 mg/kg bw
            'special_considerations': [
                "Rapid growth and bone mineral accrual: elevated requirement for protein, calcium, and iron.",
                "Energy drink caution: high-dose caffeine and taurine combinations warrant strict limitation.",
                "Monitor saturated fat and sodium in ultra-processed convenience foods."
            ],
            'evidence_source': 'EFSA Caffeine Safety Opinion (2015) / ICMR-NIN Adolescent RDA'
        },
        'ADULT': {
            'name': 'Adult',
            'age_min': 18,
            'age_max': 64,
            'reference_energy_kcal': 2000.0,
            'daily_sugar_max_g': 50.0, # WHO 10% energy standard (< 25g for conditional benefit)
            'daily_sodium_max_mg': 2000.0, # WHO < 2,000 mg
            'caffeine_permitted': True,
            'caffeine_max_mg_day': 400.0, # EFSA / FDA safe upper intake for adults
            'special_considerations': [
                "Standard adult dietary reference intakes apply.",
                "Limit free sugars to <10% energy, saturated fat to <10% energy, sodium to <2,000 mg/day."
            ],
            'evidence_source': 'WHO Healthy Diet Guidelines / FDA 21 CFR 101.9'
        },
        'OLDER_ADULT': {
            'name': 'Older Adult',
            'age_min': 65,
            'age_max': 125,
            'reference_energy_kcal': 1800.0,
            'daily_sugar_max_g': 40.0,
            'daily_sodium_max_mg': 2000.0,
            'caffeine_permitted': True,
            'caffeine_max_mg_day': 300.0,
            'special_considerations': [
                "Higher protein density per calorie required to prevent sarcopenia and preserve lean muscle mass (ESPEN / ICMR).",
                "Cardiovascular sodium moderation is beneficial without unwarranted micronutrient restriction.",
                "Age alone does not imply illness; foods are not labeled unhealthy merely due to chronological age.",
                "Hydration and dietary fiber support digestive and metabolic health."
            ],
            'evidence_source': 'ESPEN Guidelines on Clinical Nutrition & Geriatrics (2019) / ICMR-NIN'
        }
    }

    @classmethod
    def resolve_life_stage(cls, age: Optional[int]) -> Dict[str, Any]:
        """
        Resolves biological age to the corresponding evidence-based life stage.
        If age is omitted or invalid, defaults to general ADULT baseline.
        """
        if age is None:
            stage_key = 'ADULT'
        else:
            try:
                age_val = int(age)
                if age_val < 5:
                    stage_key = 'YOUNG_CHILD'
                elif age_val < 12:
                    stage_key = 'CHILD'
                elif age_val < 18:
                    stage_key = 'ADOLESCENT'
                elif age_val < 65:
                    stage_key = 'ADULT'
                else:
                    stage_key = 'OLDER_ADULT'
            except (ValueError, TypeError):
                stage_key = 'ADULT'

        profile = dict(cls.LIFE_STAGES[stage_key])
        profile['key'] = stage_key
        return profile

    @classmethod
    def evaluate_life_stage_suitability(cls, age: Optional[int], product_nutrients: Dict[str, Any], concern_flags: Dict[str, Any], category_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluates product suitability against life-stage nutritional limits.
        Returns guidance, cautions, and explicit reasons.
        """
        stage = cls.resolve_life_stage(age)
        cautions: List[str] = []
        is_restricted = False

        sugars = product_nutrients.get('sugars')
        sodium = product_nutrients.get('sodium')

        # 1. Young Child Restrictions
        if stage['key'] == 'YOUNG_CHILD':
            if sugars is not None and sugars > 10.0:
                cautions.append(f"Sugar content ({sugars:.1f}g/100g) exceeds the strict low-sugar threshold recommended for toddlers and young children.")
            if sodium is not None and sodium > 300.0:
                cautions.append(f"Elevated sodium ({sodium:.0f}mg/100g) requires strict moderation for young children.")
            if category_key == 'energy_drink':
                is_restricted = True
                cautions.append("Caffeinated energy beverages are strictly contraindicated for young children.")

        # 2. School-Age Child Restrictions
        elif stage['key'] == 'CHILD':
            if category_key == 'energy_drink':
                is_restricted = True
                cautions.append("High caffeine stimulant drinks are not recommended for children under 12 years (EFSA/FSSAI).")
            if concern_flags.get('artificial_color_indicator'):
                cautions.append("Contains artificial color additives that warrant portion caution in school-age children.")
            if sugars is not None and sugars > 20.0:
                cautions.append(f"High total sugar concentration ({sugars:.1f}g/100g) warrants portion awareness for school-age children; free/added sugar is not declared on label.")

        # 3. Adolescent Considerations
        elif stage['key'] == 'ADOLESCENT':
            if category_key == 'energy_drink':
                cautions.append("High caffeine concentration: adolescents should strictly limit energy beverage consumption.")

        # 4. Older Adult Considerations
        elif stage['key'] == 'OLDER_ADULT':
            protein = product_nutrients.get('protein')
            fiber = product_nutrients.get('fiber')
            # Positive acknowledgment of nutrient density
            if protein is not None and protein >= 8.0:
                pass # favorable for older adults
            if sodium is not None and sodium > 500.0:
                cautions.append("Elevated sodium: moderation recommended to maintain optimal cardiovascular health.")

        return {
            'life_stage': stage['key'],
            'life_stage_name': stage['name'],
            'is_age_restricted': is_restricted,
            'cautions': cautions,
            'considerations': stage['special_considerations'],
            'evidence_source': stage['evidence_source']
        }
