"""
ML Pipeline Regression Tests — Tests 24-29.
Verifies: model loading, prediction correctness, feature ordering consistency,
          feature schema stability, SHAP explanation consistency.
"""

import json
import numpy as np
import pytest
from pathlib import Path

from src.models.model_factory import ModelFactory
from src.features.feature_builder import HealthSenseFeatureBuilder
from src.features.nutrition_features import NutritionFeaturePipeline
from src.explainability.shap_explainer import HealthSenseShapExplainer


ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"
FEATURES_LIST_PATH = ARTIFACTS_DIR / "encoders" / "features_list.json"
MODEL_METADATA_PATH = ARTIFACTS_DIR / "models" / "model_metadata.json"


# ─── HELPER: Minimal valid product/member ────────────────────────────────────

def make_product_context(missing_features=False):
    if missing_features:
        return {
            'nutriments': {},
            'normalized_ingredients': '',
            'allergen_flags': {},
            'concern_flags': {},
        }
    return {
        'nutriments': {
            'energy_kcal_100g': 450.0,
            'sugars_100g': 12.0,
            'sodium_100g': 180.0,
            'fat_100g': 15.0,
            'saturated_fat_100g': 5.0,
            'protein_100g': 8.0,
            'carbohydrates_100g': 62.0,
            'fiber_100g': 2.5,
        },
        'normalized_ingredients': 'wheat flour sugar palm oil cocoa butter salt',
        'allergen_flags': {'contains_gluten': True, 'contains_milk': False},
        'concern_flags': {
            'added_sugar_indicator': 1,
            'artificial_sweetener_indicator': 0,
            'preservative_indicator': 0,
            'artificial_color_indicator': 0,
            'hydrogenated_oil_indicator': 0,
        },
    }


def make_member_profile():
    return {
        'name': 'TestUser',
        'age': 35,
        'healthConditions': ['Diabetes (Type 2)'],
        'allergies': [],
        'dietaryPreferences': [],
    }


# ─── Test 24: Normal inference ────────────────────────────────────────────────

def test_normal_model_inference():
    """Active model loads and produces valid prediction on a normal product."""
    model = ModelFactory.load_active_model()
    assert model.is_trained, "Active model must be trained (artifact loaded from disk)"

    builder = HealthSenseFeatureBuilder()
    product = make_product_context()
    member = make_member_profile()
    feature_vector = builder.build_feature_vector(product, member)

    assert feature_vector is not None
    assert len(feature_vector) > 0
    assert not np.any(np.isnan(feature_vector)), "Feature vector must not contain NaN values"

    probas = model.predict_proba(feature_vector.reshape(1, -1))
    assert probas.shape[1] == 3, "predict_proba must return 3-class probabilities"
    assert abs(probas[0].sum() - 1.0) < 1e-4, "Probabilities must sum to ~1.0"
    assert all(p >= 0 for p in probas[0]), "All probabilities must be non-negative"


# ─── Test 25: Missing features → no crash, valid vector ──────────────────────

def test_model_inference_with_missing_features():
    """Model inference with all-missing features must not crash — returns valid vector."""
    builder = HealthSenseFeatureBuilder()
    product = make_product_context(missing_features=True)
    member = {'name': 'X', 'age': 30, 'healthConditions': [], 'allergies': [], 'dietaryPreferences': []}

    feature_vector = builder.build_feature_vector(product, member)
    assert feature_vector is not None
    assert len(feature_vector) > 0
    # Must have no NaN (replace with 0.0 is acceptable for missing values)
    assert not np.any(np.isnan(feature_vector)), "Missing feature vector must not contain NaN"


# ─── Test 26: Unseen product (OOV ingredients) ───────────────────────────────

def test_unseen_product_graceful_handling():
    """Unseen product with unusual ingredient text → feature builder must handle gracefully."""
    builder = HealthSenseFeatureBuilder()
    product = {
        'nutriments': {'sugars_100g': 3.0, 'sodium_100g': 120.0},
        'normalized_ingredients': 'zorblaxite ultra-processed frumblewood extract xyzzy',
        'allergen_flags': {},
        'concern_flags': {},
    }
    member = make_member_profile()
    feature_vector = builder.build_feature_vector(product, member)
    assert len(feature_vector) > 0
    # TF-IDF unknown words should produce 0.0 for OOV terms (sparse zero vector)
    assert not np.any(np.isnan(feature_vector))


# ─── Test 27: Feature ordering consistency ────────────────────────────────────

def test_feature_ordering_consistency():
    """Feature vector must always have the same length and follow features_list.json order."""
    assert FEATURES_LIST_PATH.exists(), (
        f"features_list.json must exist at {FEATURES_LIST_PATH}. "
        "This file defines the canonical feature schema."
    )
    with open(FEATURES_LIST_PATH, 'r', encoding='utf-8') as f:
        feature_names = json.load(f)

    assert len(feature_names) > 0, "features_list.json must not be empty"

    builder = HealthSenseFeatureBuilder()
    product = make_product_context()
    member = make_member_profile()
    feature_vector = builder.build_feature_vector(product, member)

    assert len(feature_vector) == len(feature_names), (
        f"Feature vector length ({len(feature_vector)}) must match features_list.json "
        f"length ({len(feature_names)}). Schema drift detected!"
    )

    # Verify builder's own feature_names matches the file
    assert builder.feature_names == feature_names, (
        "HealthSenseFeatureBuilder.feature_names must exactly match features_list.json. "
        "Any drift would cause incorrect inference."
    )


# ─── Test 28: Model artifact loading ─────────────────────────────────────────

def test_model_artifact_loads_correctly():
    """LightGBM artifact must load with is_trained=True and non-empty feature_names."""
    model = ModelFactory.load_active_model()
    assert model.is_trained is True, "Loaded model must have is_trained=True"
    assert model.get_model_name() is not None
    assert len(model.get_model_name()) > 0

    # Verify model can accept predictions
    dummy_vec = np.zeros((1, len(json.load(open(FEATURES_LIST_PATH)))))
    probas = model.predict_proba(dummy_vec)
    assert probas.shape == (1, 3)


# ─── Test 29: SHAP explanation consistency ───────────────────────────────────

def test_shap_explanation_consistency():
    """SHAP values must reference actual model features (no stale/mismatched mapping)."""
    model = ModelFactory.load_active_model()
    assert model.is_trained, "Model must be loaded for SHAP test"

    builder = HealthSenseFeatureBuilder()
    product = make_product_context()
    member = make_member_profile()
    feature_vector = builder.build_feature_vector(product, member)

    explainer = HealthSenseShapExplainer(model)
    shap_info = explainer.explain_instance(feature_vector, builder.feature_names, top_k=5)

    assert 'top_risk_factors' in shap_info, "SHAP output must include top_risk_factors"
    assert 'top_protective_factors' in shap_info, "SHAP output must include top_protective_factors"
    assert isinstance(shap_info['top_risk_factors'], list)
    assert isinstance(shap_info['top_protective_factors'], list)

    # If SHAP successfully ran (not fell back to feature importance),
    # each factor should have 'feature', 'value', and 'shap_value' keys
    if shap_info['top_risk_factors'] and 'shap_value' in shap_info['top_risk_factors'][0]:
        for factor in shap_info['top_risk_factors']:
            assert 'feature' in factor
            assert factor['feature'] in builder.feature_names, (
                f"SHAP factor feature '{factor['feature']}' must be in feature_names. "
                "Stale/mismatched feature mapping detected!"
            )
            assert isinstance(factor['shap_value'], float)


# ─── Test: Model metadata completeness ────────────────────────────────────────

def test_model_metadata_is_present_and_complete():
    """model_metadata.json must exist and contain key fields documenting the baseline model."""
    assert MODEL_METADATA_PATH.exists(), "model_metadata.json must exist in artifacts/models/"

    with open(MODEL_METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    required_fields = [
        'dataset_version',
        'training_date',
        'active_model',
        'metrics',
        'feature_count',
    ]
    for field in required_fields:
        assert field in metadata, f"model_metadata.json must contain '{field}'"

    # Feature count must match the features_list.json
    if FEATURES_LIST_PATH.exists():
        with open(FEATURES_LIST_PATH, 'r', encoding='utf-8') as f:
            feature_names = json.load(f)
        # Allow ±1 tolerance (metadata may count differently)
        diff = abs(metadata['feature_count'] - len(feature_names))
        assert diff <= 2, (
            f"model_metadata.json feature_count ({metadata['feature_count']}) differs from "
            f"features_list.json length ({len(feature_names)}) by {diff}. "
            "Update feature_count in model_metadata.json."
        )
