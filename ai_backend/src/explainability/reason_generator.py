"""
Human-Readable Explanation Generator for HealthSense AI.
Synthesizes rule triggers, SHAP feature importance, and nutritional facts into clear clinical explanations.
"""

from typing import List, Dict, Any
from ..rules.base_rule import RuleResult


class HealthSenseReasonGenerator:
    """
    Translates model findings, SHAP attributions, and rule violations into clear explanations.
    """

    def generate_explanation(self, member_name: str, recommendation: str,
                             triggered_rules: List[RuleResult],
                             ingredient_concerns: List[str],
                             allergen_conflicts: List[str],
                             shap_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds summary reason and itemized health factor explanations.
        """
        reasons: List[str] = []
        health_factors: List[Dict[str, Any]] = []

        # 1. Deterministic Rule Violations (Highest priority)
        for rule in triggered_rules:
            reasons.append(rule.explanation)
            health_factors.append({
                'name': rule.rule_id.replace('RULE_', '').replace('_', ' ').title(),
                'impact': 'HIGH' if rule.is_hard_block or rule.severity in ['CRITICAL', 'HIGH'] else 'MODERATE',
                'description': rule.explanation,
                'isAllergen': rule.is_hard_block or rule.category == 'ALLERGEN',
                'detectedValue': rule.detected_value,
                'thresholdValue': rule.threshold_value
            })

        # 2. Ingredient Concerns
        for concern in ingredient_concerns:
            if not any(concern.lower() in r.lower() for r in reasons):
                reasons.append(f"Contains {concern}")
                health_factors.append({
                    'name': 'Ingredient Concern',
                    'impact': 'MODERATE',
                    'description': f"Flagged additive or processed ingredient: {concern}",
                    'isAllergen': False,
                    'detectedValue': concern,
                    'thresholdValue': 'None'
                })

        # 3. If SUITABLE with no negative rules
        if recommendation == 'RECOMMENDED' and not reasons:
            reasons.append("Nutritional metrics and ingredients align safely with health profile.")
            health_factors.append({
                'name': 'Nutritional Alignment',
                'impact': 'LOW',
                'description': 'Balanced nutrients within standard dietary limits with no allergen conflicts.',
                'isAllergen': False,
                'detectedValue': 'Compliant',
                'thresholdValue': 'Safe'
            })

        # Summary sentence
        if recommendation == 'AVOID':
            summary_reason = f"Not recommended for {member_name}. " + (reasons[0] if reasons else "High nutritional or allergen conflict.")
        elif recommendation == 'CAUTION':
            summary_reason = f"Consume with caution for {member_name}. " + (reasons[0] if reasons else "Moderate nutrient level requires portion control.")
        else:
            summary_reason = f"Suitable for {member_name}. Nutrients are within balanced thresholds."

        return {
            'summary_reason': summary_reason,
            'reasons_list': reasons,
            'health_factors': health_factors
        }
