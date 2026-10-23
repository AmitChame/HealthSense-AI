"""
Comprehensive Model Training Pipeline for HealthSense AI.
Constructs multi-member training scenarios from real product data, fits feature pipelines,
trains all 4 candidate models, benchmarks performance, and persists artifacts.
"""

from typing import List, Dict, Any, Tuple, Optional
import os
import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

from ..ingredient_engine.tfidf_extractor import IngredientTfidfExtractor
from ..features.nutrition_features import NutritionFeaturePipeline
from ..models.model_registry import ModelRegistry
from ..models.base_model import BaseHealthSenseModel
from ..rules.config_manager import HealthSenseConfigManager
from .evaluator import ModelEvaluator
from .model_comparator import ModelComparator

logger = logging.getLogger(__name__)


class ModelTrainingPipeline:
    """
    End-to-end training and benchmark coordinator.
    """

    PROFILE_SCENARIOS = [
        {'name': 'General_Healthy', 'diabetes': 0, 'hypertension': 0, 'cholesterol': 0, 'peanut_allergy': 0, 'milk_allergy': 0, 'gluten_allergy': 0},
        {'name': 'Diabetic_Patient', 'diabetes': 1, 'hypertension': 0, 'cholesterol': 0, 'peanut_allergy': 0, 'milk_allergy': 0, 'gluten_allergy': 0},
        {'name': 'Hypertensive_Patient', 'diabetes': 0, 'hypertension': 1, 'cholesterol': 0, 'peanut_allergy': 0, 'milk_allergy': 0, 'gluten_allergy': 0},
        {'name': 'High_Cholesterol_Patient', 'diabetes': 0, 'hypertension': 0, 'cholesterol': 1, 'peanut_allergy': 0, 'milk_allergy': 0, 'gluten_allergy': 0},
        {'name': 'Peanut_Allergic', 'diabetes': 0, 'hypertension': 0, 'cholesterol': 0, 'peanut_allergy': 1, 'milk_allergy': 0, 'gluten_allergy': 0},
        {'name': 'Dairy_Allergic', 'diabetes': 0, 'hypertension': 0, 'cholesterol': 0, 'peanut_allergy': 0, 'milk_allergy': 1, 'gluten_allergy': 0},
        {'name': 'Celiac_Gluten_Allergic', 'diabetes': 0, 'hypertension': 0, 'cholesterol': 0, 'peanut_allergy': 0, 'milk_allergy': 0, 'gluten_allergy': 1},
        {'name': 'Diabetic_Hypertensive_Senior', 'diabetes': 1, 'hypertension': 1, 'cholesterol': 0, 'peanut_allergy': 0, 'milk_allergy': 0, 'gluten_allergy': 0},
    ]

    def __init__(self, project_root: Optional[str] = None):
        if project_root is None:
            self.root = Path(__file__).resolve().parent.parent.parent
        else:
            self.root = Path(project_root)

        self.artifacts_dir = self.root / "artifacts"
        self.models_dir = self.artifacts_dir / "models"
        self.scalers_dir = self.artifacts_dir / "scalers"
        self.encoders_dir = self.artifacts_dir / "encoders"

        for d in [self.models_dir, self.scalers_dir, self.encoders_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.config_manager = HealthSenseConfigManager(str(self.root / "config"))
        self.nutrition_pipeline = NutritionFeaturePipeline()
        self.tfidf_extractor = IngredientTfidfExtractor(max_features=25)
        self.scaler = StandardScaler()
        self.evaluator = ModelEvaluator()
        self.comparator = ModelComparator(artifacts_dir=str(self.artifacts_dir))
        self.feature_names = []

    def prepare_data(self, df_products: pd.DataFrame, is_training: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extracts features and generates ground-truth labels for a given set of products.
        """
        rows_X = []
        labels_y = []

        # 1. TF-IDF Features
        ingredients_list = df_products['normalized_ingredients'].fillna('').tolist()
        if is_training:
            tfidf_features = self.tfidf_extractor.fit_transform(ingredients_list)
            self.tfidf_extractor.save(str(self.encoders_dir / "ingredient_tfidf.joblib"))
        else:
            tfidf_features = self.tfidf_extractor.transform(ingredients_list)

        tfidf_cols = self.tfidf_extractor.get_feature_names()

        # 2. Nutrition Features
        nutr_rows = []
        for _, prod in df_products.iterrows():
            nmap = {
                'energy_kcal_100g': prod.get('energy_kcal_100g'),
                'sugars_100g': prod.get('sugars_100g'),
                'sodium_100g': prod.get('sodium_100g'),
                'fat_100g': prod.get('fat_100g'),
                'saturated_fat_100g': prod.get('saturated_fat_100g'),
                'carbohydrates_100g': prod.get('carbohydrates_100g'),
                'protein_100g': prod.get('protein_100g'),
                'fiber_100g': prod.get('fiber_100g')
            }
            nfeat = self.nutrition_pipeline.extract_features(nmap)
            nutr_rows.append(nfeat)

        df_nutr = pd.DataFrame(nutr_rows).fillna(0.0)
        nutr_cols = list(df_nutr.columns)

        if is_training:
            nutr_scaled = self.scaler.fit_transform(df_nutr.values)
            joblib.dump(self.scaler, str(self.scalers_dir / "nutrition_scaler.joblib"))
        else:
            nutr_scaled = self.scaler.transform(df_nutr.values)

        # 3. Scenario Expansion & Labeling
        profile_cols = ['user_diabetes', 'user_hypertension', 'user_cholesterol', 'user_peanut_allergy', 'user_milk_allergy', 'user_gluten_allergy']
        concern_cols = ['added_sugar_indicator', 'artificial_sweetener_indicator', 'preservative_indicator', 'artificial_color_indicator', 'hydrogenated_oil_indicator']

        if is_training:
            self.feature_names = nutr_cols + list(tfidf_cols) + profile_cols + concern_cols
            with open(self.encoders_dir / "features_list.json", 'w', encoding='utf-8') as f:
                json.dump(self.feature_names, f, indent=2)

        # Load thresholds from config manager
        t_diabetes = self.config_manager.get_health_condition_rule('diabetes_high_sugar')
        t_hypertension = self.config_manager.get_health_condition_rule('hypertension_high_sodium')
        t_cholesterol = self.config_manager.get_health_condition_rule('cholesterol_sat_fat')

        # General Health Rules
        gen_rules = self.config_manager.rules_config.get('general_health_rules', {})
        t_gen_sugar = gen_rules.get('high_sugar', {}).get('threshold_caution', 20.0)
        t_gen_sodium = gen_rules.get('high_sodium', {}).get('threshold_caution', 800.0)

        for i, (_, prod) in enumerate(df_products.iterrows()):
            p_nutr = nutr_scaled[i]
            p_tfidf = tfidf_features[i]
            p_concerns = [prod.get(c, 0) for c in concern_cols]

            for scenario in self.PROFILE_SCENARIOS:
                user_vec = [
                    scenario['diabetes'], scenario['hypertension'], scenario['cholesterol'],
                    scenario['peanut_allergy'], scenario['milk_allergy'], scenario['gluten_allergy']
                ]

                obs = np.concatenate([p_nutr, p_tfidf, user_vec, p_concerns])
                rows_X.append(obs)

                # Label generation (Logic centralized via config thresholds)
                # 0 = RECOMMENDED, 1 = CAUTION, 2 = AVOID
                label = 0
                # Allergen checks
                if scenario['peanut_allergy'] and prod.get('contains_peanut', False): label = 2
                elif scenario['milk_allergy'] and prod.get('contains_milk', False): label = 2
                elif scenario['gluten_allergy'] and prod.get('contains_gluten', False): label = 2
                # Diabetes
                elif scenario['diabetes']:
                    val = prod.get('sugars_100g', 0)
                    if val >= t_diabetes.get('threshold_avoid', 12.0): label = 2
                    elif val >= t_diabetes.get('threshold_caution', 5.0): label = max(label, 1)
                # Hypertension
                elif scenario['hypertension']:
                    val = prod.get('sodium_100g', 0)
                    if val >= t_hypertension.get('threshold_avoid', 400.0): label = 2
                    elif val >= t_hypertension.get('threshold_caution', 250.0): label = max(label, 1)
                # Cholesterol
                elif scenario['cholesterol']:
                    val = prod.get('saturated_fat_100g', 0)
                    if val >= t_cholesterol.get('threshold_avoid', 4.0): label = 2
                    elif val >= t_cholesterol.get('threshold_caution', 2.0): label = max(label, 1)

                # General health checks (apply to everyone if label still 0)
                if label == 0:
                    if prod.get('sugars_100g', 0) >= t_gen_sugar or \
                       prod.get('sodium_100g', 0) >= t_gen_sodium or \
                       prod.get('hydrogenated_oil_indicator', 0) == 1:
                        label = 1

                labels_y.append(label)

        return np.array(rows_X, dtype=np.float32), np.array(labels_y, dtype=np.int32)

    def run_training_and_comparison(self, df_products: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """
        Executes full training pipeline with product-level split to avoid leakage.
        """
        print(f"[Training Pipeline] Products found: {len(df_products)}. Splitting at Product level...")

        # Product-level split
        barcodes = df_products['barcode'].unique()
        train_bc, test_barcodes = train_test_split(barcodes, test_size=0.20, random_state=42)

        df_train = df_products[df_products['barcode'].isin(train_bc)]
        df_test = df_products[df_products['barcode'].isin(test_barcodes)]

        print(f"  --> Train products: {len(df_train)}, Test products: {len(df_test)}")

        X_train, y_train = self.prepare_data(df_train, is_training=True)
        X_test, y_test = self.prepare_data(df_test, is_training=False)

        print(f"  --> Observations: Train={len(X_train)}, Test={len(X_test)}")

        all_models = ModelRegistry.list_models()
        evaluation_results: List[Dict[str, Any]] = []

        for model_name in all_models:
            print(f"  --> Training: {model_name}...")
            model_cls = ModelRegistry.get(model_name)
            model_inst: BaseHealthSenseModel = model_cls()

            model_inst.fit(X_train, y_train, feature_names=self.feature_names)
            artifact_file = self.models_dir / f"{model_name}.joblib"
            model_inst.save(str(artifact_file))

            eval_metrics = self.evaluator.evaluate_model(model_inst, X_test, y_test)
            evaluation_results.append(eval_metrics)
            print(f"      F1-Macro: {eval_metrics['f1_macro']:.4f}, Avoid Recall: {eval_metrics['per_class']['AVOID']['recall']:.4f}")

        best_result, df_comparison = self.comparator.compare_and_select(evaluation_results)

        # Copy best model
        best_name = best_result['model_name']
        best_artifact_src = self.models_dir / f"{best_name}.joblib"
        best_dir = self.models_dir / "best_model"
        best_dir.mkdir(parents=True, exist_ok=True)
        best_artifact_dst = best_dir / "model.joblib"

        # Using joblib load/save for 'copy' to ensure compatibility
        model_payload = joblib.load(str(best_artifact_src))
        joblib.dump(model_payload, str(best_artifact_dst))

        print(f"[Training Pipeline] Winner: '{best_name}' with F1-Macro={best_result['f1_macro']:.4f}")
        return best_result, df_comparison
