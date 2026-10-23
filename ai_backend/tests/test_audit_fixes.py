import pytest
import numpy as np
from src.data.dataset_builder import UnifiedDatasetBuilder
from src.rules.rule_engine import HealthSenseRuleEngine
from src.evaluation.trainer import ModelTrainingPipeline
import pandas as pd

def test_sodium_normalization():
    builder = UnifiedDatasetBuilder()

    # 1. Sodium = 500 mg (provided as 0.5g in OFF)
    raw_1 = {
        'code': '1',
        'nutriments': {'sodium_100g': 0.5}
    }
    rec_1 = builder.process_product_record(raw_1)
    assert rec_1['sodium_100g'] == 500.0

    # 2. Sodium missing, Salt = 1g
    raw_2 = {
        'code': '2',
        'nutriments': {'salt_100g': 1.0}
    }
    rec_2 = builder.process_product_record(raw_2)
    assert rec_2['sodium_100g'] == 400.0

    # 3. Sodium = 0
    raw_3 = {
        'code': '3',
        'nutriments': {'sodium_100g': 0.0}
    }
    rec_3 = builder.process_product_record(raw_3)
    assert rec_3['sodium_100g'] == 0.0

    # 4. Missing both
    raw_4 = {
        'code': '4',
        'nutriments': {}
    }
    rec_4 = builder.process_product_record(raw_4)
    assert np.isnan(rec_4['sodium_100g'])

def test_recommendation_terminology():
    engine = HealthSenseRuleEngine()

    product_data = {
        'nutriments': {'sugars_100g': 1.0},
        'allergen_flags': {},
        'concern_flags': {}
    }
    member = {'name': 'Test', 'healthConditions': []}

    results = engine.evaluate(product_data, member)
    assert len(results) == 0

def test_general_health_thresholds_loading():
    engine = HealthSenseRuleEngine()

    # Test High Sodium General Rule (> 800mg)
    product_data = {
        'nutriments': {'sodium_100g': 900.0}, # mg
        'allergen_flags': {},
        'concern_flags': {}
    }
    member = {'name': 'Healthy User', 'healthConditions': []}

    results = engine.evaluate(product_data, member)
    assert any(r.rule_id == 'RULE_GEN_HIGH_SODIUM' for r in results)
    assert any(r.recommendation == 'CAUTION' for r in results)

def test_trainer_labels_consistency():
    pipeline = ModelTrainingPipeline()

    # Create a product that triggers high sugar caution (> 20g)
    df = pd.DataFrame([{
        'barcode': '123',
        'product_name': 'Sweet stuff',
        'normalized_ingredients': 'sugar',
        'sugars_100g': 25.0,
        'sodium_100g': 100.0,
        'energy_kcal_100g': 200.0,
        'contains_peanut': False,
        'contains_milk': False,
        'contains_gluten': False
    }])

    # Fit TF-IDF before preparing data
    pipeline.tfidf_extractor.fit(['sugar'])
    pipeline.scaler.fit(np.zeros((1, 16))) # Nutrition pipeline produces 16 features

    X, y = pipeline.prepare_data(df, is_training=False)
    # y should contain at least level 1 (CAUTION) for all scenarios since it's a general health rule
    # but could be level 2 (AVOID) for diabetics
    assert np.all(y >= 1)
    assert y[1] == 2 # Diabetic patient should be AVOID (sugar 25 > 12)
