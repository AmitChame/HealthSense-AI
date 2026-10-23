"""
HealthSense AI V2 — Evidence-Informed Recommendation View
=========================================================
Endpoint: POST /api/v2/recommend/
"""

import time
import logging
from typing import Dict, Any, List
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RecommendationRequestSerializer
from src.evidence.v2_engines import (
    V2DataCompletenessEngine,
    V2FoodProfileEngine,
    V2NutrientFindingEngine,
    V2PersonalContextEngine,
    V2GuidanceEngine
)
from src.ingredient_engine.normalizer import IngredientNormalizer
from src.ingredient_engine.allergen_detector import AllergenDetector
from src.ingredient_engine.concern_detector import ConcernDetector
from src.evidence.category_engine import FoodCategoryEngine
from src.evidence.evidence_registry import EvidenceRegistry
from src.models.model_factory import ModelFactory

logger = logging.getLogger(__name__)


class AnalyzeFoodViewV2(APIView):
    """
    V2 Evidence-Informed Food Analysis Endpoint.
    Does not produce medical diagnoses, prescriptions, or universal safety claims.
    """

    _normalizer = None
    _allergen_detector = None
    _concern_detector = None
    _category_engine = None
    _evidence_registry = None

    @classmethod
    def get_engines(cls):
        if cls._normalizer is None:
            cls._normalizer = IngredientNormalizer()
            cls._allergen_detector = AllergenDetector()
            cls._concern_detector = ConcernDetector()
            cls._category_engine = FoodCategoryEngine.get_instance()
            cls._evidence_registry = EvidenceRegistry.get_instance()
        return (cls._normalizer, cls._allergen_detector, cls._concern_detector,
                cls._category_engine, cls._evidence_registry)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        (self.normalizer, self.allergen_detector, self.concern_detector,
         self.category_engine, self.evidence_registry) = self.get_engines()

    def post(self, request):
        serializer = RecommendationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid request payload', 'details': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        prod = data['foodProduct']
        family_members = data['familyMembers']

        raw_nutriments = prod.get('nutriments', {})
        ingredients_text = prod.get('ingredients', '')
        allergen_tags = prod.get('allergens', [])
        categories = prod.get('categories', [])
        serving_size_text = prod.get('servingSize', '')
        product_name = prod.get('productName', 'Analyzed Product')
        barcode = prod.get('barcode', '')

        # 1. Data Completeness Evaluation
        completeness = V2DataCompletenessEngine.evaluate_completeness(
            raw_nutriments, ingredients_text, allergen_tags
        )

        # 2. Food Category Resolution
        resolved_category = self.category_engine.resolve_category(
            categories_list=categories,
            product_name=product_name,
            ingredients_text=ingredients_text
        )
        category_key = resolved_category['key'] if resolved_category else None
        category_name = resolved_category['name'] if resolved_category else "General Packaged Food"

        # 3. Stage 1: Product-Level Food Profile (Evaluated independently of family members)
        food_profile = V2FoodProfileEngine.calculate_food_profile(
            raw_nutriments, completeness, category_key, ingredients_text
        )
        grade_letter = food_profile.grade
        grade_label = food_profile.interpretation
        profile_score = food_profile.score
        profile_factors = food_profile.factors

        # 4. Stage 1: Product-Level General Frequency (Independent of family members)
        if grade_letter in ["A", "B"]:
            product_general_freq = "REGULAR"
        elif grade_letter == "C":
            product_general_freq = "OCCASIONAL"
        elif grade_letter in ["D", "E"]:
            product_general_freq = "LIMIT FREQUENCY"
        else:
            product_general_freq = "INSUFFICIENT DATA"

        # 5. Layer 2: Nutrient Findings
        nutrient_findings = V2NutrientFindingEngine.analyze_nutrients(raw_nutriments)

        # 6. Ingredient & Allergen Intelligence
        allergen_flags = self.allergen_detector.detect_allergens(ingredients_text, allergen_tags)
        detected_allergens = self.allergen_detector.get_detected_allergen_list(ingredients_text, allergen_tags)
        concern_flags = self.concern_detector.detect_concerns(ingredients_text)

        # 7. Stage 2: Person-Level Personalized Guidance per Member
        # (Consumes product grade from Stage 1, NEVER mutates it)
        member_recommendations = []
        family_guidance_list = []
        consulted_evidence = set([
            "WHO Guideline: Sugars intake (2015)",
            "WHO Saturated Fatty Acid Guideline (2023)",
            "WHO Sodium Report (2023)",
            "Codex General Standard for the Labelling of Prepackaged Foods",
            "Nutri-Score Standard Algorithm (Rayner et al. / Santé Publique France)"
        ])

        for member in family_members:
            m_id = member.get('id')
            m_name = member.get('name', 'Member')
            m_age = member.get('age', 30)

            # Clean Stage 2 guidance object
            guidance_item = V2GuidanceEngine.calculate_personal_guidance(
                product=prod,
                food_profile=food_profile,
                family_member=member,
                allergen_flags=allergen_flags,
                detected_allergens=detected_allergens,
                category_key=category_key,
                completeness=completeness
            )
            family_guidance_list.append(guidance_item)

            # Personal Context Evaluation for backward-compatible recommendations
            personal_eval = V2PersonalContextEngine.evaluate_member_context(
                member=member,
                nutriments=raw_nutriments,
                allergen_flags=allergen_flags,
                detected_allergens=detected_allergens,
                ingredients_text=ingredients_text,
                category_key=category_key
            )

            # Check if KDIGO was consulted
            if any("Kidney Disease" in c for c in personal_eval["dietary_considerations"]):
                consulted_evidence.add("KDOQI Clinical Practice Guideline for Nutrition in CKD (2020 Update)")

            member_frequency = guidance_item["guidance"]
            status_label = guidance_item["status"]
            summary_reason = guidance_item["summary_reason"]
            guidance_text = guidance_item["guidance_text"]

            if member_frequency == "AVOID":
                cat_legacy = "AVOID"
                risk_level_legacy = "HIGH"
                risk_score_legacy = 100.0
            elif member_frequency in ["LIMIT FREQUENCY", "OCCASIONAL"]:
                cat_legacy = "CAUTION"
                risk_level_legacy = "MODERATE"
                risk_score_legacy = 50.0
            elif member_frequency in ["INSUFFICIENT DATA", "INSUFFICIENT INFORMATION"]:
                cat_legacy = "CAUTION"
                risk_level_legacy = "MODERATE"
                risk_score_legacy = 0.0
            else:
                cat_legacy = "RECOMMENDED"
                risk_level_legacy = "LOW"
                risk_score_legacy = 15.0

            # Build health factor breakdown
            health_factors_list = []
            for conf in personal_eval["hard_safety_conflicts"]:
                health_factors_list.append({
                    "name": "Hard Safety Alert",
                    "impact": "HIGH",
                    "description": conf,
                    "isAllergen": True
                })
            for sc in personal_eval["soft_concerns"]:
                health_factors_list.append({
                    "name": "Nutritional Consideration",
                    "impact": "MODERATE",
                    "description": sc,
                    "isAllergen": False
                })
            for un in personal_eval["uncertainty_notices"]:
                health_factors_list.append({
                    "name": "Clinical Uncertainty Notice",
                    "impact": "MODERATE",
                    "description": un,
                    "isAllergen": False
                })

            # Health summary label
            conditions_summary = []
            if member.get('healthConditions'):
                conditions_summary.append(", ".join(member.get('healthConditions')))
            if member.get('allergies'):
                conditions_summary.append("Allergies: " + ", ".join(member.get('allergies')))
            if member.get('dietaryPreferences'):
                conditions_summary.append(", ".join(member.get('dietaryPreferences')))
            summary_str = " | ".join(conditions_summary) if conditions_summary else "General Dietary Context"

            member_recommendations.append({
                "familyMemberId": m_id,
                "familyMemberName": m_name,
                "familyMemberAge": m_age,
                "healthSummary": summary_str,
                "category": cat_legacy,  # RECOMMENDED / CAUTION / AVOID
                "v2_status": status_label,  # FAVORABLE / CONSIDERATIONS / HIGHER CONCERN / AVOID / INSUFFICIENT DATA
                "riskLevel": risk_level_legacy,
                "riskScore": risk_score_legacy,
                "summaryReason": summary_reason,
                "guidance": guidance_text,
                "healthFactors": health_factors_list,
                "warnings": personal_eval["hard_safety_conflicts"] + personal_eval["soft_concerns"],
                "foodGrade": grade_letter,  # Guaranteed identical product grade
                "frequencyRecommendation": member_frequency,
                "dietaryConsiderations": personal_eval["dietary_considerations"],
                "uncertaintyNotices": personal_eval["uncertainty_notices"]
            })

        # Overall product verdict
        if grade_letter == "INSUFFICIENT DATA":
            overall_verdict = "Insufficient nutritional data available on product packaging to establish a reliable product grade."
        else:
            overall_verdict = f"Product Profile {grade_letter} ({grade_label}) calculated independently from nutrient composition. Review family guidance for individual dietary context."

        response_payload = {
            "version": "v2",
            "philosophy": (
                "HealthSense AI does not diagnose, prescribe, or determine medical safety. "
                "It analyzes available food composition and ingredient information against documented nutrition "
                "evidence and the user's recorded dietary context, then provides informational food insights with appropriate uncertainty."
            ),
            "barcode": barcode,
            "productName": product_name,
            "overallVerdict": overall_verdict,
            "analyzedAt": int(time.time() * 1000),
            "disclaimer": "Informational food nutrition analysis only. Not medical advice, clinical diagnosis, or dietary prescription.",
            "foodGrade": grade_letter,
            "foodGradeInterpretation": grade_label,
            "foodQualityScore": profile_score,
            "activeModel": "HealthSense V2 Evidence-Informed Engine",
            "source": "REMOTE_BACKEND_V2",
            "assessmentConfidence": completeness["nutrition_data"],
            "frequencyRecommendation": product_general_freq,
            "food_profile": {
                "grade": grade_letter,
                "interpretation": grade_label,
                "score": profile_score,
                "category": category_name,
                "methodology": getattr(food_profile, 'methodology', "Nutri-Score Standard Algorithm"),
                "basis": getattr(food_profile, 'basis', {}),
                "factors": profile_factors
            },
            "nutrient_findings": nutrient_findings,
            "data_completeness": completeness,
            "confidence_breakdown": {
                "data_completeness_pct": completeness["nutrition_coverage_pct"],
                "data_completeness_level": completeness["nutrition_data"],
                "evidence_confidence": completeness["evidence_applicability"],
                "model_confidence_label": "High (Rule-derived classifier confidence only; not clinical certainty)",
                "medical_certainty_disclaimer": "Confidence metrics reflect data completeness and rule matching only; never medical certainty or clinical probability."
            },
            "family_guidance": family_guidance_list,
            "recommendations": member_recommendations,
            "evidence_sources": list(consulted_evidence)
        }

        return Response(response_payload, status=status.HTTP_200_OK)
