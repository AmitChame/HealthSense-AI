"""
Unit tests for Pluggable ML Model Architecture (LR, RF, XGBoost, LightGBM).
"""

import pytest
import numpy as np
import os
import tempfile
from src.models.model_registry import ModelRegistry
from src.models.model_factory import ModelFactory
from src.models.base_model import BaseHealthSenseModel


@pytest.fixture
def sample_data():
    np.random.seed(42)
    X = np.random.randn(100, 10).astype(np.float32)
    y = np.random.choice([0, 1, 2], size=100)
    feature_names = [f"feat_{i}" for i in range(10)]
    return X, y, feature_names


@pytest.mark.parametrize("model_name", ["logistic_regression", "random_forest", "xgboost", "lightgbm"])
def test_model_lifecycle(model_name, sample_data):
    X, y, feature_names = sample_data

    model_cls = ModelRegistry.get(model_name)
    model: BaseHealthSenseModel = model_cls()

    # Fit
    model.fit(X, y, feature_names=feature_names)
    assert model.is_trained is True

    # Predict
    preds = model.predict(X[:5])
    assert len(preds) == 5
    assert all(p in [0, 1, 2] for p in preds)

    # Predict Proba
    probas = model.predict_proba(X[:5])
    assert probas.shape == (5, 3)
    assert np.allclose(np.sum(probas, axis=1), 1.0, atol=1e-4)

    # Feature importance
    importances = model.get_feature_importance()
    assert len(importances) == 10

    # Save and load
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, f"{model_name}.joblib")
        model.save(save_path)
        assert os.path.exists(save_path)

        loaded_model: BaseHealthSenseModel = model_cls()
        loaded_model.load(save_path)
        assert loaded_model.is_trained is True
        loaded_preds = loaded_model.predict(X[:5])
        np.testing.assert_array_equal(preds, loaded_preds)


def test_model_factory_creates_active_model():
    model = ModelFactory.create_model("xgboost")
    assert model.get_model_name() == "xgboost"

    model_rf = ModelFactory.create_model("random_forest")
    assert model_rf.get_model_name() == "random_forest"
