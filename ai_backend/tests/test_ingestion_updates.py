import pytest
import numpy as np
from src.data.dataset_builder import UnifiedDatasetBuilder
from src.ingredient_engine.concern_detector import ConcernDetector

def test_energy_kj_to_kcal_conversion():
    builder = UnifiedDatasetBuilder()

    # 1. kcal available -> Use kcal
    raw_1 = {
        'nutriments': {
            'energy-kcal_100g': 200,
            'energy-kj_100g': 1000
        }
    }
    rec_1 = builder.process_product_record(raw_1)
    assert rec_1['energy_kcal_100g'] == 200.0

    # 2. kcal missing, kj available -> Convert
    raw_2 = {
        'nutriments': {
            'energy-kj_100g': 418.4
        }
    }
    rec_2 = builder.process_product_record(raw_2)
    assert pytest.approx(rec_2['energy_kcal_100g'], 0.1) == 100.0

    # 3. Both missing
    raw_3 = {
        'nutriments': {}
    }
    rec_3 = builder.process_product_record(raw_3)
    assert np.isnan(rec_3['energy_kcal_100g'])

def test_additive_tags_detection():
    detector = ConcernDetector()

    # 1. Detect from tags (E951 = Aspartame)
    res_1 = detector.detect_concerns("", additives_tags=["en:e951"])
    assert res_1['artificial_sweetener_indicator'] == 1
    assert any("Sweetener" in x for x in res_1['flagged_concerns_list'])

    # 2. Detect from text (Preservative)
    res_2 = detector.detect_concerns("Contains sodium benzoate", additives_tags=[])
    assert res_2['preservative_indicator'] == 1

    # 3. Combined + No double counting
    # "e202" is Potassium Sorbate
    res_3 = detector.detect_concerns("Potassium sorbate", additives_tags=["en:e202"])
    assert res_3['preservative_indicator'] == 1
    # Check that high_concern_ingredient_count is only 1
    assert res_3['high_concern_ingredient_count'] == 1

def test_energy_kcal_fallback_priority():
    builder = UnifiedDatasetBuilder()

    # Should ignore energy_100g if kcal and kj are missing to avoid ambiguity
    raw = {
        'nutriments': {
            'energy_100g': 500 # Could be kcal or kj, we don't know
        }
    }
    rec = builder.process_product_record(raw)
    assert np.isnan(rec['energy_kcal_100g'])
