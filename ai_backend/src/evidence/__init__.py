"""
HealthSense AI Evidence & Standards Module.
Provides authoritative nutritional standards, life-stage personalization,
food category standards, nutrient normalization, and frequency intelligence.
"""

from .evidence_registry import EvidenceRegistry
from .nutrient_normalizer import NutrientNormalizer
from .category_engine import FoodCategoryEngine
from .life_stage_engine import LifeStageEngine
from .frequency_engine import FrequencyIntelligenceEngine

__all__ = [
    'EvidenceRegistry',
    'NutrientNormalizer',
    'FoodCategoryEngine',
    'LifeStageEngine',
    'FrequencyIntelligenceEngine'
]
