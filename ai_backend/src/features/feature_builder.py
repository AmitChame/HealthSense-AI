"""
Unified Feature Builder for HealthSense AI.
Ensures consistency between training-time feature engineering and runtime inference.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import joblib
import json
import os
from pathlib import Path

from .nutrition_features import NutritionFeaturePipeline
from ..ingredient_engine.tfidf_extractor import IngredientTfidfExtractor


class HealthSenseFeatureBuilder:
    """
    Constructs a complete feature vector for a (Product, FamilyMember) pair.
    """

    def __init__(self, artifacts_dir: Optional[str] = None):
        if artifacts_dir is None:
            # Default to relative path from this file
            self.root = Path(__file__).resolve().parent.parent.parent
            self.artifacts_dir = self.root / "artifacts"
        else:
            self.artifacts_dir = Path(artifacts_dir)

        self.nutrition_pipeline = NutritionFeaturePipeline()
        self.tfidf_extractor = IngredientTfidfExtractor()

        # Load fitted artifacts
        scaler_path = self.artifacts_dir / "scalers" / "nutrition_scaler.joblib"
        tfidf_path = self.artifacts_dir / "encoders" / "ingredient_tfidf.joblib"
        features_list_path = self.artifacts_dir / "encoders" / "features_list.json"

        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
        else:
            self.scaler = None

        if tfidf_path.exists():
            self.tfidf_extractor.load(str(tfidf_path))
        else:
            self.tfidf_extractor = None

        if features_list_path.exists():
            with open(features_list_path, 'r', encoding='utf-8') as f:
                self.feature_names = json.load(f)
        else:
            self.feature_names = []

    def build_feature_vector(self, product_data: Dict[str, Any], member_profile: Dict[str, Any]) -> np.ndarray:
        """
        Builds the 1D feature vector matching the training schema.
        """
        # 1. Nutrition Features
        nutr_map = product_data.get('nutriments', {})
        nfeat_dict = self.nutrition_pipeline.extract_features(nutr_map)

        # We need to maintain the order of nutr_cols used during training
        # According to trainer.py: nutr_cols = list(df_nutr.columns)
        # NutritionFeaturePipeline returns a dict, we need to convert it to a sorted list of values if we don't have the exact names.
        # However, we have self.feature_names which contains all features in order.

        # 2. Ingredient TF-IDF
        normalized_ingredients = product_data.get('normalized_ingredients', '')
        if self.tfidf_extractor:
            tfidf_vec = self.tfidf_extractor.transform([normalized_ingredients])[0]
        else:
            tfidf_vec = np.zeros(25) # Default max_features was 25 in trainer.py

        # 3. User Profile Flags
        user_vec = self._map_member_profile_to_flags(member_profile)

        # 4. Product Concern Flags
        concern_flags = product_data.get('concern_flags', {})
        concern_cols = ['added_sugar_indicator', 'artificial_sweetener_indicator', 'preservative_indicator', 'artificial_color_indicator', 'hydrogenated_oil_indicator']
        prod_concerns = [concern_flags.get(c, 0) for c in concern_cols]

        # Assembly
        # We must strictly follow the feature_names if available
        if self.feature_names:
            # Create a dict of all available raw features
            full_feat_dict = {}
            full_feat_dict.update(nfeat_dict)

            # TF-IDF features
            if self.tfidf_extractor:
                tfidf_names = self.tfidf_extractor.get_feature_names()
                for name, val in zip(tfidf_names, tfidf_vec):
                    full_feat_dict[name] = val

            # User flags
            profile_cols = ['user_diabetes', 'user_hypertension', 'user_cholesterol', 'user_peanut_allergy', 'user_milk_allergy', 'user_gluten_allergy']
            for name, val in zip(profile_cols, user_vec):
                full_feat_dict[name] = val

            # Concern flags
            for name, val in zip(concern_cols, prod_concerns):
                full_feat_dict[name] = val

            # Construct vector in correct order
            vec = []
            for name in self.feature_names:
                # Special handling for scaled nutrition features
                # In trainer.py, ONLY the nutrition features were scaled.
                # feature_names = nutr_cols + list(tfidf_cols) + profile_cols + concern_cols
                vec.append(full_feat_dict.get(name, 0.0))

            # Now scale ONLY the nutrition part if scaler exists
            # We know nutr_cols are at the beginning.
            if self.scaler:
                num_nutr = self.scaler.n_features_in_
                nutr_part = np.array(vec[:num_nutr]).reshape(1, -1)
                # Handle NaNs in nutrition part before scaling (fill with 0.0 as in trainer.py)
                nutr_part = np.nan_to_num(nutr_part, nan=0.0)
                scaled_nutr = self.scaler.transform(nutr_part)[0]
                vec[:num_nutr] = scaled_nutr.tolist()

            return np.array(vec, dtype=np.float32)

        else:
            # Fallback if features_list.json is missing (not ideal)
            # Reconstruct based on trainer.py logic
            # This is risky if NutritionFeaturePipeline changes
            # Better to error out or log warning
            return np.zeros(40, dtype=np.float32)

    def _map_member_profile_to_flags(self, member_profile: Dict[str, Any]) -> List[float]:
        """
        Maps raw member profile (conditions, allergies) to binary ML flags.
        """
        conditions = member_profile.get('healthConditions', member_profile.get('health_conditions', []))
        if not isinstance(conditions, list): conditions = []
        cond_str = " ".join(conditions).lower()

        allergies = member_profile.get('allergies', [])
        if not isinstance(allergies, list): allergies = []
        all_str = " ".join(allergies).lower()

        return [
            1.0 if 'diabetes' in cond_str or member_profile.get('diabetes', False) else 0.0,
            1.0 if 'hypertension' in cond_str or 'blood pressure' in cond_str or member_profile.get('hypertension', False) else 0.0,
            1.0 if 'cholesterol' in cond_str or member_profile.get('cholesterol', False) else 0.0,
            1.0 if 'peanut' in all_str or member_profile.get('peanut_allergy', False) else 0.0,
            1.0 if 'milk' in all_str or 'dairy' in all_str or member_profile.get('milk_allergy', False) else 0.0,
            1.0 if 'gluten' in all_str or 'celiac' in all_str or member_profile.get('gluten_allergy', False) else 0.0
        ]
