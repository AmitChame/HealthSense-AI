"""
Django REST API Views for HealthSense AI.
Integrates evidence-backed food quality grading, food category knowledge (Codex/FSSAI),
life-stage personalization, nutrient normalization, frequency intelligence, and ML explainability.
"""

import time
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    RecommendationRequestSerializer,
    RecommendationResponseSerializer
)
from src.ingredient_engine.normalizer import IngredientNormalizer
from src.ingredient_engine.allergen_detector import AllergenDetector
from src.ingredient_engine.concern_detector import ConcernDetector
from src.features.food_grader import HealthSenseFoodGrader
from src.features.nutrition_features import NutritionFeaturePipeline
from src.features.feature_builder import HealthSenseFeatureBuilder
from src.rules.rule_engine import HealthSenseRuleEngine
from src.explainability.reason_generator import HealthSenseReasonGenerator
from src.explainability.shap_explainer import HealthSenseShapExplainer
from src.models.model_factory import ModelFactory
from src.models.model_registry import ModelRegistry
from src.evidence.evidence_registry import EvidenceRegistry
from src.evidence.nutrient_normalizer import NutrientNormalizer
from src.evidence.category_engine import FoodCategoryEngine
from src.evidence.life_stage_engine import LifeStageEngine
from src.evidence.frequency_engine import FrequencyIntelligenceEngine

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    Health check endpoint reporting API status, active ML model, and registered models.
    GET /api/health/
    """

    def get(self, request):
        active_model = ModelFactory.load_active_model()
        model_name = active_model.get_model_name()
        is_trained = getattr(active_model, 'is_trained', False)

        return Response({
            'status': 'healthy',
            'service': 'HealthSense AI Recommendation Service',
            'version': '1.0.0',
            'phase': 'Phase 3 (Evidence-Backed)',
            'active_model': model_name,
            'is_model_trained': is_trained,
            'available_models': ModelRegistry.list_models(),
            'timestamp': int(time.time() * 1000)
        }, status=status.HTTP_200_OK)


class AnalyzeFoodView(APIView):
    """
    Core AI Recommendation Endpoint.
    POST /api/analyze/  and  POST /api/v1/recommend/
    """

    # In-memory cached singletons to avoid reloading from disk on every request
    _normalizer = None
    _allergen_detector = None
    _concern_detector = None
    _food_grader = None
    _nutrition_pipeline = None
    _feature_builder = None
    _rule_engine = None
    _reason_generator = None
    _model = None
    _shap_explainer = None
    _evidence_registry = None
    _category_engine = None

    @classmethod
    def get_engines(cls):
        if cls._normalizer is None:
            cls._normalizer = IngredientNormalizer()
            cls._allergen_detector = AllergenDetector()
            cls._concern_detector = ConcernDetector()
            cls._food_grader = HealthSenseFoodGrader()
            cls._nutrition_pipeline = NutritionFeaturePipeline()
            cls._feature_builder = HealthSenseFeatureBuilder()
            cls._rule_engine = HealthSenseRuleEngine()
            cls._reason_generator = HealthSenseReasonGenerator()
            cls._evidence_registry = EvidenceRegistry.get_instance()
            cls._category_engine = FoodCategoryEngine.get_instance()
            try:
                cls._model = ModelFactory.load_active_model()
                cls._shap_explainer = HealthSenseShapExplainer(cls._model)
            except Exception as e:
                logger.warning(f"Active model loading notice: {e}")
                cls._model = ModelFactory.create_model()
                cls._shap_explainer = None

        return (cls._normalizer, cls._allergen_detector, cls._concern_detector,
                cls._food_grader, cls._nutrition_pipeline, cls._feature_builder,
                cls._rule_engine, cls._reason_generator, cls._model, cls._shap_explainer,
                cls._evidence_registry, cls._category_engine)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        (self.normalizer, self.allergen_detector, self.concern_detector,
         self.food_grader, self.nutrition_pipeline, self.feature_builder,
         self.rule_engine, self.reason_generator, self.model, self.shap_explainer,
         self.evidence_registry, self.category_engine) = self.get_engines()

    def post(self, request):
        serializer = RecommendationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid request payload', 'details': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        prod = data['foodProduct']
        family_members = data['familyMembers']

        # 1. Ingredient Intelligence
        ingredients_text = prod.get('ingredients', '')
        allergen_tags = prod.get('allergens', [])
        categories = prod.get('categories', [])
        serving_size_text = prod.get('servingSize', '')
        product_name = prod.get('productName', '')

        normalized_ingredients = self.normalizer.normalize(ingredients_text)
        allergen_flags = self.allergen_detector.detect_allergens(ingredients_text, allergen_tags)
        detected_allergens = self.allergen_detector.get_detected_allergen_list(ingredients_text, allergen_tags)
        concern_flags = self.concern_detector.detect_concerns(ingredients_text)

        # 2. Nutrient Normalization & Serving Size Intelligence
        raw_nutriments = prod.get('nutriments', {})
        normalized_nutrition = NutrientNormalizer.normalize_nutrients(raw_nutriments, serving_size_text)
        per_100g_nutriments = normalized_nutrition['per_100g']

        # 3. Food Category Intelligence & Standards
        resolved_category = self.category_engine.resolve_category(
            categories_list=categories,
            product_name=product_name,
            ingredients_text=ingredients_text
        )
        category_key = resolved_category['key'] if resolved_category else None
        category_name = resolved_category['name'] if resolved_category else "General Packaged Food"

        product_context = {
            'nutriments': {
                'energy_kcal_100g': per_100g_nutriments.get('energy_kcal'),
                'sugars_100g': per_100g_nutriments.get('sugars'),
                'sodium_100g': per_100g_nutriments.get('sodium'),
                'fat_100g': per_100g_nutriments.get('fat'),
                'saturated_fat_100g': per_100g_nutriments.get('saturated_fat'),
                'protein_100g': per_100g_nutriments.get('protein'),
                'carbohydrates_100g': per_100g_nutriments.get('carbohydrates'),
                'fiber_100g': per_100g_nutriments.get('fiber')
            },
            'allergen_flags': allergen_flags,
            'detected_allergens': detected_allergens,
            'concern_flags': concern_flags,
            'normalized_ingredients': normalized_ingredients,
            'categories': categories,
            'explicit_child_warning': prod.get('explicitChildWarning')
        }

        composition_eval = self.category_engine.evaluate_composition_standard(category_key, product_context) if category_key else None

        # 4. Standalone HealthSense Food Quality Grade (A to E)
        grade_letter, quality_score, grade_breakdown = self.food_grader.grade_product(
            product_context['nutriments'],
            concern_flags,
            nova_group=prod.get('novaGroup'),
            nutriscore=prod.get('nutriScore'),
            category_key=category_key
        )

        # 5. Data Completeness & Assessment Confidence
        known_nutrients = sum(1 for v in product_context['nutriments'].values() if v is not None and not (isinstance(v, float) and np.isnan(v)))
        nutr_coverage_pct = round((known_nutrients / max(1, len(product_context['nutriments']))) * 100, 1)
        has_ingredients = bool(ingredients_text and len(ingredients_text.strip()) > 5)

        if nutr_coverage_pct >= 75 and has_ingredients:
            overall_confidence_label = "HIGH"
            confidence_numeric = 0.95
        elif nutr_coverage_pct >= 40:
            overall_confidence_label = "MEDIUM"
            confidence_numeric = 0.75
        else:
            overall_confidence_label = "LOW"
            confidence_numeric = 0.50

        # 6. General Product Frequency Intelligence
        general_freq_bundle = FrequencyIntelligenceEngine.determine_frequency(
            food_grade=grade_letter,
            product_nutrients=per_100g_nutriments,
            concern_flags=concern_flags,
            category_key=category_key,
            life_stage="ADULT",
            has_hard_block=False,
            risk_level="LOW",
            data_confidence=overall_confidence_label
        )
        general_frequency = general_freq_bundle['frequency']

        # 7. Process Each Family Member Profile with Life-Stage Intelligence
        recommendations_list: List[Dict[str, Any]] = []
        any_avoid = False
        any_caution = False
        consulted_evidence_sources = set()

        for member in family_members:
            m_id = member.get('id')
            m_name = member.get('name', 'Member')
            m_age = member.get('age', 30)
            m_conditions = member.get('healthConditions', [])
            m_allergies = member.get('allergies', [])
            m_diets = member.get('dietaryPreferences', [])

            # Life-Stage Personalization
            life_stage_eval = LifeStageEngine.evaluate_life_stage_suitability(
                age=m_age,
                product_nutrients=per_100g_nutriments,
                concern_flags=concern_flags,
                category_key=category_key
            )
            life_stage_key = life_stage_eval['life_stage']
            consulted_evidence_sources.add(life_stage_eval['evidence_source'])

            # Summary health string
            summary_parts = []
            summary_parts.append(life_stage_eval['life_stage_name'])
            if m_conditions:
                summary_parts.append(", ".join(m_conditions))
            if m_allergies:
                summary_parts.append("Allergic to " + ", ".join(m_allergies))
            if m_diets:
                summary_parts.append(", ".join(m_diets))
            health_summary_str = " | ".join(summary_parts)

            # Deterministic Rule Engine Evaluation
            triggered_rules = self.rule_engine.evaluate(product_context, member)
            has_hard_block = self.rule_engine.has_hard_block(triggered_rules)

            for r in triggered_rules:
                if getattr(r, 'evidence_source', None):
                    consulted_evidence_sources.add(r.evidence_source)

            # Hybrid Decision Logic
            feature_vector = self.feature_builder.build_feature_vector(product_context, member)

            if has_hard_block:
                final_cat = "AVOID"
                final_risk_level = "HIGH"
                final_risk_score = 100.0
                confidence = 1.0
                member_frequency = "AVOID"
            else:
                risk_score_calc = 15.0 # baseline low risk

                # Add rule-based risk impacts
                for r in triggered_rules:
                    risk_score_calc += r.risk_score_impact

                # Add life-stage restriction risk
                if life_stage_eval['is_age_restricted']:
                    risk_score_calc += 50.0

                # ML model inference if trained
                if getattr(self.model, 'is_trained', False):
                    try:
                        raw_vec = feature_vector.reshape(1, -1)
                        probas = self.model.predict_proba(raw_vec)[0]
                        avoid_prob = probas[2] if len(probas) > 2 else 0.0
                        caution_prob = probas[1] if len(probas) > 1 else 0.0
                        ml_risk = (avoid_prob * 80.0) + (caution_prob * 40.0)
                        risk_score_calc = max(risk_score_calc, ml_risk)
                        confidence = float(max(probas))
                    except Exception as e:
                        logger.error(f"ML Inference failed: {str(e)}")
                        confidence = confidence_numeric
                else:
                    confidence = confidence_numeric

                final_risk_score = min(100.0, max(0.0, risk_score_calc))

                if final_risk_score >= 60.0 or any(r.recommendation == 'AVOID' for r in triggered_rules) or life_stage_eval['is_age_restricted']:
                    final_cat = "AVOID"
                    final_risk_level = "HIGH"
                elif final_risk_score >= 30.0 or any(r.recommendation == 'CAUTION' for r in triggered_rules) or len(life_stage_eval['cautions']) > 0:
                    final_cat = "CAUTION"
                    final_risk_level = "MODERATE"
                else:
                    final_cat = "RECOMMENDED"
                    final_risk_level = "LOW"

                # Member Frequency
                member_freq_bundle = FrequencyIntelligenceEngine.determine_frequency(
                    food_grade=grade_letter,
                    product_nutrients=per_100g_nutriments,
                    concern_flags=concern_flags,
                    category_key=category_key,
                    life_stage=life_stage_key,
                    has_hard_block=has_hard_block,
                    risk_level=final_risk_level,
                    data_confidence=overall_confidence_label
                )
                member_frequency = member_freq_bundle['frequency']

            if final_cat == "AVOID":
                any_avoid = True
            elif final_cat == "CAUTION":
                any_caution = True

            # Generate Explanations & Factor Breakdown
            shap_info = {}
            if self.shap_explainer and getattr(self.model, 'is_trained', False):
                try:
                    shap_info = self.shap_explainer.explain_instance(
                        feature_vector, self.feature_builder.feature_names
                    )
                except Exception as e:
                    logger.warning(f"SHAP explanation failed: {str(e)}")

            explanation_bundle = self.reason_generator.generate_explanation(
                member_name=m_name,
                recommendation=final_cat,
                triggered_rules=triggered_rules,
                ingredient_concerns=concern_flags.get('flagged_concerns_list', []),
                allergen_conflicts=detected_allergens,
                shap_info=shap_info
            )

            # Append life-stage cautions to health factors
            health_factors_list = list(explanation_bundle['health_factors'])
            for caution in life_stage_eval['cautions']:
                health_factors_list.append({
                    'name': f"Life Stage ({life_stage_eval['life_stage_name']})",
                    'impact': "MODERATE",
                    'description': caution,
                    'isAllergen': False
                })

            warnings_list = [r.explanation for r in triggered_rules if r.severity in ['CRITICAL', 'HIGH']]
            if life_stage_eval['is_age_restricted']:
                warnings_list.extend(life_stage_eval['cautions'])

            recommendations_list.append({
                'familyMemberId': m_id,
                'familyMemberName': m_name,
                'familyMemberAge': m_age,
                'lifeStage': life_stage_key,
                'healthSummary': health_summary_str,
                'category': final_cat, # RECOMMENDED, CAUTION, AVOID
                'riskLevel': final_risk_level,
                'riskScore': round(final_risk_score, 1),
                'summaryReason': explanation_bundle['summary_reason'],
                'healthFactors': health_factors_list,
                'warnings': warnings_list,
                'foodGrade': grade_letter,
                'ingredientConcerns': concern_flags.get('flagged_concerns_list', []),
                'modelName': self.model.get_model_name(),
                'confidence': round(confidence, 2),
                'assessmentConfidence': overall_confidence_label,
                'frequencyRecommendation': member_frequency
            })

        # Overall verdict
        if any_avoid:
            overall_verdict = f"Grade {grade_letter} — High Risk for some family members. Review member warnings before consumption."
        elif any_caution:
            overall_verdict = f"Grade {grade_letter} — Consume with Caution. Portion moderation recommended."
        else:
            overall_verdict = f"Grade {grade_letter} — Recommended for all evaluated family members."

        response_payload = {
            'barcode': prod.get('barcode', ''),
            'productName': prod.get('productName', ''),
            'recommendations': recommendations_list,
            'overallVerdict': overall_verdict,
            'analyzedAt': int(time.time() * 1000),
            'disclaimer': "HealthSense AI provides educational dietary decision support and is not a medical diagnosis system.",
            'foodGrade': grade_letter,
            'foodQualityScore': quality_score,
            'foodCategory': {
                'key': category_key,
                'name': category_name
            },
            'compositionStandard': composition_eval,
            'servingInfo': normalized_nutrition['serving_size'],
            'referenceContributions': normalized_nutrition['reference_contributions'],
            'activeModel': self.model.get_model_name(),
            'source': 'REMOTE_BACKEND',
            'assessmentConfidence': overall_confidence_label,
            'confidenceBreakdown': {
                'dataConfidence': overall_confidence_label,
                'modelConfidence': "HIGH" if getattr(self.model, 'is_trained', False) else "LOW",
                'evidenceConfidence': "HIGH",
                'safetyCertainty': "ABSOLUTE" if any_avoid else "HIGH"
            },
            'frequencyRecommendation': general_frequency,
            'dataCompleteness': {
                'nutrientCoveragePct': nutr_coverage_pct,
                'hasIngredients': has_ingredients,
                'status': "Complete" if nutr_coverage_pct >= 75 else "Partial"
            },
            'evidenceSources': list(consulted_evidence_sources)
        }

        return Response(response_payload, status=status.HTTP_200_OK)
