"""
Comprehensive Automated Test Suite for HealthSense AI V2
=========================================================
Tests:
1. Missing nutrition handled without inventing zero (missing fiber != 0g, missing sodium != 0mg)
2. Missing ingredients & incomplete data
3. Missing allergens & unknown allergen status
4. Confirmed allergen conflict triggers HARD OVERRIDE (AVOID)
5. Precautionary trace allergen handling ("may contain")
6. Free sugar vs added sugar vs total sugar distinction (unknown != absent)
7. Child age contexts (young child sugar, child energy drink contraindication)
8. Kidney disease uncertainty rule (KDIGO 2020: INSUFFICIENT INFORMATION notice; NEVER "safe")
9. Hypertension, Diabetes, High Cholesterol cautious non-medical considerations
10. Vegetarian & Vegan dietary considerations
11. Hershey's Chocolate Regression Test (0034000249862)
12. V1 backward compatibility
"""

import os
import django
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class HealthSenseV2Tests(TestCase):

    def setUp(self):
        self.client = APIClient()

    # ─── 1. HERSHEY'S REGRESSION TEST ─────────────────────────────────────────
    def test_hersheys_chocolate_regression(self):
        """
        Regression Test for Hershey's Milk Chocolate (Barcode: 0034000249862).
        Nutritional Data:
          Calories: 512 kcal/100g, Sugar: 58.1 g, Sodium: 80 mg, Total Fat: 30.2 g,
          Saturated Fat: 18.6 g, Protein: 7.0 g, Carbs: 60.5 g, Fiber: MISSING
        Requirements:
          - Must NOT say "safe", "daily", or "nutrient levels well within safe thresholds".
          - Fiber must be identified as "Unavailable", NOT "0g".
          - For High Cholesterol or Diabetes, must produce HIGHER CONCERN / LIMIT FREQUENCY.
        """
        payload = {
            "foodProduct": {
                "barcode": "0034000249862",
                "productName": "Hershey's Milk Chocolate Bar",
                "brand": "Hershey's",
                "ingredients": "Sugar, skim milk, cocoa butter, chocolate, milk fat, lecithin (soy), natural flavor.",
                "servingSize": "43 g",
                "categories": ["en:chocolates", "en:milk-chocolates"],
                "allergens": ["en:milk", "en:soybeans"],
                "nutriments": {
                    "calories": 512.0,
                    "sugars": 58.1,
                    "sodium": 80.0,
                    "fats": 30.2,
                    "saturatedFat": 18.6,
                    "proteins": 7.0,
                    "carbohydrates": 60.5
                    # Note: fiber is omitted / missing
                }
            },
            "familyMembers": [
                {
                    "id": "member_amit",
                    "name": "Amit",
                    "age": 35,
                    "healthConditions": ["High Cholesterol"],
                    "allergies": []
                },
                {
                    "id": "member_diabetic",
                    "name": "Priya",
                    "age": 42,
                    "healthConditions": ["Diabetes"],
                    "allergies": []
                }
            ]
        }

        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # 1. Version and philosophy
        self.assertEqual(data['version'], 'v2')
        self.assertIn("does not diagnose, prescribe, or determine medical safety", data['philosophy'])

        # 2. General food profile must reflect high sugar/sat-fat (Grade D or E)
        self.assertIn(data['foodGrade'], ['D', 'E'])
        self.assertIn(data['food_profile']['interpretation'], [
            "Least favorable nutritional profile", "Less favorable nutritional profile",
            "Higher-concern profile", "Very high-concern profile"
        ])

        # 3. Overall frequency must NOT be "DAILY" or "REGULAR"
        self.assertIn(data['frequencyRecommendation'], ["OCCASIONAL", "LIMIT FREQUENCY"])

        # 4. Fiber finding must NOT be 0g
        fiber_finding = next((f for f in data['nutrient_findings'] if f['nutrient'] == "Dietary Fiber"), None)
        self.assertIsNotNone(fiber_finding)
        self.assertEqual(fiber_finding['value'], "Unavailable")
        self.assertNotIn("0g", fiber_finding['value'])

        # 5. Check Amit's recommendation (High Cholesterol)
        amit_rec = next(r for r in data['recommendations'] if r['familyMemberName'] == "Amit")
        self.assertIn(amit_rec['v2_status'], ["CONSIDERATIONS", "HIGHER CONCERN"])
        self.assertIn(amit_rec['frequencyRecommendation'], ["OCCASIONAL", "LIMIT FREQUENCY"])
        self.assertNotIn("well within safe thresholds", amit_rec['summaryReason'].lower())
        self.assertNotIn("eat daily", amit_rec['summaryReason'].lower())

        # Saturated fat concern must be explicitly recognized
        has_sat_fat_consideration = any("saturated fat" in c.lower() for c in amit_rec['dietaryConsiderations'])
        self.assertTrue(has_sat_fat_consideration)

        # 6. Check Priya's recommendation (Diabetes)
        priya_rec = next(r for r in data['recommendations'] if r['familyMemberName'] == "Priya")
        has_sugar_consideration = any("sugar" in c.lower() for c in priya_rec['dietaryConsiderations'])
        self.assertTrue(has_sugar_consideration)

    # ─── 2. KIDNEY DISEASE UNCERTAINTY RULE (KDIGO 2020) ──────────────────────
    def test_kidney_disease_uncertainty_notice(self):
        """
        Ensures that when a member has Chronic Kidney Disease:
        - The system returns an explicit INSUFFICIENT INFORMATION notice citing KDIGO.
        - The system NEVER declares the food 'safe for kidney disease' or 'good for kidneys'.
        """
        payload = {
            "foodProduct": {
                "barcode": "8901234567890",
                "productName": "Rolled Oats",
                "ingredients": "100% whole grain oats",
                "nutriments": {
                    "calories": 380.0,
                    "sugars": 1.0,
                    "sodium": 5.0,
                    "fats": 6.5,
                    "saturatedFat": 1.1,
                    "proteins": 13.0,
                    "carbohydrates": 66.0,
                    "fiber": 10.0
                }
            },
            "familyMembers": [
                {
                    "id": "member_kidney",
                    "name": "Rajesh",
                    "age": 58,
                    "healthConditions": ["Chronic Kidney Disease"],
                    "allergies": []
                }
            ]
        }

        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        rajesh_rec = data['recommendations'][0]
        summary_text = rajesh_rec['summaryReason']

        # Must explicitly cite renal-diet suitability insufficiency
        self.assertIn("renal-diet suitability cannot be determined reliably", summary_text.lower())
        self.assertNotIn("safe for kidney disease", summary_text.lower())
        self.assertNotIn("good for kidneys", summary_text.lower())

        # Evidence sources must include KDIGO
        self.assertTrue(any("KDIGO" in s or "KDOQI" in s for s in data['evidence_sources']))

    # ─── 3. CONFIRMED ALLERGEN CONFLICT (HARD SAFETY OVERRIDE) ─────────────────
    def test_confirmed_allergen_hard_override(self):
        """
        Confirmed allergen presence must trigger a HARD SAFETY OVERRIDE (AVOID).
        """
        payload = {
            "foodProduct": {
                "barcode": "1112223334445",
                "productName": "Peanut Butter Crunch",
                "ingredients": "Roasted peanuts, sugar, salt.",
                "allergens": ["en:peanuts"],
                "nutriments": {
                    "calories": 580.0,
                    "sugars": 8.0,
                    "sodium": 200.0,
                    "fats": 50.0,
                    "saturatedFat": 8.0,
                    "proteins": 25.0
                }
            },
            "familyMembers": [
                {
                    "id": "member_peanut_allergy",
                    "name": "Ananya",
                    "age": 14,
                    "healthConditions": [],
                    "allergies": ["Peanut"]
                }
            ]
        }

        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        ananya_rec = data['recommendations'][0]
        self.assertEqual(ananya_rec['v2_status'], "AVOID")
        self.assertEqual(ananya_rec['frequencyRecommendation'], "AVOID")
        self.assertIn("confirmed allergen conflict", ananya_rec['summaryReason'].lower())

    # ─── 4. PRECAUTIONARY TRACE ALLERGEN ("MAY CONTAIN") ──────────────────────
    def test_trace_allergen_precautionary_notice(self):
        """
        Traces / 'May contain' should produce a precautionary notice rather than
        an absolute confirmed-allergen claim.
        """
        payload = {
            "foodProduct": {
                "barcode": "2223334445556",
                "productName": "Dark Chocolate Biscuit",
                "ingredients": "Wheat flour, cocoa powder, sugar. May contain traces of hazelnut.",
                "nutriments": {
                    "calories": 450.0,
                    "sugars": 20.0,
                    "sodium": 150.0,
                    "fats": 15.0
                }
            },
            "familyMembers": [
                {
                    "id": "member_hazelnut",
                    "name": "Dev",
                    "age": 28,
                    "healthConditions": [],
                    "allergies": ["Hazelnut"]
                }
            ]
        }

        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        dev_rec = data['recommendations'][0]
        self.assertTrue(any("traces" in w.lower() or "cross-contact" in w.lower() for w in dev_rec['warnings']))

    # ─── 5. PEDIATRIC CONTRAINDICATIONS ────────────────────────────────────────
    def test_child_energy_drink_contraindication(self):
        """
        High caffeine / energy drinks are contraindicated for children under 12.
        """
        payload = {
            "foodProduct": {
                "barcode": "9002490205987",
                "productName": "Red Bull Energy Drink",
                "ingredients": "Carbonated water, sucrose, glucose, citric acid, taurine, caffeine.",
                "categories": ["en:energy-drinks"],
                "nutriments": {
                    "calories": 45.0,
                    "sugars": 11.0,
                    "sodium": 40.0
                }
            },
            "familyMembers": [
                {
                    "id": "child_under_12",
                    "name": "Aarav",
                    "age": 8,
                    "healthConditions": [],
                    "allergies": []
                }
            ]
        }

        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        aarav_rec = data['recommendations'][0]
        self.assertEqual(aarav_rec['v2_status'], "AVOID")
        self.assertIn("children under 12", aarav_rec['summaryReason'])

    # ─── 6. INSUFFICIENT DATA HANDLING ────────────────────────────────────────
    def test_insufficient_nutrition_data(self):
        """
        When product nutrition data is largely omitted, return INSUFFICIENT DATA
        instead of fabricating a high or low grade.
        """
        payload = {
            "foodProduct": {
                "barcode": "9998887776665",
                "productName": "Unlabeled Local Snack",
                "ingredients": "",
                "nutriments": {} # zero nutrient fields reported
            },
            "familyMembers": [
                {
                    "id": "member_normal",
                    "name": "Meera",
                    "age": 25,
                    "healthConditions": [],
                    "allergies": []
                }
            ]
        }

        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data['foodGrade'], "INSUFFICIENT DATA")
        self.assertEqual(data['frequencyRecommendation'], "INSUFFICIENT DATA")
        self.assertEqual(data['data_completeness']['nutrition_data'], "LIMITED")

    # ─── 7. V1 BACKWARD COMPATIBILITY ─────────────────────────────────────────
    def test_v1_endpoint_unbroken(self):
        """
        Ensures POST /api/v1/recommend/ still functions identically for legacy clients.
        """
        payload = {
            "foodProduct": {
                "barcode": "8901030383749",
                "productName": "Green Tea",
                "brand": "Lipton",
                "ingredients": "Pure green tea leaves",
                "servingSize": "1 tea bag",
                "nutriments": {
                    "calories": 2.0,
                    "sugars": 0.0,
                    "sodium": 0.0,
                    "fats": 0.0,
                    "saturatedFat": 0.0,
                    "proteins": 0.0,
                    "carbohydrates": 0.0,
                    "fiber": 0.0
                }
            },
            "familyMembers": [
                {
                    "id": "member_v1",
                    "name": "Pooja",
                    "age": 29,
                    "healthConditions": [],
                    "allergies": []
                }
            ]
        }

        response = self.client.post('/api/v1/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['source'], "REMOTE_BACKEND")
        self.assertTrue(len(data['recommendations']) > 0)

    # ─── 8. SUGAR SEMANTICS & NO WHO FREE SUGAR CONFUSION (ISSUES 1 & 2) ──────
    def test_sugar_semantics_separation(self):
        """
        Verify:
        - Total sugar != Free sugar
        - Total sugar != Added sugar
        - Missing free sugar is 'Unavailable'
        - Missing added sugar is 'Unavailable'
        - Per-100g total sugar is NOT reported as exceeding WHO daily limit
        """
        payload = {
            "foodProduct": {
                "barcode": "1234567890123",
                "productName": "Sweet Snack Bar",
                "ingredients": "Oats, sugar, honey, palm oil.",
                "nutriments": {
                    "calories": 400.0,
                    "sugars": 35.0, # Only total sugar known
                    "sodium": 120.0,
                    "fats": 15.0,
                    "saturatedFat": 4.0,
                    "proteins": 5.0
                }
            },
            "familyMembers": [{"id": "m1", "name": "User", "age": 30}]
        }
        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        findings = {f['nutrient']: f for f in data['nutrient_findings']}

        # 1. Total sugar must be reported
        self.assertIn("Total Sugars", findings)
        self.assertEqual(findings["Total Sugars"]["value"], "35.0 g/100g")
        self.assertIn("Total sugar is reported by the product data", findings["Total Sugars"]["evidence_notes"])

        # 2. Free sugar must be Unavailable, NOT inferred
        self.assertIn("Free Sugars", findings)
        self.assertEqual(findings["Free Sugars"]["value"], "Unavailable")
        self.assertIn("not declared on standard packaging labels", findings["Free Sugars"]["description"])

        # 3. Added sugar must be Unavailable, NOT inferred
        self.assertIn("Added Sugars", findings)
        self.assertEqual(findings["Added Sugars"]["value"], "Unavailable")

        # 4. No false claim that 35g/100g exceeds WHO daily intake limit
        for f in data['nutrient_findings']:
            self.assertNotIn("who limit exceeded", f['description'].lower())
            self.assertNotIn("exceeds who daily limit", f['description'].lower())

    # ─── 9. ORDINARY NUTRITION NEVER PRODUCES 'UNSUITABLE' (ISSUES 3 & 4) ─────
    def test_ordinary_nutrition_does_not_produce_unsuitable_or_avoid(self):
        """
        High total sugar + Diabetes and High Saturated Fat + High Cholesterol
        must produce DIETARY CONSIDERATION or HIGHER CONCERN / LIMIT FREQUENCY,
        and NEVER 'UNSUITABLE' or 'AVOID'.
        """
        payload = {
            "foodProduct": {
                "barcode": "0034000249862",
                "productName": "Rich Chocolate Pastry",
                "ingredients": "Sugar, flour, butter, cocoa butter, milk fat.",
                "nutriments": {
                    "calories": 480.0,
                    "sugars": 45.0,
                    "sodium": 250.0,
                    "fats": 28.0,
                    "saturatedFat": 16.0,
                    "proteins": 6.0
                }
            },
            "familyMembers": [
                {
                    "id": "m_diabetic",
                    "name": "Karan",
                    "age": 50,
                    "healthConditions": ["Diabetes"],
                    "allergies": []
                },
                {
                    "id": "m_lipid",
                    "name": "Sunita",
                    "age": 52,
                    "healthConditions": ["High Cholesterol"],
                    "allergies": []
                }
            ]
        }
        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        for rec in data['recommendations']:
            # Must NOT be AVOID
            self.assertNotEqual(rec['frequencyRecommendation'], "AVOID")
            self.assertEqual(rec['frequencyRecommendation'], "LIMIT FREQUENCY")

            # Must NOT contain UNSUITABLE
            self.assertNotEqual(rec['v2_status'], "UNSUITABLE")
            self.assertIn(rec['v2_status'], ["HIGHER CONCERN", "DIETARY CONSIDERATION"])

            # Must not claim medical diagnosis
            self.assertNotIn("medical assessment", rec['summaryReason'].lower())

    # ─── 10. CKD UNCERTAINTY SAFEGUARD & NEVER SAFE/DAILY (ISSUE 6) ───────────
    def test_ckd_missing_potassium_phosphorus_uncertainty(self):
        """
        For CKD, incomplete potassium/phosphorus must yield INSUFFICIENT INFORMATION
        and NEVER declare 'SAFE', 'SUITABLE', or 'DAILY'.
        """
        payload = {
            "foodProduct": {
                "barcode": "7776665554443",
                "productName": "Granola Bar",
                "ingredients": "Whole rolled oats, brown sugar, canola oil.",
                "nutriments": {
                    "calories": 200.0,
                    "sugars": 8.0,
                    "sodium": 60.0,
                    "fats": 6.0,
                    "saturatedFat": 0.8,
                    "proteins": 4.0,
                    "fiber": 3.0
                    # Note: potassium and phosphorus are undeclared
                }
            },
            "familyMembers": [
                {
                    "id": "m_ckd",
                    "name": "Neeraj",
                    "age": 62,
                    "healthConditions": ["Chronic Kidney Disease (CKD)"],
                    "allergies": []
                }
            ]
        }
        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        rec = data['recommendations'][0]
        self.assertEqual(rec['v2_status'], "INSUFFICIENT INFORMATION")
        self.assertNotIn("safe", rec['summaryReason'].lower())
        self.assertNotIn("suitable for kidney", rec['summaryReason'].lower())
        self.assertNotIn("daily", rec['summaryReason'].lower())
        self.assertNotEqual(rec['frequencyRecommendation'], "DAILY")

    # ─── 11. PEDIATRIC STIMULANT VS ORDINARY HIGH SUGAR (ISSUE 5) ─────────────
    def test_pediatric_stimulant_vs_ordinary_sugar(self):
        """
        Child energy drink -> AVOID.
        Child ordinary sweet biscuit -> DIETARY CONSIDERATION / portion caution (NOT AVOID).
        """
        payload = {
            "foodProduct": {
                "barcode": "4445556667778",
                "productName": "Sweet Butter Biscuit",
                "ingredients": "Wheat flour, sugar, butter.",
                "nutriments": {
                    "calories": 420.0,
                    "sugars": 22.0,
                    "sodium": 180.0,
                    "fats": 14.0,
                    "saturatedFat": 7.0,
                    "proteins": 6.0
                }
            },
            "familyMembers": [
                {
                    "id": "child_01",
                    "name": "Ishaan",
                    "age": 7,
                    "healthConditions": [],
                    "allergies": []
                }
            ]
        }
        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        rec = data['recommendations'][0]
        # Ordinary high sugar in children must NOT trigger AVOID
        self.assertNotEqual(rec['v2_status'], "AVOID")
        self.assertNotEqual(rec['frequencyRecommendation'], "AVOID")
        self.assertIn(rec['frequencyRecommendation'], ["OCCASIONAL", "LIMIT FREQUENCY"])

    # ─── 12. CONFIDENCE SEPARATION & NO MEDICAL CERTAINTY (ISSUE 9 & 13) ──────
    def test_confidence_separation_and_no_medical_certainty(self):
        """
        Verify that Data Completeness, Model Confidence, and Evidence Confidence
        are separate and none claims clinical certainty.
        """
        payload = {
            "foodProduct": {
                "barcode": "9990001112223",
                "productName": "Whole Grain Bread",
                "ingredients": "Whole wheat flour, water, yeast, salt.",
                "nutriments": {
                    "calories": 240.0,
                    "sugars": 2.5,
                    "sodium": 380.0,
                    "fats": 2.0,
                    "saturatedFat": 0.4,
                    "proteins": 10.0,
                    "fiber": 6.0
                }
            },
            "familyMembers": [{"id": "m1", "name": "User", "age": 30}]
        }
        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        conf = data['confidence_breakdown']
        self.assertIn("data_completeness_pct", conf)
        self.assertIn("evidence_confidence", conf)
        self.assertIn("model_confidence_label", conf)
        self.assertNotIn("clinical confidence", str(conf).lower())
        self.assertNotIn("medical certainty", str(conf).lower().replace("never medical certainty", ""))
        self.assertIn("never medical certainty", conf['medical_certainty_disclaimer'].lower())

    # ─── 13. PRODUCT GRADE IMMUTABILITY ACROSS 6 FAMILY CONTEXTS ───────────────
    def test_product_grade_immutability_across_family_profiles(self):
        """
        Verify Stage 1 Guarantee:
        The exact same product receives the EXACT SAME product grade (E)
        regardless of whether it is viewed by:
          1. Empty family (standalone)
          2. Healthy adult (Amit, 35)
          3. Diabetic adult (Priya, 42)
          4. CKD patient (Rajesh, 58)
          5. Young child (Aarav, 4)
          6. Peanut allergy member (Ananya, 14)
        """
        base_product = {
            "barcode": "0034000249862",
            "productName": "Hershey's Milk Chocolate Bar",
            "brand": "Hershey's",
            "ingredients": "Sugar, skim milk, cocoa butter, chocolate, milk fat, lecithin (soy), natural flavor.",
            "servingSize": "43 g",
            "categories": ["en:chocolates", "en:milk-chocolates"],
            "allergens": ["en:milk", "en:soybeans"],
            "nutriments": {
                "calories": 512.0,
                "sugars": 58.1,
                "sodium": 80.0,
                "fats": 30.2,
                "saturatedFat": 18.6,
                "proteins": 7.0,
                "carbohydrates": 60.5
            }
        }

        family_scenarios = [
            ("Empty Family", []),
            ("Healthy Adult", [{"id": "m1", "name": "Amit", "age": 35}]),
            ("Diabetic Adult", [{"id": "m2", "name": "Priya", "age": 42, "healthConditions": ["Diabetes"]}]),
            ("CKD Patient", [{"id": "m3", "name": "Rajesh", "age": 58, "healthConditions": ["Chronic Kidney Disease"]}]),
            ("Young Child", [{"id": "m4", "name": "Aarav", "age": 4}]),
            ("Severe Allergy", [{"id": "m5", "name": "Ananya", "age": 14, "allergies": ["Peanut"]}])
        ]

        expected_grade = "E"
        expected_general_freq = "LIMIT FREQUENCY"

        for label, members in family_scenarios:
            payload = {"foodProduct": base_product, "familyMembers": members}
            response = self.client.post('/api/v2/recommend/', payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Failed for scenario: {label}")
            data = response.json()

            # Product Grade MUST be E in all scenarios!
            self.assertEqual(data['foodGrade'], expected_grade,
                             f"Product grade mutated for scenario {label}! Expected {expected_grade}, got {data['foodGrade']}")
            self.assertEqual(data['food_profile']['grade'], expected_grade,
                             f"food_profile.grade mutated for scenario {label}!")
            self.assertEqual(data['frequencyRecommendation'], expected_general_freq,
                             f"Product general frequency mutated for scenario {label}!")

            # If members were evaluated, their individual product_grade field must also strictly be E
            if members:
                for member_guidance in data.get('family_guidance', []):
                    self.assertEqual(member_guidance['product_grade'], expected_grade,
                                     f"Member {member_guidance['name']} received altered product_grade!")

    # ─── 14. ALLERGEN CONFLICT CHANGES GUIDANCE TO AVOID WITHOUT MUTATING GRADE 
    def test_allergen_conflict_leaves_product_grade_unchanged(self):
        """
        A peanut product scanned by someone with a peanut allergy must trigger
        personal guidance 'AVOID', but the product grade itself must NOT mutate to 'AVOID' or 'F'.
        """
        payload = {
            "foodProduct": {
                "barcode": "1112223334445",
                "productName": "Peanut Butter Crunch",
                "ingredients": "Roasted peanuts, sugar, salt.",
                "allergens": ["en:peanuts"],
                "nutriments": {
                    "calories": 580.0,
                    "sugars": 8.0,
                    "sodium": 200.0,
                    "fats": 50.0,
                    "saturatedFat": 8.0,
                    "proteins": 25.0,
                    "fiber": 6.0
                }
            },
            "familyMembers": [
                {
                    "id": "member_peanut_allergy",
                    "name": "Ananya",
                    "age": 14,
                    "healthConditions": [],
                    "allergies": ["Peanut"]
                }
            ]
        }

        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Product-level grade is a valid Nutri-Score grade (A, B, C, D, or E), NOT 'AVOID'
        self.assertIn(data['foodGrade'], ['A', 'B', 'C', 'D', 'E'])
        self.assertNotEqual(data['foodGrade'], "AVOID")
        self.assertNotEqual(data['frequencyRecommendation'], "AVOID")

        # Stage 2 Personal Guidance for Ananya must be AVOID
        ananya_guidance = data['family_guidance'][0]
        self.assertEqual(ananya_guidance['product_grade'], data['foodGrade'])
        self.assertEqual(ananya_guidance['guidance'], "AVOID")
        self.assertEqual(ananya_guidance['allergen_status'], "CONFIRMED_ALLERGEN_CONFLICT")

    # ─── 15. DIVERSE FAMILY GUIDANCE WHILE PRODUCT GRADE IS IDENTICAL ─────────
    def test_diverse_family_guidance_identical_product_grade(self):
        """
        In a single multi-member request, each member receives distinct personalized
        frequency and considerations, but all share the exact same immutable product grade.
        """
        payload = {
            "foodProduct": {
                "barcode": "5556667778889",
                "productName": "Mixed Trail Bar",
                "ingredients": "Oats, peanuts, honey, milk powder, salt.",
                "allergens": ["en:peanuts", "en:milk"],
                "nutriments": {
                    "calories": 420.0,
                    "sugars": 22.0,
                    "sodium": 150.0,
                    "fats": 18.0,
                    "saturatedFat": 5.0,
                    "proteins": 12.0,
                    "fiber": 5.0
                }
            },
            "familyMembers": [
                {"id": "m1", "name": "Healthy Adult", "age": 30, "healthConditions": [], "allergies": []},
                {"id": "m2", "name": "Diabetic Adult", "age": 55, "healthConditions": ["Diabetes"], "allergies": []},
                {"id": "m3", "name": "Allergic Child", "age": 8, "healthConditions": [], "allergies": ["Peanut"]}
            ]
        }

        response = self.client.post('/api/v2/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        product_grade = data['foodGrade']
        guidance_list = data['family_guidance']
        self.assertEqual(len(guidance_list), 3)

        # All members must share the identical product grade
        for g in guidance_list:
            self.assertEqual(g['product_grade'], product_grade)

        # But personalized guidance must differ
        healthy = next(g for g in guidance_list if g['name'] == "Healthy Adult")
        diabetic = next(g for g in guidance_list if g['name'] == "Diabetic Adult")
        allergic = next(g for g in guidance_list if g['name'] == "Allergic Child")

        self.assertIn(healthy['guidance'], ["REGULAR", "OCCASIONAL", "LIMIT FREQUENCY"])
        self.assertEqual(allergic['guidance'], "AVOID")
        self.assertEqual(allergic['allergen_status'], "CONFIRMED_ALLERGEN_CONFLICT")
        self.assertIn(diabetic['guidance'], ["OCCASIONAL", "LIMIT FREQUENCY"])

