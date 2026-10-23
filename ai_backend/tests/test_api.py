"""
Integration tests for Django REST API endpoints (/api/health/ and /api/analyze/).
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class HealthSenseAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_health_check_endpoint(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('active_model', data)
        self.assertIn('available_models', data)

    def test_analyze_endpoint_peanut_allergy_conflict(self):
        payload = {
            "foodProduct": {
                "barcode": "0011223344",
                "productName": "Creamy Peanut Butter",
                "brand": "Skippy",
                "ingredients": "Roasted peanuts, sugar, hydrogenated vegetable oil, salt",
                "allergens": ["peanuts"],
                "nutriments": {
                    "calories": 590.0,
                    "sugars": 6.0,
                    "sodium": 290.0,
                    "fats": 50.0,
                    "saturatedFat": 8.0,
                    "proteins": 25.0,
                    "carbohydrates": 20.0,
                    "fiber": 6.0
                }
            },
            "familyMembers": [
                {
                    "id": "member_1",
                    "name": "Sarah (Allergic)",
                    "age": 14,
                    "allergies": ["Peanuts"],
                    "healthConditions": []
                },
                {
                    "id": "member_2",
                    "name": "Alex (Healthy)",
                    "age": 28,
                    "allergies": [],
                    "healthConditions": []
                }
            ]
        }

        response = self.client.post('/api/analyze/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIn('foodGrade', data)
        self.assertIn('recommendations', data)
        self.assertEqual(len(data['recommendations']), 2)

        # Sarah must be AVOID due to Peanut Allergen
        sarah_rec = next(r for r in data['recommendations'] if r['familyMemberId'] == 'member_1')
        self.assertEqual(sarah_rec['category'], 'AVOID')
        self.assertEqual(sarah_rec['riskLevel'], 'HIGH')
        self.assertEqual(sarah_rec['riskScore'], 100.0)

        # Alex should have lower risk
        alex_rec = next(r for r in data['recommendations'] if r['familyMemberId'] == 'member_2')
        self.assertIn(alex_rec['category'], ['RECOMMENDED', 'CAUTION'])

    def test_recommend_v1_backwards_compatibility(self):
        payload = {
            "foodProduct": {
                "barcode": "998877",
                "productName": "Rolled Oats",
                "ingredients": "Whole grain rolled oats",
                "nutriments": {
                    "calories": 150.0,
                    "sugars": 1.0,
                    "sodium": 0.0
                }
            },
            "familyMembers": [
                {
                    "name": "John",
                    "age": 40
                }
            ]
        }
        response = self.client.post('/api/v1/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['productName'], 'Rolled Oats')
        self.assertEqual(len(data['recommendations']), 1)
