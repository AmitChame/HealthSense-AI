"""
Implementations of Deterministic Safety Rules, Allergen Overrides, and Health Condition Rules.
Maintains full evidence traceability (linking to evidence_standards.yaml).
"""

from typing import Dict, Any, Optional
from .base_rule import BaseSafetyRule, RuleResult


class AllergenRule(BaseSafetyRule):
    """
    Hard Safety Rule for Allergen Conflicts.
    If a family member has an allergy and the product contains it,
    it triggers an absolute deterministic AVOID override.
    """

    def __init__(self, rule_id: str, allergen_name: str, condition_field: str, trigger_flag: str,
                 explanation: str, evidence_id: Optional[str] = None):
        super().__init__(rule_id=rule_id, category="ALLERGEN", severity="CRITICAL", evidence_id=evidence_id)
        self.allergen_name = allergen_name
        self.condition_field = condition_field
        self.trigger_flag = trigger_flag
        self.explanation = explanation

    def evaluate(self, product_data: Dict[str, Any], member_profile: Dict[str, Any]) -> Optional[RuleResult]:
        # Check if member has this allergy
        allergies = member_profile.get('allergies', [])
        has_allergy = False

        if isinstance(allergies, list):
            for a in allergies:
                if isinstance(a, str) and (self.allergen_name.lower() in a.lower() or a.lower() in self.allergen_name.lower()):
                    has_allergy = True
                    break

        if not has_allergy and member_profile.get(self.condition_field, False):
            has_allergy = True

        if not has_allergy:
            return None

        # Check if product contains allergen
        allergen_flags = product_data.get('allergen_flags', {})
        contains_allergen = allergen_flags.get(self.trigger_flag, False)

        # Check detected allergens list
        if not contains_allergen:
            detected_allergens = product_data.get('detected_allergens', [])
            for da in detected_allergens:
                if self.allergen_name.lower() in da.lower():
                    contains_allergen = True
                    break

        if contains_allergen:
            return RuleResult(
                triggered=True,
                rule_id=self.rule_id,
                category=self.category,
                severity=self.severity,
                recommendation="AVOID",
                risk_score_impact=100.0,
                explanation=self.explanation,
                is_hard_block=True,
                detected_value=self.allergen_name,
                threshold_value="0 tolerance",
                evidence_id=self.evidence_id,
                evidence_source="Codex Alimentarius General Standard for the Labelling of Prepackaged Foods (CXS 1-1985)"
            )

        return None


class HealthConditionRule(BaseSafetyRule):
    """
    Nutritional Safety Rule for Chronic Health Conditions (Diabetes, Hypertension, Cholesterol, etc.).
    """

    def __init__(self, rule_id: str, condition_name: str, metric_key: str,
                 threshold_avoid: float, threshold_caution: float,
                 explanation_avoid: str, explanation_caution: str,
                 evidence_id: Optional[str] = None, evidence_source: Optional[str] = None):
        super().__init__(rule_id=rule_id, category="CHRONIC_CONDITION", severity="HIGH", evidence_id=evidence_id)
        self.condition_name = condition_name
        self.metric_key = metric_key
        self.threshold_avoid = threshold_avoid
        self.threshold_caution = threshold_caution
        self.explanation_avoid = explanation_avoid
        self.explanation_caution = explanation_caution
        self.evidence_source = evidence_source

    def evaluate(self, product_data: Dict[str, Any], member_profile: Dict[str, Any]) -> Optional[RuleResult]:
        # Check if member has this condition
        conditions = member_profile.get('health_conditions', member_profile.get('healthConditions', []))
        has_condition = False

        if isinstance(conditions, list):
            for c in conditions:
                if isinstance(c, str) and self.condition_name.lower() in c.lower():
                    has_condition = True
                    break

        if not has_condition and member_profile.get(self.condition_name.lower(), False):
            has_condition = True

        if not has_condition:
            return None

        # Check nutritional metric
        nutriments = product_data.get('nutriments', {})
        value = nutriments.get(self.metric_key)

        if value is None or str(value) == 'nan':
            return None

        try:
            val_float = float(value)
        except (ValueError, TypeError):
            return None

        if val_float >= self.threshold_avoid:
            return RuleResult(
                triggered=True,
                rule_id=self.rule_id,
                category=self.category,
                severity=self.severity,
                recommendation="AVOID",
                risk_score_impact=60.0,
                explanation=self.explanation_avoid.format(value=val_float, threshold=self.threshold_avoid),
                is_hard_block=False,
                detected_value=f"{val_float:.1f}",
                threshold_value=f"<{self.threshold_avoid:.1f}",
                evidence_id=self.evidence_id,
                evidence_source=self.evidence_source
            )
        elif val_float >= self.threshold_caution:
            return RuleResult(
                triggered=True,
                rule_id=self.rule_id,
                category=self.category,
                severity="MODERATE",
                recommendation="CAUTION",
                risk_score_impact=30.0,
                explanation=self.explanation_caution.format(value=val_float, threshold=self.threshold_caution),
                is_hard_block=False,
                detected_value=f"{val_float:.1f}",
                threshold_value=f"<{self.threshold_caution:.1f}",
                evidence_id=self.evidence_id,
                evidence_source=self.evidence_source
            )

        return None


class DietaryPreferenceRule(BaseSafetyRule):
    """
    Rule for Dietary Preferences (Vegetarian, Vegan).
    """

    def __init__(self, rule_id: str, preference_name: str, trigger_flag: str,
                 explanation: str, evidence_id: Optional[str] = None):
        super().__init__(rule_id=rule_id, category="DIETARY_PREFERENCE", severity="MEDIUM", evidence_id=evidence_id)
        self.preference_name = preference_name
        self.trigger_flag = trigger_flag
        self.explanation = explanation

    def evaluate(self, product_data: Dict[str, Any], member_profile: Dict[str, Any]) -> Optional[RuleResult]:
        preferences = member_profile.get('dietary_preferences', member_profile.get('dietaryPreferences', []))
        has_pref = False

        if isinstance(preferences, list):
            for p in preferences:
                if isinstance(p, str) and self.preference_name.lower() in p.lower():
                    has_pref = True
                    break

        if not has_pref and member_profile.get(self.preference_name.lower(), False):
            has_pref = True

        if not has_pref:
            return None

        concern_flags = product_data.get('concern_flags', {})
        if concern_flags.get(self.trigger_flag, False):
            return RuleResult(
                triggered=True,
                rule_id=self.rule_id,
                category=self.category,
                severity=self.severity,
                recommendation="AVOID",
                risk_score_impact=40.0,
                explanation=self.explanation,
                is_hard_block=False,
                detected_value="Animal derivative detected",
                threshold_value="Plant-based required",
                evidence_id=self.evidence_id,
                evidence_source="Standard Dietary Composition Taxonomy"
            )

        return None


class ChildSafetyRule(BaseSafetyRule):
    """
    Age-Aware Child Safety Rule.
    Evaluates age-related dietary constraints such as high caffeine/energy drinks,
    artificial food colors linked to hyperactivity, excessive sodium, and manufacturer age restrictions.
    """

    def __init__(self, rule_id: str, max_age: int, check_type: str, explanation: str,
                 severity: str = "HIGH", recommendation: str = "AVOID", is_hard_block: bool = False,
                 evidence_id: Optional[str] = None, evidence_source: Optional[str] = None):
        super().__init__(rule_id=rule_id, category="CHILD_SAFETY", severity=severity, evidence_id=evidence_id)
        self.max_age = max_age
        self.check_type = check_type
        self.explanation = explanation
        self.rec = recommendation
        self.is_hard = is_hard_block
        self.evidence_source = evidence_source or "WHO/EFSA Pediatric Safety Consensus"

    def evaluate(self, product_data: Dict[str, Any], member_profile: Dict[str, Any]) -> Optional[RuleResult]:
        age = member_profile.get('age')
        if age is None:
            return None
        try:
            age_int = int(age)
        except (ValueError, TypeError):
            return None

        if age_int >= self.max_age:
            return None

        # 1. Explicit manufacturer warning check
        explicit_warning = product_data.get('explicit_child_warning')
        if self.check_type == 'explicit_warning' and explicit_warning:
            return RuleResult(
                triggered=True,
                rule_id=self.rule_id,
                category=self.category,
                severity="CRITICAL",
                recommendation="AVOID",
                risk_score_impact=100.0,
                explanation=f"Explicit Manufacturer Warning: {explicit_warning}",
                is_hard_block=True,
                detected_value=f"Age {age_int} (Restriction applies)",
                threshold_value=f"Age >= {self.max_age}",
                evidence_id=self.evidence_id or "EVID_MANUFACTURER_RESTRICTION",
                evidence_source="Packaging Statutory Restriction"
            )

        # 2. Caffeine / Energy Drink check
        if self.check_type == 'caffeine_energy':
            norm_ing = product_data.get('normalized_ingredients', '').lower()
            categories = [str(c).lower() for c in product_data.get('categories', [])]
            
            is_caffeine = ('caffeine' in norm_ing or 'energy drink' in norm_ing or 
                           'taurine' in norm_ing or 'guarana' in norm_ing or 
                           any('energy drink' in c or 'energy-drinks' in c for c in categories))
            if is_caffeine:
                return RuleResult(
                    triggered=True,
                    rule_id=self.rule_id,
                    category=self.category,
                    severity="HIGH",
                    recommendation="AVOID",
                    risk_score_impact=70.0,
                    explanation=self.explanation.format(age=age_int),
                    is_hard_block=False,
                    detected_value="Caffeine / Stimulants present",
                    threshold_value=f"Not recommended for Age < {self.max_age}",
                    evidence_id="EVID_EFSA_CAFFEINE_CHILDREN",
                    evidence_source="EFSA Caffeine Scientific Opinion (2015) / FSSAI"
                )

        # 3. Artificial Colors check
        if self.check_type == 'artificial_colors':
            concern_flags = product_data.get('concern_flags', {})
            if concern_flags.get('artificial_color_indicator'):
                return RuleResult(
                    triggered=True,
                    rule_id=self.rule_id,
                    category=self.category,
                    severity="MODERATE",
                    recommendation="CAUTION",
                    risk_score_impact=30.0,
                    explanation=self.explanation.format(age=age_int),
                    is_hard_block=False,
                    detected_value="Artificial colorants present",
                    threshold_value=f"Caution for Age < {self.max_age}",
                    evidence_id="EVID_EU_COLORANTS_WARNING",
                    evidence_source="EU Regulation (EC) No 1333/2008 on Food Additives"
                )

        # 4. Young Child Sugar & Sodium check
        if self.check_type == 'young_child_sugar_sodium':
            nutr = product_data.get('nutriments', {})
            sugar = nutr.get('sugars_100g')
            sodium = nutr.get('sodium_100g')
            
            is_high_sugar = sugar is not None and not str(sugar) == 'nan' and float(sugar) > 20.0
            is_high_sodium = sodium is not None and not str(sodium) == 'nan' and float(sodium) > 400.0

            if is_high_sugar or is_high_sodium:
                trigger_reasons = []
                if is_high_sugar:
                    trigger_reasons.append(f"Sugar {float(sugar):.1f}g/100g")
                if is_high_sodium:
                    trigger_reasons.append(f"Sodium {float(sodium):.0f}mg/100g")
                    
                return RuleResult(
                    triggered=True,
                    rule_id=self.rule_id,
                    category=self.category,
                    severity="MODERATE",
                    recommendation="CAUTION",
                    risk_score_impact=35.0,
                    explanation=self.explanation.format(age=age_int) + f" ({', '.join(trigger_reasons)})",
                    is_hard_block=False,
                    detected_value=", ".join(trigger_reasons),
                    threshold_value=f"Strict limits for Age < {self.max_age}",
                    evidence_id="EVID_AAP_WHO_YOUNG_CHILD_SUGAR",
                    evidence_source="WHO Guideline on Sugars (2015) / AAP Guidance"
                )

        return None
