"""
Phase 3 Comprehensive Evidence, Life-Stage, Category Standards,
Nutrient Normalization, and Frequency Intelligence Test Suite.
"""

import pytest
from src.evidence.evidence_registry import EvidenceRegistry
from src.evidence.nutrient_normalizer import NutrientNormalizer
from src.evidence.category_engine import FoodCategoryEngine
from src.evidence.life_stage_engine import LifeStageEngine
from src.evidence.frequency_engine import FrequencyIntelligenceEngine
from src.features.food_grader import HealthSenseFoodGrader
from rest_framework.test import APIClient
from rest_framework import status


# ─── 1. EVIDENCE REGISTRY TESTS ──────────────────────────────────────────────

class TestEvidenceRegistry:
    """Verifies that all evidence records originate from authoritative sources with no fabricated data."""

    def test_registry_loads_standards(self):
        registry = EvidenceRegistry.get_instance()
        assert len(registry.standards) >= 10, "Registry must contain authoritative standards"
        assert registry.metadata.get('version') == "1.0.0"

    def test_who_sugar_standard_exists(self):
        registry = EvidenceRegistry.get_instance()
        std = registry.get_by_id("EVID_WHO_SUGARS_2015")
        assert std is not None
        assert std['source_organization'] == "WHO"
        assert std['maximum'] == 10.0
        assert std['unit'] == "PERCENT_ENERGY"
        assert std['evidence_status'] == "OFFICIAL_ACTIVE"

    def test_who_sodium_standard_exists(self):
        registry = EvidenceRegistry.get_instance()
        std = registry.get_by_id("EVID_WHO_SODIUM_2023")
        assert std is not None
        assert std['source_organization'] == "WHO"
        assert std['maximum'] == 2000.0
        assert std['unit'] == "mg"

    def test_codex_chocolate_composition_standard(self):
        registry = EvidenceRegistry.get_instance()
        std = registry.get_by_id("EVID_CODEX_CHOCOLATE_CXS87")
        assert std is not None
        assert std['source_organization'] == "CODEX"
        assert std['minimum'] == 35.0
        assert std['standard_type'] == "FOOD_COMPOSITION_STANDARD"

    def test_jurisdiction_filtering_does_not_mix_standards(self):
        registry = EvidenceRegistry.get_instance()
        in_standards = registry.find_standards(jurisdiction="IN")
        assert any(s['jurisdiction'] == "IN" for s in in_standards)
        # FDA standards must not be labeled as GLOBAL or IN
        fda_std = registry.get_by_id("EVID_FDA_ADDED_SUGARS_DV")
        assert fda_std['jurisdiction'] == "US"


# ─── 2. NUTRIENT NORMALIZATION & SERVING SIZE TESTS ──────────────────────────

class TestNutrientNormalizer:
    """Verifies serving size parsing, per-serving calculation, and reference contributions."""

    def test_parse_serving_size_grams(self):
        amt, unit = NutrientNormalizer.parse_serving_size("30 g")
        assert amt == 30.0
        assert unit == "g"

    def test_parse_serving_size_with_parentheses(self):
        amt, unit = NutrientNormalizer.parse_serving_size("1 pouch (45 g)")
        assert amt == 45.0
        assert unit == "g"

    def test_parse_serving_size_liquid_milliliters(self):
        amt, unit = NutrientNormalizer.parse_serving_size("250 ml")
        assert amt == 250.0
        assert unit == "ml"

    def test_missing_serving_size_returns_none(self):
        amt, unit = NutrientNormalizer.parse_serving_size(None)
        assert amt is None
        assert unit is None
        amt, unit = NutrientNormalizer.parse_serving_size("")
        assert amt is None
        assert unit is None

    def test_normalize_nutrients_computes_serving_contributions(self):
        raw = {
            'sugars_100g': 20.0,
            'sodium_100g': 400.0,
            'energy_kcal_100g': 400.0,
            'proteins': 10.0
        }
        res = NutrientNormalizer.normalize_nutrients(raw, "50 g")

        # 50g is 0.5 of 100g
        assert res['per_serving']['sugars'] == 10.0
        assert res['per_serving']['sodium'] == 200.0
        assert res['per_serving']['energy_kcal'] == 200.0
        assert res['serving_size']['is_available'] is True

        # Reference contribution: 10g sugar / 50g reference = 20.0%
        assert res['reference_contributions']['sugars'] == 20.0
        # Sodium: 200mg / 2000mg reference = 10.0%
        assert res['reference_contributions']['sodium'] == 10.0

    def test_missing_nutrient_not_treated_as_zero(self):
        raw = {'energy_kcal_100g': 150.0} # sugars and sodium absent
        res = NutrientNormalizer.normalize_nutrients(raw, "30 g")
        assert res['per_100g']['sugars'] is None
        assert res['per_serving']['sugars'] is None
        assert res['data_status']['sugars'] == "UNKNOWN"
        assert res['reference_contributions']['sugars'] is None


# ─── 3. FOOD CATEGORY & COMPOSITION STANDARD TESTS ───────────────────────────

class TestFoodCategoryEngine:
    """Verifies food category identification and composition standard validation."""

    def test_resolve_chocolate_category(self):
        engine = FoodCategoryEngine.get_instance()
        cat = engine.resolve_category(["en:chocolates"], "Dark Chocolate Bar", "cocoa mass, sugar, cocoa butter")
        assert cat is not None
        assert cat['key'] == "chocolate"
        assert "Codex" in cat['composition_standards']['source']

    def test_resolve_energy_drink_category(self):
        engine = FoodCategoryEngine.get_instance()
        cat = engine.resolve_category(["en:energy-drinks"], "Max Energy Drink", "water, caffeine, taurine, sugar")
        assert cat is not None
        assert cat['key'] == "energy_drink"
        assert cat['pediatric_restriction'] == "STRICT_AVOID_UNDER_12"

    def test_resolve_oats_category(self):
        engine = FoodCategoryEngine.get_instance()
        cat = engine.resolve_category(["en:rolled-oats"], "Rolled Oats", "100% whole grain oats")
        assert cat is not None
        assert cat['key'] == "oats"
        assert cat['baseline_frequency'] == "REGULAR"

    def test_chocolate_composition_standard_evaluation(self):
        engine = FoodCategoryEngine.get_instance()
        context = {
            'normalized_ingredients': 'cocoa mass, sugar, cocoa butter, vanilla extract'
        }
        eval_res = engine.evaluate_composition_standard("chocolate", context)
        assert eval_res['has_standard'] is True
        assert eval_res['meets_standard'] is True
        assert "Cocoa Composition" in eval_res['standard_name']
        assert "not healthfulness" in eval_res['conceptual_clarification']


# ─── 4. LIFE-STAGE PERSONALIZATION TESTS ─────────────────────────────────────

class TestLifeStageEngine:
    """Verifies life-stage boundary mapping and age-appropriate constraints."""

    def test_life_stage_boundary_resolution(self):
        assert LifeStageEngine.resolve_life_stage(2)['key'] == "YOUNG_CHILD"
        assert LifeStageEngine.resolve_life_stage(4)['key'] == "YOUNG_CHILD"
        assert LifeStageEngine.resolve_life_stage(5)['key'] == "CHILD"
        assert LifeStageEngine.resolve_life_stage(11)['key'] == "CHILD"
        assert LifeStageEngine.resolve_life_stage(12)['key'] == "ADOLESCENT"
        assert LifeStageEngine.resolve_life_stage(17)['key'] == "ADOLESCENT"
        assert LifeStageEngine.resolve_life_stage(18)['key'] == "ADULT"
        assert LifeStageEngine.resolve_life_stage(64)['key'] == "ADULT"
        assert LifeStageEngine.resolve_life_stage(65)['key'] == "OLDER_ADULT"
        assert LifeStageEngine.resolve_life_stage(80)['key'] == "OLDER_ADULT"

    def test_young_child_sugar_restriction(self):
        eval_res = LifeStageEngine.evaluate_life_stage_suitability(
            age=3,
            product_nutrients={'sugars': 18.0, 'sodium': 100.0},
            concern_flags={}
        )
        assert eval_res['life_stage'] == "YOUNG_CHILD"
        assert any("strict low-sugar threshold" in c for c in eval_res['cautions'])

    def test_child_energy_drink_restriction(self):
        eval_res = LifeStageEngine.evaluate_life_stage_suitability(
            age=8,
            product_nutrients={'sugars': 10.0},
            concern_flags={},
            category_key="energy_drink"
        )
        assert eval_res['life_stage'] == "CHILD"
        assert eval_res['is_age_restricted'] is True
        assert any("not recommended for children under 12" in c for c in eval_res['cautions'])

    def test_older_adult_not_automatically_diseased(self):
        eval_res = LifeStageEngine.evaluate_life_stage_suitability(
            age=72,
            product_nutrients={'sugars': 3.0, 'sodium': 150.0, 'protein': 12.0},
            concern_flags={}
        )
        assert eval_res['life_stage'] == "OLDER_ADULT"
        assert eval_res['is_age_restricted'] is False
        assert len(eval_res['cautions']) == 0 # Clean healthy product produces no cautions


# ─── 5. FREQUENCY INTELLIGENCE TESTS ─────────────────────────────────────────

class TestFrequencyIntelligenceEngine:
    """Verifies evidence-backed consumption frequency guidance."""

    def test_oats_qualify_for_regular_frequency(self):
        res = FrequencyIntelligenceEngine.determine_frequency(
            food_grade="A",
            product_nutrients={'sugars': 1.0, 'sodium': 10.0, 'saturated_fat': 0.5},
            concern_flags={},
            category_key="oats",
            life_stage="ADULT"
        )
        assert res['frequency'] == "REGULAR"
        assert "regular inclusion" in res['explanation'].lower()

    def test_chocolate_confectionery_is_occasional(self):
        res = FrequencyIntelligenceEngine.determine_frequency(
            food_grade="C",
            product_nutrients={'sugars': 35.0, 'saturated_fat': 14.0},
            concern_flags={},
            category_key="chocolate",
            life_stage="ADULT"
        )
        assert res['frequency'] == "OCCASIONAL"
        assert "occasional consumption" in res['explanation'].lower()

    def test_energy_drink_is_limit(self):
        res = FrequencyIntelligenceEngine.determine_frequency(
            food_grade="D",
            product_nutrients={'sugars': 12.0},
            concern_flags={},
            category_key="energy_drink",
            life_stage="ADULT"
        )
        assert res['frequency'] == "LIMIT"

    def test_hard_block_overrides_to_avoid(self):
        res = FrequencyIntelligenceEngine.determine_frequency(
            food_grade="A",
            product_nutrients={'sugars': 1.0, 'sodium': 10.0},
            concern_flags={},
            category_key="oats",
            life_stage="ADULT",
            has_hard_block=True
        )
        assert res['frequency'] == "AVOID"


# ─── 6. FOOD QUALITY GRADER WITH INGREDIENT PROFILE TESTS ────────────────────

class TestFoodGraderIngredientProfile:
    """Verifies transparent ingredient profile scoring without fake naturalness."""

    def test_clean_ingredient_profile(self):
        grader = HealthSenseFoodGrader()
        _, _, breakdown = grader.grade_product(
            nutriments={'sugars_100g': 2.0, 'fiber_100g': 6.0, 'protein_100g': 10.0},
            concern_flags={},
            nova_group=1
        )
        prof = breakdown['ingredient_profile']
        assert prof['ingredient_profile_score'] == 100.0
        assert prof['profile_label'] == "Clean Whole-Ingredient Profile"
        assert len(prof['flagged_additives']) == 0

    def test_ultra_processed_additive_profile(self):
        grader = HealthSenseFoodGrader()
        _, _, breakdown = grader.grade_product(
            nutriments={'sugars_100g': 30.0},
            concern_flags={'hydrogenated_oil_indicator': 1, 'artificial_color_indicator': 1},
            nova_group=4
        )
        prof = breakdown['ingredient_profile']
        assert prof['ingredient_profile_score'] <= 60.0
        assert len(prof['flagged_additives']) >= 2


# ─── 7. FULL API END-TO-END WITH PHASE 3 FIELDS ──────────────────────────────

class TestPhase3APIIntegration:
    """Integration test ensuring API responds with all Phase 3 evidence-backed fields."""

    def setup_method(self):
        self.client = APIClient()

    def test_health_check_endpoint_phase3(self):
        response = self.client.get('/api/health/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == "healthy"
        assert "Phase 3" in data.get('phase', '')

    def test_recommend_endpoint_returns_phase3_fields(self):
        payload = {
            "foodProduct": {
                "barcode": "8901234567890",
                "productName": "Whole Grain Rolled Oats",
                "brand": "Quaker",
                "ingredients": "100% whole grain rolled oats",
                "servingSize": "40 g",
                "categories": ["en:rolled-oats"],
                "nutriments": {
                    "calories": 375.0,
                    "sugars": 1.0,
                    "sodium": 5.0,
                    "fats": 7.0,
                    "saturatedFat": 1.2,
                    "proteins": 12.5,
                    "carbohydrates": 60.0,
                    "fiber": 10.0
                }
            },
            "familyMembers": [
                {
                    "id": "member_toddler",
                    "name": "Leo (Toddler)",
                    "age": 3,
                    "healthConditions": [],
                    "allergies": []
                },
                {
                    "id": "member_grandparent",
                    "name": "Kamala (Senior)",
                    "age": 70,
                    "healthConditions": ["Hypertension"],
                    "allergies": []
                }
            ]
        }
        response = self.client.post('/api/v1/recommend/', payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check top-level Phase 3 fields
        assert 'foodCategory' in data
        assert data['foodCategory']['key'] == "oats"
        assert 'servingInfo' in data
        assert data['servingInfo']['amount'] == 40.0
        assert 'referenceContributions' in data
        assert 'confidenceBreakdown' in data
        assert data['confidenceBreakdown']['evidenceConfidence'] == "HIGH"
        assert 'evidenceSources' in data
        assert len(data['evidenceSources']) > 0

        # Check member-level Phase 3 fields
        recs = data['recommendations']
        assert len(recs) == 2

        toddler_rec = next(r for r in recs if r['familyMemberId'] == "member_toddler")
        assert toddler_rec['lifeStage'] == "YOUNG_CHILD"
        assert toddler_rec['frequencyRecommendation'] == "REGULAR"

        senior_rec = next(r for r in recs if r['familyMemberId'] == "member_grandparent")
        assert senior_rec['lifeStage'] == "OLDER_ADULT"
        assert senior_rec['category'] == "RECOMMENDED"
