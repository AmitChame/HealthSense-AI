"""
HealthSense AI V2 — Evidence-Informed Food Analysis Engine
==========================================================
Philosophy:
"HealthSense AI does not diagnose, prescribe, or determine medical safety.
It analyzes available food composition and ingredient information against
documented nutrition evidence and the user's recorded dietary context,
then provides informational food insights with appropriate uncertainty."

Core Layers:
1. General Food Profile (A-E or INSUFFICIENT DATA)
2. Nutrient Findings (WHO, Codex, USDA, FDA, ICMR-NIN with full provenance)
3. Personal Dietary Context (cautious considerations, no medical claims, Kidney Disease special rule)
4. Guidance & Frequency Intelligence (REGULAR, OCCASIONAL, LIMIT FREQUENCY, AVOID, INSUFFICIENT DATA)
5. Data Completeness & Multi-Dimensional Confidence
"""

import math
from typing import Dict, Any, List, Optional, Tuple


class V2DataCompletenessEngine:
    """
    Evaluates data coverage and separates Data Completeness from
    Model Confidence and Evidence Confidence.
    """

    @staticmethod
    def evaluate_completeness(nutriments: Dict[str, Any], ingredients_text: str, allergens_list: List[str]) -> Dict[str, Any]:
        # Evaluated nutrient fields
        core_nutrients = ['calories', 'sugars', 'sodium', 'saturatedFat', 'fats', 'proteins', 'carbohydrates', 'fiber']
        known_core = 0
        missing_core = []

        for k in core_nutrients:
            val = nutriments.get(k)
            if val is not None and not (isinstance(val, float) and (math.isnan(val) or val < 0)):
                known_core += 1
            else:
                missing_core.append(k)

        coverage_pct = round((known_core / len(core_nutrients)) * 100, 1)

        if coverage_pct >= 75:
            nutr_status = "COMPLETE"
        elif coverage_pct >= 37.5:
            nutr_status = "PARTIAL"
        else:
            nutr_status = "LIMITED"

        # Ingredient completeness
        ing_clean = ingredients_text.strip() if ingredients_text else ""
        if len(ing_clean) > 20:
            ing_status = "COMPLETE"
        elif len(ing_clean) > 5:
            ing_status = "PARTIAL"
        else:
            ing_status = "MISSING"

        # Allergen completeness
        if allergens_list and len(allergens_list) > 0:
            allergen_status = "REPORTED"
        elif ing_status == "COMPLETE":
            allergen_status = "PARTIAL" # ingredients present but explicit allergen panel omitted
        else:
            allergen_status = "UNKNOWN"

        return {
            "nutrition_data": nutr_status,
            "nutrition_coverage_pct": coverage_pct,
            "missing_nutrients": missing_core,
            "ingredient_data": ing_status,
            "allergen_data": allergen_status,
            "evidence_applicability": "HIGH" if nutr_status in ["COMPLETE", "PARTIAL"] and ing_status != "MISSING" else "LOW"
        }


class FoodProfileResult(tuple):
    """
    Tuple-subclass that unpacks cleanly as (grade, interpretation, score, factors)
    for 100% backward compatibility with existing callers, while exposing
    rich attributes: .grade, .interpretation, .score, .factors, .methodology, .basis.
    """
    def __new__(cls, grade: str, interpretation: str, score: float, factors: List[str],
                basis: Optional[Dict[str, Any]] = None, methodology: Optional[str] = None):
        return super().__new__(cls, (grade, interpretation, score, factors))

    def __init__(self, grade: str, interpretation: str, score: float, factors: List[str],
                 basis: Optional[Dict[str, Any]] = None, methodology: Optional[str] = None):
        self.grade = grade
        self.interpretation = interpretation
        self.score = score
        self.factors = factors
        self.basis = basis or {}
        self.methodology = methodology or "Nutri-Score Standard Algorithm (Santé Publique France / Rayner Profiling)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grade": self.grade,
            "label": self.interpretation,
            "score": self.score,
            "methodology": self.methodology,
            "basis": self.basis,
            "factors": self.factors
        }


class V2FoodProfileEngine:
    """
    STAGE 1: PRODUCT-LEVEL FOOD PROFILE ENGINE
    ==========================================
    Analyzes packaged food composition independently of any individual person.
    Evaluates only product composition: energy, sugars, saturated fat, sodium, fiber, protein,
    and category (general food vs beverage vs cheese).

    Implements the standard Nutri-Score methodology (Santé Publique France / Rayner Profiling):
    Grade A = "More favorable nutritional profile"
    Grade B = "Generally favorable nutritional profile"
    Grade C = "Mixed / intermediate nutritional profile"
    Grade D = "Less favorable nutritional profile"
    Grade E = "Least favorable nutritional profile"
    or "INSUFFICIENT DATA"

    CRITICAL ARCHITECTURAL GUARANTEE:
    This engine MUST NEVER receive, access, or depend on family member profiles,
    health conditions, age, or allergies. The same product barcode always produces
    the exact same product grade.
    """

    GRADE_INTERPRETATIONS = {
        "A": "More favorable nutritional profile",
        "B": "Generally favorable nutritional profile",
        "C": "Mixed / intermediate nutritional profile",
        "D": "Less favorable nutritional profile",
        "E": "Least favorable nutritional profile",
        "INSUFFICIENT DATA": "Insufficient nutrient information to establish product grade"
    }

    @classmethod
    def calculate_food_profile_standalone(cls, product: Dict[str, Any]) -> FoodProfileResult:
        """
        Calculates the product-level food profile directly from a canonical product dictionary.
        Requires NO family member information.
        """
        nutriments = product.get('nutriments', {})
        categories = product.get('categories', [])
        ingredients = product.get('ingredients', '')
        allergens = product.get('allergens', [])
        completeness = V2DataCompletenessEngine.evaluate_completeness(nutriments, ingredients, allergens)
        
        # Resolve category if string or list
        cat_key = None
        if isinstance(categories, list):
            cat_lower = " ".join(str(c).lower() for c in categories)
        else:
            cat_lower = str(categories).lower()

        if any(b in cat_lower for b in ['beverage', 'drink', 'soda', 'juice']):
            cat_key = 'beverage'
        elif 'cheese' in cat_lower:
            cat_key = 'cheese'

        return cls.calculate_food_profile(nutriments, completeness, cat_key, ingredients)

    @classmethod
    def calculate_food_profile(cls, nutriments: Dict[str, Any], completeness: Dict[str, Any],
                               category_key: Optional[str] = None,
                               ingredients_text: Optional[str] = None) -> FoodProfileResult:
        # If core nutrients are limited (< 3 core nutrients available), do not fabricate certainty
        if completeness.get("nutrition_coverage_pct", 0) < 37.5:
            return FoodProfileResult("INSUFFICIENT DATA", cls.GRADE_INTERPRETATIONS["INSUFFICIENT DATA"], 0.0,
                                     ["Insufficient nutrient data reported on product label."],
                                     basis={}, methodology="Nutri-Score Standard Algorithm")

        is_beverage = category_key in ['beverage', 'beverages', 'energy_drink', 'energy_drinks', 'soft_drink', 'soft_drinks', 'soda', 'juice']
        is_cheese = category_key in ['cheese', 'cheeses']

        # 1. Energy (kJ)
        calories = nutriments.get('calories')
        if calories is None:
            calories = nutriments.get('energy_kcal')
        energy_kj = nutriments.get('energy_kj')
        if energy_kj is None and calories is not None:
            try:
                energy_kj = float(calories) * 4.184
            except (ValueError, TypeError):
                energy_kj = None

        # 2. Total Sugars (g/100g)
        sugars = nutriments.get('sugars')

        # 3. Saturated Fat (g/100g)
        sat_fat = nutriments.get('saturatedFat')
        if sat_fat is None:
            sat_fat = nutriments.get('saturated_fat')

        # 4. Sodium (mg/100g)
        sodium = nutriments.get('sodium')

        # 5. Fiber (g/100g)
        fiber = nutriments.get('fiber')

        # 6. Protein (g/100g)
        protein = nutriments.get('proteins')
        if protein is None:
            protein = nutriments.get('protein')

        # 7. Fruit/Veg/Legume/Nut (FVLN %)
        fvln_pct = 0.0
        ing_lower = ingredients_text.lower() if ingredients_text else ""
        if category_key in ['nut_spread', 'nuts', 'dried_fruits'] or 'peanut' in ing_lower or 'almond' in ing_lower:
            fvln_pct = 80.0 # High whole nut proportion

        # ─── NEGATIVE POINTS (0 to 10 each) ──────────────────────────────────
        # Energy Points
        if is_beverage:
            if energy_kj is None or energy_kj <= 0: p_energy = 0
            elif energy_kj <= 30: p_energy = 1
            elif energy_kj <= 60: p_energy = 2
            elif energy_kj <= 90: p_energy = 3
            elif energy_kj <= 120: p_energy = 4
            elif energy_kj <= 150: p_energy = 5
            elif energy_kj <= 180: p_energy = 6
            elif energy_kj <= 210: p_energy = 7
            elif energy_kj <= 240: p_energy = 8
            elif energy_kj <= 270: p_energy = 9
            else: p_energy = 10
        else:
            if energy_kj is None or energy_kj <= 335: p_energy = 0
            elif energy_kj <= 670: p_energy = 1
            elif energy_kj <= 1005: p_energy = 2
            elif energy_kj <= 1340: p_energy = 3
            elif energy_kj <= 1675: p_energy = 4
            elif energy_kj <= 2010: p_energy = 5
            elif energy_kj <= 2345: p_energy = 6
            elif energy_kj <= 2680: p_energy = 7
            elif energy_kj <= 3015: p_energy = 8
            elif energy_kj <= 3350: p_energy = 9
            else: p_energy = 10

        # Sugars Points
        if is_beverage:
            if sugars is None or sugars <= 0: p_sugars = 0
            elif sugars <= 1.5: p_sugars = 1
            elif sugars <= 3.0: p_sugars = 2
            elif sugars <= 4.5: p_sugars = 3
            elif sugars <= 6.0: p_sugars = 4
            elif sugars <= 7.5: p_sugars = 5
            elif sugars <= 9.0: p_sugars = 6
            elif sugars <= 10.5: p_sugars = 7
            elif sugars <= 12.0: p_sugars = 8
            elif sugars <= 13.5: p_sugars = 9
            else: p_sugars = 10
        else:
            if sugars is None or sugars <= 4.5: p_sugars = 0
            elif sugars <= 9.0: p_sugars = 1
            elif sugars <= 13.5: p_sugars = 2
            elif sugars <= 18.0: p_sugars = 3
            elif sugars <= 22.5: p_sugars = 4
            elif sugars <= 27.0: p_sugars = 5
            elif sugars <= 31.0: p_sugars = 6
            elif sugars <= 36.0: p_sugars = 7
            elif sugars <= 40.0: p_sugars = 8
            elif sugars <= 45.0: p_sugars = 9
            else: p_sugars = 10

        # Saturated Fat Points
        if sat_fat is None or sat_fat <= 1.0: p_sat_fat = 0
        elif sat_fat <= 2.0: p_sat_fat = 1
        elif sat_fat <= 3.0: p_sat_fat = 2
        elif sat_fat <= 4.0: p_sat_fat = 3
        elif sat_fat <= 5.0: p_sat_fat = 4
        elif sat_fat <= 6.0: p_sat_fat = 5
        elif sat_fat <= 7.0: p_sat_fat = 6
        elif sat_fat <= 8.0: p_sat_fat = 7
        elif sat_fat <= 9.0: p_sat_fat = 8
        elif sat_fat <= 10.0: p_sat_fat = 9
        else: p_sat_fat = 10

        # Sodium Points (mg/100g)
        if sodium is None or sodium <= 90.0: p_sodium = 0
        elif sodium <= 180.0: p_sodium = 1
        elif sodium <= 270.0: p_sodium = 2
        elif sodium <= 360.0: p_sodium = 3
        elif sodium <= 450.0: p_sodium = 4
        elif sodium <= 540.0: p_sodium = 5
        elif sodium <= 630.0: p_sodium = 6
        elif sodium <= 720.0: p_sodium = 7
        elif sodium <= 810.0: p_sodium = 8
        elif sodium <= 900.0: p_sodium = 9
        else: p_sodium = 10

        # ─── POSITIVE POINTS (0 to 5 each) ───────────────────────────────────
        # FVLN Points
        if is_beverage:
            if fvln_pct <= 40.0: p_fvln = 0
            elif fvln_pct <= 60.0: p_fvln = 2
            elif fvln_pct <= 80.0: p_fvln = 4
            else: p_fvln = 10
        else:
            if fvln_pct <= 40.0: p_fvln = 0
            elif fvln_pct <= 60.0: p_fvln = 1
            elif fvln_pct <= 80.0: p_fvln = 2
            else: p_fvln = 5

        # Fiber Points
        if fiber is None or fiber <= 0.9: p_fiber = 0
        elif fiber <= 1.9: p_fiber = 1
        elif fiber <= 2.8: p_fiber = 2
        elif fiber <= 3.7: p_fiber = 3
        elif fiber <= 4.7: p_fiber = 4
        else: p_fiber = 5

        # Protein Points
        if protein is None or protein <= 1.6: p_protein = 0
        elif protein <= 3.2: p_protein = 1
        elif protein <= 4.8: p_protein = 2
        elif protein <= 6.4: p_protein = 3
        elif protein <= 8.0: p_protein = 4
        else: p_protein = 5

        # ─── TOTAL AND BALANCING RULE ────────────────────────────────────────
        total_n = p_energy + p_sugars + p_sat_fat + p_sodium
        total_p = p_fiber + p_protein + p_fvln

        if is_beverage:
            final_score = total_n - p_fvln
            protein_counted = False
        elif is_cheese:
            final_score = total_n - total_p
            protein_counted = True
        elif total_n < 11:
            final_score = total_n - total_p
            protein_counted = True
        else:
            if p_fvln >= 5:
                final_score = total_n - total_p
                protein_counted = True
            else:
                final_score = total_n - (p_fiber + p_fvln)
                protein_counted = False

        # ─── GRADE MAPPING ───────────────────────────────────────────────────
        if is_beverage:
            if nutriments.get('is_water'):
                grade = "A"
            elif final_score <= 1:
                grade = "B"
            elif final_score <= 5:
                grade = "C"
            elif final_score <= 9:
                grade = "D"
            else:
                grade = "E"
        else:
            if final_score <= -1:
                grade = "A"
            elif final_score <= 2:
                grade = "B"
            elif final_score <= 10:
                grade = "C"
            elif final_score <= 18:
                grade = "D"
            else:
                grade = "E"

        # Factors list for UI explainability
        factors = [
            f"Energy: {energy_kj:.0f} kJ ({p_energy}/10 negative points)" if energy_kj is not None else "Energy: Not reported",
            f"Total Sugars: {sugars:.1f}g/100g ({p_sugars}/10 negative points)" if sugars is not None else "Total Sugars: Not reported",
            f"Saturated Fat: {sat_fat:.1f}g/100g ({p_sat_fat}/10 negative points)" if sat_fat is not None else "Saturated Fat: Not reported",
            f"Sodium: {sodium:.0f}mg/100g ({p_sodium}/10 negative points)" if sodium is not None else "Sodium: Not reported",
            f"Dietary Fiber: {fiber:.1f}g/100g ({p_fiber}/5 positive points)" if fiber is not None else "Dietary Fiber: Unavailable on label (0 positive points)",
            f"Protein: {protein:.1f}g/100g ({p_protein if protein_counted else 0}/5 positive points{' - protein not counted due to high negative points N >= 11' if not protein_counted and protein is not None else ''})" if protein is not None else "Protein: Not reported",
        ]

        basis = {
            "energy_kj": round(energy_kj, 1) if energy_kj is not None else None,
            "energy_points": p_energy,
            "sugars_g": round(sugars, 1) if sugars is not None else None,
            "sugars_points": p_sugars,
            "saturated_fat_g": round(sat_fat, 1) if sat_fat is not None else None,
            "saturated_fat_points": p_sat_fat,
            "sodium_mg": round(sodium, 1) if sodium is not None else None,
            "sodium_points": p_sodium,
            "fiber_g": round(fiber, 1) if fiber is not None else None,
            "fiber_points": p_fiber,
            "protein_g": round(protein, 1) if protein is not None else None,
            "protein_points": p_protein,
            "protein_counted": protein_counted,
            "fvln_percent": fvln_pct,
            "fvln_points": p_fvln,
            "negative_points": total_n,
            "positive_points": total_p if protein_counted else (p_fiber + p_fvln),
            "final_score": final_score
        }

        return FoodProfileResult(grade, cls.GRADE_INTERPRETATIONS[grade], float(final_score), factors,
                                 basis=basis, methodology="Nutri-Score Standard Algorithm (Santé Publique France / Rayner Profiling)")



class V2NutrientFindingEngine:
    """
    Evaluates individual nutrients against authoritative reference standards.
    Strictly separates total sugar, free sugar, and added sugar without fabricating missing values.
    Does not convert per-100g concentration into daily intake claims without explicit serving & energy context.
    """

    @staticmethod
    def analyze_nutrients(nutriments: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings = []

        # 1. Total Sugars
        total_sugar = nutriments.get('sugars')
        if total_sugar is not None:
            if total_sugar > 22.5:
                status = "Higher concentration"
                desc = f"Total sugar concentration is high at {total_sugar:.1f} g/100g."
            elif total_sugar > 10.0:
                status = "Moderate concentration"
                desc = f"Total sugar concentration is moderate at {total_sugar:.1f} g/100g."
            else:
                status = "Favorable concentration"
                desc = f"Total sugar concentration is low at {total_sugar:.1f} g/100g."

            findings.append({
                "nutrient": "Total Sugars",
                "value": f"{total_sugar:.1f} g/100g",
                "status": status,
                "description": desc,
                "evidence_source": "Codex Alimentarius / National Labelling Standards (Composition Observation)",
                "evidence_notes": "Total sugar is reported by the product data. Free/added sugar information is unavailable, so HealthSense AI does not infer it."
            })
        else:
            findings.append({
                "nutrient": "Total Sugars",
                "value": "Unavailable",
                "status": "Incomplete",
                "description": "Total sugar quantity was not reported on the packaging label.",
                "evidence_source": "Mandatory Nutritional Labelling Standards",
                "evidence_notes": "Missing values are never treated as zero."
            })

        # 2. Free Sugars (Separate Line Item)
        free_sugar = nutriments.get('freeSugars') or nutriments.get('free_sugars')
        if free_sugar is not None:
            findings.append({
                "nutrient": "Free Sugars",
                "value": f"{free_sugar:.1f} g/100g",
                "status": "Higher concentration" if free_sugar > 10.0 else "Moderate concentration",
                "description": f"Product explicitly declares {free_sugar:.1f}g free sugars per 100g.",
                "evidence_source": "WHO Guideline: Sugars intake for adults and children (2015)",
                "evidence_notes": "WHO conditionally recommends limiting free sugars to < 5% of daily energy intake, and strongly < 10%."
            })
        else:
            findings.append({
                "nutrient": "Free Sugars",
                "value": "Unavailable",
                "status": "Unknown",
                "description": "Free sugar is not declared on standard packaging labels, so HealthSense AI does not infer it.",
                "evidence_source": "WHO Guideline: Sugars intake (2015)",
                "evidence_notes": "WHO recommendations apply to free sugars, not total sugars. Total sugar concentration should not be equated with free sugar intake."
            })

        # 3. Added Sugars (Separate Line Item)
        added_sugar = nutriments.get('addedSugars') or nutriments.get('added_sugars')
        if added_sugar is not None:
            findings.append({
                "nutrient": "Added Sugars",
                "value": f"{added_sugar:.1f} g/100g",
                "status": "Higher concentration" if added_sugar > 10.0 else "Moderate concentration" if added_sugar > 5.0 else "Favorable concentration",
                "description": f"Product explicitly reports {added_sugar:.1f}g added sugars per 100g.",
                "evidence_source": "FDA 21 CFR 101.9 / ICMR-NIN 2024",
                "evidence_notes": "Reference daily intakes: US FDA Daily Value is 50g/day; ICMR-NIN recommends < 20-25g/day. Portion size determines actual contribution."
            })
        else:
            findings.append({
                "nutrient": "Added Sugars",
                "value": "Unavailable",
                "status": "Unknown",
                "description": "Added sugar was not reported as a separate line item on the product label.",
                "evidence_source": "National Labelling Regulations",
                "evidence_notes": "HealthSense AI does not assume total sugar equals added sugar without explicit manufacturer declaration."
            })

        # 4. Saturated Fat
        sat_fat = nutriments.get('saturatedFat')
        if sat_fat is not None:
            if sat_fat > 5.0:
                status = "Higher concentration"
                desc = f"Saturated fat concentration is relatively high at {sat_fat:.1f} g/100g."
            elif sat_fat > 2.0:
                status = "Moderate concentration"
                desc = f"Saturated fat concentration is moderate at {sat_fat:.1f} g/100g."
            else:
                status = "Favorable concentration"
                desc = f"Saturated fat concentration is low at {sat_fat:.1f} g/100g."

            findings.append({
                "nutrient": "Saturated Fat",
                "value": f"{sat_fat:.1f} g/100g",
                "status": status,
                "description": desc,
                "evidence_source": "WHO Saturated Fatty Acid Guideline (2023)",
                "evidence_notes": "WHO recommends limiting saturated fatty acids to < 10% of total daily energy intake. Concentration per 100g is an indicator, not a total daily intake measurement."
            })
        else:
            findings.append({
                "nutrient": "Saturated Fat",
                "value": "Unavailable",
                "status": "Incomplete",
                "description": "Saturated fat quantity was not reported on the packaging label.",
                "evidence_source": "Food Labelling Standards",
                "evidence_notes": "Missing values are never treated as zero."
            })

        # 5. Sodium
        sodium = nutriments.get('sodium')
        if sodium is not None:
            if sodium > 600.0:
                status = "Higher concentration"
                desc = f"Sodium concentration is high at {sodium:.0f} mg/100g."
            elif sodium > 300.0:
                status = "Moderate concentration"
                desc = f"Sodium concentration is moderate at {sodium:.0f} mg/100g."
            else:
                status = "Favorable concentration"
                desc = f"Sodium concentration is low at {sodium:.0f} mg/100g."

            findings.append({
                "nutrient": "Sodium",
                "value": f"{sodium:.0f} mg/100g",
                "status": status,
                "description": desc,
                "evidence_source": "WHO Global Report on Sodium Intake Reduction (2023)",
                "evidence_notes": "WHO adult daily benchmark is < 2,000 mg/day (< 5g salt/day). Per-100g concentration informs portion choices and is not identical to daily consumption."
            })
        else:
            findings.append({
                "nutrient": "Sodium",
                "value": "Unavailable",
                "status": "Incomplete",
                "description": "Sodium quantity was not reported on the packaging label.",
                "evidence_source": "Food Labelling Standards",
                "evidence_notes": "Missing values are never treated as zero."
            })

        # 6. Dietary Fiber
        fiber = nutriments.get('fiber')
        if fiber is not None:
            findings.append({
                "nutrient": "Dietary Fiber",
                "value": f"{fiber:.1f} g/100g",
                "status": "Favorable concentration" if fiber >= 3.0 else "Neutral",
                "description": f"Contains {fiber:.1f}g dietary fiber per 100g.",
                "evidence_source": "Codex / WHO Carbohydrate Guidelines (2023)",
                "evidence_notes": "Adequate dietary fiber intake supports digestive and metabolic health."
            })
        else:
            findings.append({
                "nutrient": "Dietary Fiber",
                "value": "Unavailable",
                "status": "Incomplete",
                "description": "Fiber information unavailable on the product label.",
                "evidence_source": "Food Labelling Standards",
                "evidence_notes": "Do not assume 0g fiber merely because it is omitted from the label."
            })

        # 7. Protein
        protein = nutriments.get('proteins')
        if protein is not None:
            findings.append({
                "nutrient": "Protein",
                "value": f"{protein:.1f} g/100g",
                "status": "Favorable concentration" if protein >= 8.0 else "Neutral",
                "description": f"Contains {protein:.1f}g protein per 100g.",
                "evidence_source": "WHO / FAO Protein Requirements",
                "evidence_notes": "Contributes to daily nitrogen and essential amino acid balance."
            })

        return findings


class V2PersonalContextEngine:
    """
    Evaluates food data in the context of an individual family member.
    Enforces cautious informational guidance:
    - Never declares medical safety or diagnoses.
    - Kidney Disease: Enforces conservative uncertainty rule informed by renal nutrition evidence (KDIGO/KDOQI).
    - Allergens: Confirmed conflict triggers hard safety override (AVOID).
    - Life stages: Authoritative pediatric restrictions (stimulant drinks for children).
    - Chronic conditions: Framed as dietary considerations (DIETARY CONSIDERATION / LIMIT FREQUENCY), never 'UNSUITABLE'.
    """

    @classmethod
    def evaluate_member_context(cls, member: Dict[str, Any], nutriments: Dict[str, Any],
                                allergen_flags: Dict[str, bool], detected_allergens: List[str],
                                ingredients_text: str, category_key: Optional[str] = None) -> Dict[str, Any]:
        m_name = member.get('name', 'Member')
        m_age = member.get('age', 30)
        m_conditions = [c.strip().lower() for c in member.get('healthConditions', [])]
        m_allergies = [a.strip().lower() for a in member.get('allergies', [])]
        m_diets = [d.strip().lower() for d in member.get('dietaryPreferences', [])]

        dietary_considerations = []
        hard_safety_conflicts = []
        soft_concerns = []
        uncertainty_notices = []

        is_hard_block = False

        # ─── 1. ALLERGEN EVALUATION ──────────────────────────────────────────
        ing_lower = ingredients_text.lower() if ingredients_text else ""

        for allergy in m_allergies:
            allergen_key = allergy.replace(' ', '_')
            has_conflict = False

            # Check explicit detected allergens and flags
            if any(allergy in da.lower() for da in detected_allergens):
                has_conflict = True
            elif allergen_flags.get(f"contains_{allergen_key}", False):
                has_conflict = True
            elif allergy in ing_lower:
                has_conflict = True

            # Check traces / may contain
            is_trace = False
            if "may contain" in ing_lower and allergy in ing_lower.split("may contain")[-1]:
                is_trace = True

            if has_conflict:
                if not is_trace:
                    is_hard_block = True
                    hard_safety_conflicts.append(f"Confirmed allergen conflict: product contains {allergy.title()}. Strict avoidance recommended.")
                else:
                    soft_concerns.append(f"Precautionary allergen notice: product packaging indicates traces or potential cross-contact with {allergy.title()}.")

        if not ingredients_text or len(ingredients_text.strip()) <= 5:
            if m_allergies:
                uncertainty_notices.append("Ingredient text is unavailable. Allergen presence or cross-contact cannot be verified from available data.")

        # ─── 2. SPECIAL RULE: KIDNEY DISEASE / RENAL DIET ─────────────────────
        has_kidney_condition = any("kidney" in c or "renal" in c or "ckd" in c or "nephro" in c for c in m_conditions)
        if has_kidney_condition:
            uncertainty_notices.append(
                "Renal-diet suitability cannot be determined reliably from this product label. "
                "HealthSense AI implements a conservative uncertainty rule informed by the limitations and nutritional "
                "considerations described in renal nutrition evidence (such as KDIGO 2020 / KDOQI clinical practice guidelines). "
                "Standard food packaging does not declare potassium or bioavailable phosphorus additives. "
                "Always consult your nephrologist or renal dietitian."
            )
            dietary_considerations.append("Kidney Disease context: Clinical parameters (potassium, phosphorus) are not declared on standard food labels; professional guidance required.")

        # ─── 3. HEALTH CONDITIONS (Cautious Non-Medical Considerations) ───────
        # Diabetes
        if any("diabet" in c or "sugar" in c or "insulin" in c for c in m_conditions):
            sugars = nutriments.get('sugars')
            if sugars is not None:
                if sugars > 15.0:
                    dietary_considerations.append(f"Personal context: Diabetes recorded. Total sugar concentration is high at {sugars:.1f}g/100g. Free/added sugar information is unavailable, so this finding should be evaluated as an informational dietary consideration rather than a medical assessment.")
                    soft_concerns.append(f"Total sugar concentration is high at {sugars:.1f}g/100g; consider limiting frequency for glycemic monitoring.")
                elif sugars > 7.0:
                    dietary_considerations.append(f"Personal context: Diabetes recorded. Moderate total sugar concentration ({sugars:.1f}g/100g) warrants portion awareness.")
                else:
                    dietary_considerations.append(f"Personal context: Diabetes recorded. Low total sugar profile ({sugars:.1f}g/100g) aligns favorably with general carbohydrate awareness.")
            else:
                uncertainty_notices.append("Total sugar information is unavailable on the label; glycemic consideration cannot be evaluated.")

        # Hypertension
        if any("hypertens" in c or "blood pressure" in c or "bp" in c for c in m_conditions):
            sodium = nutriments.get('sodium')
            if sodium is not None:
                if sodium > 400.0:
                    dietary_considerations.append(f"Personal context: Hypertension / blood pressure recorded. Sodium concentration ({sodium:.0f}mg/100g) is elevated; portion moderation is a dietary consideration.")
                    soft_concerns.append(f"Elevated sodium concentration ({sodium:.0f}mg/100g) warrants portion awareness for blood pressure management.")
                elif sodium > 200.0:
                    dietary_considerations.append(f"Personal context: Hypertension recorded. Moderate sodium concentration ({sodium:.0f}mg/100g).")
                else:
                    dietary_considerations.append(f"Personal context: Hypertension recorded. Low sodium concentration ({sodium:.0f}mg/100g).")
            else:
                uncertainty_notices.append("Sodium information is unavailable on the label; sodium consideration cannot be evaluated.")

        # High Cholesterol / Lipid Profile
        if any("cholesterol" in c or "lipid" in c or "heart" in c or "cardio" in c for c in m_conditions):
            sat_fat = nutriments.get('saturatedFat')
            if sat_fat is not None:
                if sat_fat > 4.0:
                    dietary_considerations.append(f"Personal context: Lipid profile / cholesterol recorded. Saturated fat concentration ({sat_fat:.1f}g/100g) may be a dietary consideration for cardiovascular monitoring.")
                    soft_concerns.append(f"High saturated fat concentration ({sat_fat:.1f}g/100g) may be a dietary consideration for lipid management; consider limiting frequency.")
                elif sat_fat > 2.0:
                    dietary_considerations.append(f"Personal context: Lipid profile recorded. Moderate saturated fat concentration ({sat_fat:.1f}g/100g).")
                else:
                    dietary_considerations.append(f"Personal context: Lipid profile recorded. Low saturated fat concentration ({sat_fat:.1f}g/100g).")
            else:
                uncertainty_notices.append("Saturated fat content is unavailable on label; lipid consideration cannot be evaluated.")

        # ─── 4. DIETARY PREFERENCES ──────────────────────────────────────────
        for diet in m_diets:
            if "vegan" in diet:
                if any(term in ing_lower for term in ["milk", "dairy", "whey", "casein", "egg", "meat", "gelatin", "honey"]):
                    soft_concerns.append("Dietary preference note: Ingredients list indicates potential animal-derived components.")
                    dietary_considerations.append("Vegan preference: Check full packaging ingredients for animal derivatives.")
            elif "vegetarian" in diet:
                if any(term in ing_lower for term in ["meat", "beef", "chicken", "pork", "fish", "gelatin"]):
                    soft_concerns.append("Dietary preference note: Ingredients list indicates potential non-vegetarian components (e.g. gelatin or animal derivatives).")
                    dietary_considerations.append("Vegetarian preference: Check packaging for non-vegetarian additives.")

        # ─── 5. PEDIATRIC & AGE LOGIC ────────────────────────────────────────
        if m_age < 4:
            sugars = nutriments.get('sugars')
            if sugars is not None and sugars > 10.0:
                dietary_considerations.append(f"Early childhood (Age {m_age}): AAP and WHO guidance advise minimizing concentrated sugars in young children; total sugar is {sugars:.1f}g/100g.")
                soft_concerns.append(f"High total sugar density ({sugars:.1f}g/100g) is a dietary consideration for children under 4.")
        elif m_age < 12:
            if category_key in ["energy_drinks", "energy_drink"] or "caffeine" in ing_lower or "taurine" in ing_lower:
                is_hard_block = True
                hard_safety_conflicts.append(f"Child safety alert: Energy drinks and high-caffeine formulations are contraindicated for children under 12 (EFSA/AAP guidance).")
            else:
                sugars = nutriments.get('sugars')
                if sugars is not None and sugars > 20.0:
                    dietary_considerations.append(f"Childhood nutrition (Age {m_age}): Total sugar concentration is {sugars:.1f}g/100g. Free/added sugar is not declared on label.")
                    soft_concerns.append(f"Elevated total sugar concentration ({sugars:.1f}g/100g) warrants portion awareness for children.")

        return {
            "is_hard_block": is_hard_block,
            "dietary_considerations": dietary_considerations,
            "hard_safety_conflicts": hard_safety_conflicts,
            "soft_concerns": soft_concerns,
            "uncertainty_notices": uncertainty_notices
        }


class V2GuidanceEngine:
    """
    Synthesizes food profile, evidence findings, personal context, and data completeness
    into transparent, cautious guidance and appropriate frequency tiers.
    Rules:
    - Never declares medical safety or prescriptions.
    - Never outputs 'DAILY'.
    - Hard safety (allergens, young child stimulant drinks) -> AVOID.
    - Ordinary nutrition (sugar, sat fat, sodium, processing) -> REGULAR, OCCASIONAL, LIMIT FREQUENCY, or INSUFFICIENT DATA.
    """

    @classmethod
    def determine_guidance(cls, member_name: str, food_profile_grade: str,
                           personal_eval: Dict[str, Any], completeness: Dict[str, Any],
                           nutriments: Dict[str, Any]) -> Tuple[str, str, str, str]:
        # 1. Hard Safety Override (Confirmed allergen conflict or explicit child contraindication)
        if personal_eval["is_hard_block"]:
            frequency = "AVOID"
            status_label = "AVOID"
            summary_reason = " ".join(personal_eval["hard_safety_conflicts"])
            guidance = "Strict avoidance advised due to confirmed allergen conflict or statutory child restriction."
            return status_label, frequency, summary_reason, guidance

        # 2. Insufficient Data Fallback
        if completeness["nutrition_coverage_pct"] < 37.5:
            frequency = "INSUFFICIENT DATA"
            status_label = "INSUFFICIENT DATA"
            summary_reason = "Product nutrition information is incomplete or unverified; reliable nutritional comparison cannot be formed."
            guidance = "Check packaging label directly; available digital data is insufficient for a reliable assessment."
            return status_label, frequency, summary_reason, guidance

        # 3. Kidney Disease Specific Handling
        has_ckd_uncertainty = any("renal" in un.lower() or "kidney" in un.lower() for un in personal_eval["uncertainty_notices"])
        if has_ckd_uncertainty:
            status_label = "INSUFFICIENT INFORMATION"
            frequency = "LIMIT FREQUENCY"
            summary_reason = "Renal-diet suitability cannot be determined reliably from this product information alone. Consult your renal dietitian."
            guidance = "Packaged food labels lack potassium and bioavailable phosphorus values critical for renal diets. Professional guidance required."
            if personal_eval["uncertainty_notices"]:
                summary_reason = f"{summary_reason} [Notice: {' • '.join(personal_eval['uncertainty_notices'])}]"
            return status_label, frequency, summary_reason, guidance

        # 4. Ordinary Nutritional Evaluation (Never AVOID or UNSUITABLE)
        has_concerns = len(personal_eval["soft_concerns"]) > 0 or food_profile_grade in ["D", "E"]
        sugars = nutriments.get('sugars', 0.0) or 0.0
        sat_fat = nutriments.get('saturatedFat', 0.0) or 0.0

        if food_profile_grade == "E" or (sugars > 35.0 and sat_fat > 10.0):
            frequency = "LIMIT FREQUENCY"
            status_label = "HIGHER CONCERN"
            guidance = "Consider limiting consumption frequency and being mindful of portion size due to elevated saturated fat and sugar concentrations."
            reasons = []
            if sugars > 25.0:
                reasons.append(f"total sugar concentration is high at {sugars:.1f}g/100g")
            if sat_fat > 8.0:
                reasons.append(f"saturated fat concentration is elevated at {sat_fat:.1f}g/100g")
            summary_reason = f"Product presents higher-concern characteristics ({', '.join(reasons)}) relative to reference nutrition benchmarks."
        elif has_concerns or food_profile_grade in ["C", "D"]:
            frequency = "OCCASIONAL"
            status_label = "DIETARY CONSIDERATION"
            guidance = "Consider this food occasionally with portion mindfulness in the context of an overall balanced diet."
            if personal_eval["soft_concerns"]:
                summary_reason = personal_eval["soft_concerns"][0]
            else:
                summary_reason = "Nutritional profile shows mixed characteristics with moderate sugar, sodium, or fat."
        else:
            frequency = "REGULAR"
            status_label = "FAVORABLE"
            guidance = "Product demonstrates a generally favorable nutritional composition based on available data; suitable for regular inclusion in a varied diet."
            summary_reason = "Analyzed nutrient values align favorably with general population dietary references."

        # Append any other uncertainty notices
        if personal_eval["uncertainty_notices"]:
            uncertainty_text = " • ".join(personal_eval["uncertainty_notices"])
            summary_reason = f"{summary_reason} [Notice: {uncertainty_text}]"

        return status_label, frequency, summary_reason, guidance

    @classmethod
    def calculate_personal_guidance(cls, product: Dict[str, Any], food_profile: Any,
                                    family_member: Dict[str, Any],
                                    allergen_flags: Optional[Dict[str, bool]] = None,
                                    detected_allergens: Optional[List[str]] = None,
                                    category_key: Optional[str] = None,
                                    completeness: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        STAGE 2: PERSON-LEVEL PERSONALIZED GUIDANCE
        ===========================================
        Input:
          product data
          + food_profile (from Stage 1)
          + family_member (age, health conditions, allergies, dietary preferences)
        
        Output:
          Personalized guidance for the specific family member.
          Guarantees that food_profile.grade is copied as product_grade and NEVER mutated!
        """
        nutriments = product.get('nutriments', {})
        ingredients_text = product.get('ingredients', '')
        allergen_flags = allergen_flags or {}
        detected_allergens = detected_allergens or []
        completeness = completeness or {"nutrition_coverage_pct": 100.0, "nutrition_data": "COMPLETE"}

        grade_letter = getattr(food_profile, 'grade', str(food_profile))

        # Evaluate personal context
        personal_eval = V2PersonalContextEngine.evaluate_member_context(
            member=family_member,
            nutriments=nutriments,
            allergen_flags=allergen_flags,
            detected_allergens=detected_allergens,
            ingredients_text=ingredients_text,
            category_key=category_key
        )

        m_name = family_member.get('name', 'Member')
        m_id = family_member.get('id', '')
        m_age = family_member.get('age', 30)

        status_label, member_frequency, summary_reason, guidance_text = cls.determine_guidance(
            member_name=m_name,
            food_profile_grade=grade_letter,
            personal_eval=personal_eval,
            completeness=completeness,
            nutriments=nutriments
        )

        allergen_status = "NONE_DETECTED"
        if personal_eval["is_hard_block"] and personal_eval["hard_safety_conflicts"]:
            allergen_status = "CONFIRMED_ALLERGEN_CONFLICT"
        elif personal_eval["soft_concerns"] and any("trace" in sc.lower() or "cross-contact" in sc.lower() for sc in personal_eval["soft_concerns"]):
            allergen_status = "PRECAUTIONARY_TRACE"

        return {
            "member_id": m_id,
            "name": m_name,
            "age": m_age,
            "product_grade": grade_letter,  # Guaranteed immutable product-level grade
            "guidance": member_frequency,   # REGULAR, OCCASIONAL, LIMIT FREQUENCY, AVOID, INSUFFICIENT INFORMATION
            "status": status_label,
            "findings": personal_eval["dietary_considerations"],
            "summary_reason": summary_reason,
            "guidance_text": guidance_text,
            "allergen_status": allergen_status,
            "uncertainty_notices": personal_eval["uncertainty_notices"],
            "hard_safety_conflicts": personal_eval["hard_safety_conflicts"],
            "soft_concerns": personal_eval["soft_concerns"]
        }


