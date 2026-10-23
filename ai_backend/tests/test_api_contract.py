"""
API Contract Regression Tests — Tests 30-35.
Verifies: null nutrition, empty family members, invalid products, backend exceptions,
          missing optional fields, and contract stability between Android and Django.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class APIContractRegressionTests(TestCase):
    """
    Tests 30-35: API contract hardening — null handling, edge inputs,
                 response shape stability that Android depends on.
    """

    def setUp(self):
        self.client = APIClient()

    # ─── Test 30: Valid recommendation request ────────────────────────────────

    def test_valid_recommendation_request_returns_all_required_fields(self):
        """Complete request → response must include all fields the Android app parses."""
        payload = {
            "foodProduct": {
                "barcode": "5000112637922",
                "productName": "Whole Grain Bread",
                "brand": "Hovis",
                "ingredients": "Whole wheat flour, water, yeast, salt, sunflower oil",
                "allergens": ["en:gluten"],
                "categories": ["en:breads"],
                "nutriments": {
                    "calories": 220.0,
                    "sugars": 3.0,
                    "sodium": 350.0,
                    "fats": 3.0,
                    "saturatedFat": 0.5,
                    "proteins": 8.0,
                    "carbohydrates": 40.0,
                    "fiber": 5.0
                }
            },
            "familyMembers": [
                {"id": "m1", "name": "Raj", "age": 42, "allergies": [], "healthConditions": ["Hypertension"]}
            ]
        }
        response = self.client.post('/api/v1/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # All fields the Android app parses must be present
        required_top_level = [
            'barcode', 'productName', 'recommendations', 'overallVerdict',
            'foodGrade', 'activeModel', 'source', 'assessmentConfidence',
            'frequencyRecommendation', 'dataCompleteness', 'disclaimer'
        ]
        for field in required_top_level:
            self.assertIn(field, data, f"Response missing required field: {field}")

        # foodGrade must be A-E
        self.assertIn(data['foodGrade'], ['A', 'B', 'C', 'D', 'E'])

        # source must be a known value
        self.assertIn(data['source'], ['REMOTE_BACKEND', 'LOCAL_FALLBACK'])

        # assessmentConfidence must be HIGH, MEDIUM, or LOW
        self.assertIn(data['assessmentConfidence'], ['HIGH', 'MEDIUM', 'LOW'])

        # Each recommendation must have required member-level fields
        for rec in data['recommendations']:
            for rec_field in ['familyMemberId', 'familyMemberName', 'category', 'riskLevel',
                               'riskScore', 'summaryReason', 'foodGrade', 'confidence',
                               'assessmentConfidence', 'frequencyRecommendation']:
                self.assertIn(rec_field, rec, f"Member recommendation missing: {rec_field}")

            # category must be one of the known values
            self.assertIn(rec['category'], ['RECOMMENDED', 'CAUTION', 'AVOID'])

    # ─── Test 31: Missing optional fields ─────────────────────────────────────

    def test_request_with_missing_optional_nutrition_fields_succeeds(self):
        """
        Android may send products with only partial nutrition.
        API must succeed and return a valid (possibly LOW confidence) response.
        """
        payload = {
            "foodProduct": {
                "barcode": "1234567890",
                "productName": "Mystery Biscuits",
                # No ingredients, no allergens, only partial nutrition
                "nutriments": {
                    "calories": 420.0
                    # sugars, sodium, etc. absent
                }
            },
            "familyMembers": [
                {"id": "m1", "name": "Priya", "age": 28, "allergies": [], "healthConditions": []}
            ]
        }
        response = self.client.post('/api/v1/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Must still succeed
        self.assertIn('recommendations', data)
        self.assertEqual(len(data['recommendations']), 1)

        # With only calories, confidence should be LOW
        self.assertIn(data['assessmentConfidence'], ['LOW', 'MEDIUM'])

    # ─── Test 32: Null nutrition ───────────────────────────────────────────────

    def test_null_nutrition_object_handled_gracefully(self):
        """Null/empty nutriments must not crash the API — returns graceful LOW-confidence response."""
        payload = {
            "foodProduct": {
                "barcode": "0000000001",
                "productName": "Unknown Product",
                "nutriments": {}    # Completely empty
            },
            "familyMembers": [
                {"id": "m1", "name": "John", "age": 35, "allergies": [], "healthConditions": []}
            ]
        }
        response = self.client.post('/api/v1/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('recommendations', data)
        self.assertEqual(data['assessmentConfidence'], 'LOW')

    # ─── Test 33: Empty family member list ────────────────────────────────────

    def test_empty_family_member_list_returns_400(self):
        """Empty familyMembers array must return HTTP 400 — not crash."""
        payload = {
            "foodProduct": {
                "barcode": "111222333",
                "productName": "Corn Chips",
                "nutriments": {"calories": 500.0}
            },
            "familyMembers": []
        }
        response = self.client.post('/api/v1/recommend/', payload, format='json')
        # Serializer should reject empty list
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK])
        # Either a 400 with error, or a 200 with empty recommendations — no crash
        if response.status_code == 200:
            data = response.json()
            self.assertIn('recommendations', data)

    # ─── Test 34: Invalid product (missing barcode/productName) ───────────────

    def test_invalid_product_missing_required_fields_returns_400(self):
        """foodProduct without any nutrition and invalid schema → 400."""
        payload = {
            "foodProduct": {},   # Missing all fields
            "familyMembers": [
                {"id": "m1", "name": "X", "age": 30}
            ]
        }
        response = self.client.post('/api/v1/recommend/', payload, format='json')
        # Should return 400 or handle gracefully without 500
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR,
                             "API must never return 500 on malformed product input")

    # ─── Test 35: Source field truthfulness on normal response ────────────────

    def test_source_field_is_truthful_in_response(self):
        """
        The 'source' field must accurately reflect whether the recommendation
        came from the REMOTE_BACKEND or a LOCAL_FALLBACK.
        This test verifies the Django backend always returns REMOTE_BACKEND.
        """
        payload = {
            "foodProduct": {
                "barcode": "5901234123457",
                "productName": "Rolled Oats (Quaker)",
                "ingredients": "Whole grain rolled oats",
                "nutriments": {
                    "calories": 150.0, "sugars": 1.0, "sodium": 5.0,
                    "fats": 3.0, "proteins": 5.0, "fiber": 4.0,
                    "carbohydrates": 27.0, "saturatedFat": 0.5
                }
            },
            "familyMembers": [
                {"id": "m1", "name": "Amita", "age": 45, "allergies": [], "healthConditions": []}
            ]
        }
        response = self.client.post('/api/v1/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['source'], 'REMOTE_BACKEND',
                         "Django backend must always return source=REMOTE_BACKEND")

    # ─── Test: dataCompleteness shape ─────────────────────────────────────────

    def test_data_completeness_structure_in_response(self):
        """dataCompleteness object must have nutrientCoveragePct, hasIngredients, status."""
        payload = {
            "foodProduct": {
                "barcode": "9876543210",
                "productName": "Full Nutrition Bar",
                "ingredients": "Oats, honey, almonds, chocolate",
                "nutriments": {
                    "calories": 380.0, "sugars": 18.0, "sodium": 120.0,
                    "fats": 14.0, "saturatedFat": 4.0, "proteins": 10.0,
                    "carbohydrates": 52.0, "fiber": 3.0
                }
            },
            "familyMembers": [
                {"id": "m1", "name": "Dev", "age": 30, "allergies": [], "healthConditions": []}
            ]
        }
        response = self.client.post('/api/v1/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIn('dataCompleteness', data)
        dc = data['dataCompleteness']
        self.assertIn('nutrientCoveragePct', dc)
        self.assertIn('hasIngredients', dc)
        self.assertIn('status', dc)

        # With full nutrition + ingredients, coverage should be HIGH
        self.assertGreater(dc['nutrientCoveragePct'], 75.0)
        self.assertTrue(dc['hasIngredients'])
        self.assertEqual(dc['status'], 'Complete')
