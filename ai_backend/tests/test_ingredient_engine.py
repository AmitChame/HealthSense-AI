"""
Unit tests for Ingredient Engine (Normalizer, Allergen Detector, Concern Detector).
"""

import pytest
from src.ingredient_engine.normalizer import IngredientNormalizer
from src.ingredient_engine.allergen_detector import AllergenDetector
from src.ingredient_engine.concern_detector import ConcernDetector


def test_ingredient_normalizer_cleans_noise():
    normalizer = IngredientNormalizer()
    raw = "Contains less than 2% of: Salt, Sugar, Natural Flavors [from wheat], Preservatives (BHT)*."
    cleaned = normalizer.clean_text(raw)
    assert "contains less than 2% of:" not in cleaned
    assert "*" not in cleaned

    phrases = normalizer.extract_phrases(raw)
    assert len(phrases) > 0
    assert any("salt" in p for p in phrases)


def test_allergen_detector_identifies_major_allergens():
    detector = AllergenDetector()

    # Peanut test
    res = detector.detect_allergens("Roasted peanuts, sea salt, peanut oil")
    assert res['contains_peanut'] is True
    assert res['contains_tree_nuts'] is False

    # Tree nut test
    res = detector.detect_allergens("Whole almonds, cashews, sunflower oil")
    assert res['contains_tree_nuts'] is True
    assert res['contains_peanut'] is False

    # Milk & Gluten test
    res = detector.detect_allergens("Enriched wheat flour, whey protein, cheddar cheese, butter")
    assert res['contains_milk'] is True
    assert res['contains_gluten'] is True

    # Shellfish test
    res = detector.detect_allergens("Shrimp paste, salt, spices")
    assert res['contains_shellfish'] is True


def test_concern_detector_flags_ultra_processed_additives():
    detector = ConcernDetector()

    # High fructose corn syrup + Artificial colors + Preservatives
    text = "Water, High Fructose Corn Syrup, Red 40, Sodium Benzoate, Partially Hydrogenated Palm Oil"
    concerns = detector.detect_concerns(text)

    assert concerns['added_sugar_indicator'] == 1
    assert concerns['artificial_color_indicator'] == 1
    assert concerns['preservative_indicator'] == 1
    assert concerns['hydrogenated_oil_indicator'] == 1
    assert concerns['high_concern_ingredient_count'] >= 4
    assert len(concerns['flagged_concerns_list']) >= 4
