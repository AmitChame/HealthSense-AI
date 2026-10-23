"""
Edge case testing for HealthSense AI recommendation engine.
"""

import pytest
from src.features.nutrition_features import NutritionFeaturePipeline
from src.rules.rule_engine import HealthSenseRuleEngine
from src.features.food_grader import HealthSenseFoodGrader


def test_missing_nutrition_values_handled_gracefully():
    pipeline = NutritionFeaturePipeline()
    # Empty nutriments map
    feats = pipeline.extract_features({})

    assert feats['is_sugar_missing'] == 1.0
    assert feats['is_sodium_missing'] == 1.0
    assert feats['sugar_to_carb_ratio'] == 0.0


def test_empty_member_profile_handled_safely():
    engine = HealthSenseRuleEngine()

    product_data = {
        'nutriments': {'sugars_100g': 5.0},
        'allergen_flags': {'contains_peanut': False},
        'detected_allergens': []
    }

    # Empty member profile
    member_profile = {
        'name': 'Unknown Member',
        'age': 25,
        'health_conditions': [],
        'allergies': [],
        'dietary_preferences': []
    }

    triggered = engine.evaluate(product_data, member_profile)
    assert len(triggered) == 0
    assert engine.has_hard_block(triggered) is False


def test_product_with_no_ingredients():
    grader = HealthSenseFoodGrader()
    grade, score, breakdown = grader.grade_product({}, {}, nova_group=None)
    assert grade in ['A', 'B', 'C', 'D', 'E']
    assert 0.0 <= score <= 100.0
