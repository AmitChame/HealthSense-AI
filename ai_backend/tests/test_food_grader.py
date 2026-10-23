"""
Unit tests for Standalone HealthSense Food Quality Grader.
"""

import pytest
from src.features.food_grader import HealthSenseFoodGrader


def test_food_grader_healthy_oats():
    grader = HealthSenseFoodGrader()

    nutriments = {
        'sugars_100g': 1.0,
        'sodium_100g': 5.0,
        'saturated_fat_100g': 0.5,
        'fiber_100g': 8.0,
        'protein_100g': 12.0,
        'energy_kcal_100g': 360.0
    }
    concerns = {
        'added_sugar_indicator': 0,
        'artificial_sweetener_indicator': 0,
        'preservative_indicator': 0,
        'artificial_color_indicator': 0,
        'hydrogenated_oil_indicator': 0
    }

    grade, score, breakdown = grader.grade_product(nutriments, concerns, nova_group=1)
    assert grade in ['A', 'B']
    assert score >= 75.0


def test_food_grader_ultra_processed_sugary_snack():
    grader = HealthSenseFoodGrader()

    nutriments = {
        'sugars_100g': 38.0,
        'sodium_100g': 550.0,
        'saturated_fat_100g': 12.0,
        'fiber_100g': 0.5,
        'protein_100g': 2.0,
        'energy_kcal_100g': 490.0
    }
    concerns = {
        'added_sugar_indicator': 1,
        'artificial_color_indicator': 1,
        'preservative_indicator': 1,
        'hydrogenated_oil_indicator': 1
    }

    grade, score, breakdown = grader.grade_product(nutriments, concerns, nova_group=4)
    assert grade in ['D', 'E']
    assert score <= 45.0
