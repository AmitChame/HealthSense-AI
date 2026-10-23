"""
Evidence Registry for HealthSense AI.
Loads and indexes authoritative nutritional, medical, composition, and dietary standards.
Ensures zero fabricated standards and preserves jurisdiction and source provenance.
"""

from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class EvidenceRegistry:
    """
    Registry providing query access to authoritative nutritional and food composition standards.
    Supports filtering by parameter, jurisdiction, standard_type, and life_stage.
    """

    _instance: Optional['EvidenceRegistry'] = None

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            config_path = str(base_dir / "config" / "evidence_standards.yaml")

        self.config_path = config_path
        self.metadata: Dict[str, Any] = {}
        self.standards: List[Dict[str, Any]] = []
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self._by_param: Dict[str, List[Dict[str, Any]]] = {}
        self._load_standards()

    @classmethod
    def get_instance(cls, config_path: Optional[str] = None) -> 'EvidenceRegistry':
        """Singleton accessor for thread-safe in-memory caching."""
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance

    def _load_standards(self):
        if not os.path.exists(self.config_path):
            logger.warning(f"Evidence standards configuration file not found at: {self.config_path}")
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}

            self.metadata = data.get('metadata', {})
            self.standards = data.get('standards', [])

            for record in self.standards:
                eid = record.get('evidence_id')
                if eid:
                    self._by_id[eid] = record

                param = record.get('nutrient_or_parameter')
                if param:
                    if param not in self._by_param:
                        self._by_param[param] = []
                    self._by_param[param].append(record)

        except Exception as e:
            logger.error(f"Failed to parse evidence standards YAML: {e}")

    def get_by_id(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an evidence record by unique ID."""
        return self._by_id.get(evidence_id)

    def find_standards(self,
                       parameter: Optional[str] = None,
                       jurisdiction: Optional[str] = None,
                       standard_type: Optional[str] = None,
                       life_stage: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Queries standards matching specified criteria.
        Hierarchy preference: WHO / CODEX (GLOBAL) -> National (IN, US, EU).
        """
        results = self.standards

        if parameter:
            results = [r for r in results if r.get('nutrient_or_parameter') == parameter]

        if jurisdiction:
            # Allow GLOBAL standards if specific jurisdiction doesn't supersede
            results = [r for r in results if r.get('jurisdiction') in [jurisdiction, "GLOBAL"]]

        if standard_type:
            results = [r for r in results if r.get('standard_type') == standard_type]

        if life_stage:
            results = [r for r in results if r.get('life_stage') in [life_stage, "ALL", "GENERAL", "ALL_EXCEPT_INFANTS"]]

        return results

    def get_reference_value(self, parameter: str, jurisdiction: str = "GLOBAL", life_stage: str = "ADULT") -> Optional[Dict[str, Any]]:
        """
        Finds the primary applicable reference value for a parameter, respecting source hierarchy.
        Preference: WHO > National statutory body (FSSAI/FDA) > Codex.
        """
        candidates = self.find_standards(parameter=parameter, jurisdiction=jurisdiction, life_stage=life_stage)
        if not candidates:
            # Fallback to general life stage
            candidates = self.find_standards(parameter=parameter, jurisdiction=jurisdiction)

        if not candidates:
            return None

        # Prioritize according to hierarchy
        hierarchy = ["WHO", "CODEX", "FSSAI", "FDA", "EFSA", "ICMR-NIN"]
        for org in hierarchy:
            for c in candidates:
                if c.get('source_organization') == org:
                    return c

        return candidates[0]
