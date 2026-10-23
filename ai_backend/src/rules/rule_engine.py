"""
Rule Engine Evaluator for HealthSense AI.
Executes safety rules and returns deterministic violations, hard blocks,
and rule-based risk factors with full evidence traceability.
"""

from typing import List, Dict, Any, Optional
import os
import yaml
from .base_rule import BaseSafetyRule, RuleResult
from .safety_rules import AllergenRule, HealthConditionRule, DietaryPreferenceRule, ChildSafetyRule
from .config_manager import HealthSenseConfigManager


class HealthSenseRuleEngine:
    """
    Evaluates a collection of deterministic safety and medical rules.
    Maintains 100% evidence traceability linking to evidence_standards.yaml.
    """

    def __init__(self, config_dir: Optional[str] = None):
        self.rules: List[BaseSafetyRule] = []
        self.config_manager = HealthSenseConfigManager(config_dir)
        self._load_rules()

    def _load_rules(self):
        """
        Initializes rules from centralized configuration.
        """
        # 1. Load Hard Safety Rules (Allergens)
        hard_rules = self.config_manager.rules_config.get('hard_safety_rules', {})
        for key, r in hard_rules.items():
            if r.get('category') == 'ALLERGEN':
                name = key.replace('_allergy', '').replace('_', ' ')
                self.rules.append(AllergenRule(
                    rule_id=r['id'],
                    allergen_name=name,
                    condition_field=r['condition_field'],
                    trigger_flag=r['trigger_flag'],
                    explanation=r['explanation'],
                    evidence_id=r.get('evidence_id')
                ))

        # 2. Load Health Condition Rules
        cond_rules = self.config_manager.rules_config.get('health_condition_rules', {})
        for key, r in cond_rules.items():
            self.rules.append(HealthConditionRule(
                rule_id=r['id'],
                condition_name=r['condition_field'],
                metric_key=r['metric'],
                threshold_avoid=r['threshold_avoid'],
                threshold_caution=r['threshold_caution'],
                explanation_avoid=r['explanation_avoid'],
                explanation_caution=r['explanation_caution'],
                evidence_id=r.get('evidence_id'),
                evidence_source=r.get('evidence_source')
            ))

        # 3. Load Dietary Preference Rules
        diet_rules = self.config_manager.rules_config.get('dietary_preference_rules', {})
        for key, r in diet_rules.items():
            self.rules.append(DietaryPreferenceRule(
                rule_id=r['id'],
                preference_name=r['condition_field'],
                trigger_flag=r['trigger_flag'],
                explanation=r['explanation'],
                evidence_id=r.get('evidence_id')
            ))

        # 4. Load Age-Aware Child Safety Rules
        self.rules.append(ChildSafetyRule(
            rule_id="child_explicit_warning",
            max_age=18,
            check_type="explicit_warning",
            explanation="Explicit manufacturer restriction applies to age {age}.",
            severity="CRITICAL",
            recommendation="AVOID",
            is_hard_block=True,
            evidence_id="EVID_MANUFACTURER_RESTRICTION",
            evidence_source="Statutory Product Labelling"
        ))
        self.rules.append(ChildSafetyRule(
            rule_id="child_caffeine_energy",
            max_age=12,
            check_type="caffeine_energy",
            explanation="High caffeine or energy drink formulations are not recommended for children (Age {age}).",
            severity="HIGH",
            recommendation="AVOID",
            evidence_id="EVID_EFSA_CAFFEINE_CHILDREN",
            evidence_source="EFSA Caffeine Scientific Opinion (2015)"
        ))
        self.rules.append(ChildSafetyRule(
            rule_id="child_artificial_colors",
            max_age=12,
            check_type="artificial_colors",
            explanation="Contains artificial food colorings that warrant portion caution for children (Age {age}).",
            severity="MODERATE",
            recommendation="CAUTION",
            evidence_id="EVID_EU_COLORANTS_WARNING",
            evidence_source="EU Regulation (EC) No 1333/2008"
        ))
        self.rules.append(ChildSafetyRule(
            rule_id="young_child_sugar_sodium",
            max_age=5,
            check_type="young_child_sugar_sodium",
            explanation="Elevated sugar or sodium levels require strict moderation for young children (Age {age}).",
            severity="MODERATE",
            recommendation="CAUTION",
            evidence_id="EVID_AAP_WHO_YOUNG_CHILD_SUGAR",
            evidence_source="WHO Guideline on Sugars (2015) / AAP Guidance"
        ))

    def evaluate(self, product_data: Dict[str, Any], member_profile: Dict[str, Any]) -> List[RuleResult]:
        """
        Evaluates all safety rules against the member health profile and product data.
        """
        triggered_results: List[RuleResult] = []
        for rule in self.rules:
            res = rule.evaluate(product_data, member_profile)
            if res and res.triggered:
                triggered_results.append(res)

        # Manually evaluate General Health Rules for everyone
        gen_rules = self.config_manager.rules_config.get('general_health_rules', {})
        nutriments = product_data.get('nutriments', {})

        for key, r in gen_rules.items():
            metric = r.get('metric')
            threshold = r.get('threshold_caution')
            val = nutriments.get(metric)
            if val is not None and not isinstance(val, str) and val >= threshold:
                triggered_results.append(RuleResult(
                    triggered=True,
                    rule_id=r['id'],
                    category="GENERAL_HEALTH",
                    severity="MODERATE",
                    recommendation="CAUTION",
                    risk_score_impact=20.0,
                    explanation=r['explanation'].format(value=val),
                    is_hard_block=False,
                    detected_value=f"{val:.1f}",
                    threshold_value=f"<{threshold:.1f}",
                    evidence_id=r.get('evidence_id'),
                    evidence_source=r.get('evidence_source')
                ))

        return triggered_results

    def has_hard_block(self, triggered_rules: List[RuleResult]) -> bool:
        """
        Returns True if any triggered rule is a hard safety block (e.g. Allergen conflict).
        """
        return any(r.is_hard_block for r in triggered_rules)
