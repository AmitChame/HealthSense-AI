"""
Unit tests for Safety Rule Engine.
"""

import pytest
from src.rules.rule_engine import HealthSenseRuleEngine


def test_hard_allergen_override_peanut():
    engine = HealthSenseRuleEngine()

    product_data = {
        'nutriments': {'sugars_100g': 2.0, 'sodium_100g': 100.0, 'saturated_fat_100g': 1.0},
        'allergen_flags': {'contains_peanut': True, 'contains_milk': False},
        'detected_allergens': ['Peanut']
    }

    # Member with peanut allergy
    member_profile = {
        'name': 'Sarah',
        'age': 12,
        'allergies': ['Peanuts'],
        'health_conditions': []
    }

    triggered = engine.evaluate(product_data, member_profile)
    assert len(triggered) > 0
    assert engine.has_hard_block(triggered) is True

    allergen_rule = next((r for r in triggered if r.category == 'ALLERGEN'), None)
    assert allergen_rule is not None
    assert allergen_rule.recommendation == 'AVOID'
    assert allergen_rule.risk_score_impact == 100.0


def test_diabetes_high_sugar_rule():
    engine = HealthSenseRuleEngine()

    # Product with 22g sugar / 100g
    product_data = {
        'nutriments': {'sugars_100g': 22.0},
        'allergen_flags': {},
        'detected_allergens': []
    }

    member_profile = {
        'name': 'John',
        'age': 52,
        'health_conditions': ['Diabetes (Type 2)'],
        'allergies': []
    }

    triggered = engine.evaluate(product_data, member_profile)
    sugar_rule = next((r for r in triggered if 'DIABETES' in r.rule_id), None)
    assert sugar_rule is not None
    assert sugar_rule.recommendation == 'AVOID'
    assert sugar_rule.severity == 'HIGH'


def test_hypertension_high_sodium_rule():
    engine = HealthSenseRuleEngine()

    # Product with 650mg sodium / 100g
    product_data = {
        'nutriments': {'sodium_100g': 650.0},
        'allergen_flags': {},
        'detected_allergens': []
    }

    member_profile = {
        'name': 'Grandpa',
        'age': 75,
        'health_conditions': ['Hypertension'],
        'allergies': []
    }

    triggered = engine.evaluate(product_data, member_profile)
    sodium_rule = next((r for r in triggered if 'HYPERTENSION' in r.rule_id), None)
    assert sodium_rule is not None
    assert sodium_rule.recommendation == 'AVOID'


def test_child_safety_caffeine_rule():
    engine = HealthSenseRuleEngine()

    product_data = {
        'normalized_ingredients': 'carbonated water, sugar, caffeine, taurine, citric acid',
        'categories': ['en:energy-drinks'],
        'nutriments': {'sugars_100g': 11.0},
        'allergen_flags': {},
        'detected_allergens': []
    }

    child_profile = {
        'name': 'Leo',
        'age': 8,
        'health_conditions': [],
        'allergies': []
    }

    triggered = engine.evaluate(product_data, child_profile)
    caffeine_rule = next((r for r in triggered if r.rule_id == 'child_caffeine_energy'), None)
    assert caffeine_rule is not None
    assert caffeine_rule.recommendation == 'AVOID'
    assert caffeine_rule.severity == 'HIGH'


def test_vegetarian_preference_rule():
    engine = HealthSenseRuleEngine()

    product_data = {
        'normalized_ingredients': 'sugar, gelatin, glucose syrup, natural flavors',
        'concern_flags': {'contains_animal_derived': True, 'contains_meat_or_gelatin': True},
        'nutriments': {'sugars_100g': 55.0},
        'allergen_flags': {},
        'detected_allergens': []
    }

    veg_profile = {
        'name': 'Priya',
        'age': 28,
        'dietary_preferences': ['Vegetarian'],
        'health_conditions': [],
        'allergies': []
    }

    triggered = engine.evaluate(product_data, veg_profile)
    veg_rule = next((r for r in triggered if r.category == 'DIETARY_PREFERENCE'), None)
    assert veg_rule is not None
    assert veg_rule.recommendation == 'AVOID'
