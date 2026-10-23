"""
Base Rule Interface for HealthSense Safety & Health Rules.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class RuleResult:
    triggered: bool
    rule_id: str
    category: str       # ALLERGEN, CHRONIC_CONDITION, DIETARY_PREFERENCE, CHILD_SAFETY, GENERAL_HEALTH
    severity: str       # CRITICAL, HIGH, MODERATE, LOW
    recommendation: str # AVOID, CAUTION, RECOMMENDED
    risk_score_impact: float
    explanation: str
    is_hard_block: bool = False
    detected_value: Optional[str] = None
    threshold_value: Optional[str] = None
    evidence_id: Optional[str] = None
    evidence_source: Optional[str] = None


class BaseSafetyRule(ABC):
    """
    Abstract base class for all deterministic safety and health rules.
    """

    def __init__(self, rule_id: str, category: str, severity: str, evidence_id: Optional[str] = None):
        self.rule_id = rule_id
        self.category = category
        self.severity = severity
        self.evidence_id = evidence_id

    @abstractmethod
    def evaluate(self, product_data: Dict[str, Any], member_profile: Dict[str, Any]) -> Optional[RuleResult]:
        """
        Evaluates product data against member health profile.
        Returns a RuleResult if triggered, else None.
        """
        pass
