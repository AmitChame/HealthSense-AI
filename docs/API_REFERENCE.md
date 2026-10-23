# HealthSense AI — REST API Reference Manual

**Base URL (Local Development)**: `http://localhost:8000/` (or `http://10.0.2.2:8000/` inside Android emulator)  
**Protocol**: HTTP/1.1 REST  
**Content-Type**: `application/json`  
**Authentication**: Open REST endpoint (stateless computation engine; client authentication managed via Firebase on device)

---

## 📑 Summary of Endpoints

| HTTP Method | Route | Description | Version | Status |
|:---:|:---|:---|:---:|:---:|
| `GET` | `/api/health/` | System health check and model registry status | V1 & V2 | Active |
| `POST` | `/api/v2/recommend/` | **Primary V2 Endpoint**: Two-stage decoupled nutritional evaluation & personalized guidance | V2.0 | Recommended |
| `POST` | `/api/v1/recommend/` | Legacy baseline ML recommendation with SHAP feature attributions | V1.0 | Supported |
| `POST` | `/api/analyze/` | Legacy alias for `/api/v1/recommend/` | V1.0 | Supported |

---

## 1. Health Check Endpoint

### `GET /api/health/`
Checks API availability, active ML model, and system readiness.

#### Response (`200 OK`):
```json
{
  "status": "healthy",
  "service": "HealthSense AI Backend",
  "version": "2.0.0",
  "active_model": "lightgbm",
  "available_models": [
    "lightgbm",
    "logistic_regression",
    "random_forest",
    "xgboost"
  ],
  "components": {
    "food_grader": true,
    "rule_engine": true,
    "ingredient_engine": true,
    "shap_explainer": true
  }
}
```

---

## 2. Primary Recommendation Endpoint (V2)

### `POST /api/v2/recommend/`
Performs decoupled two-stage nutritional analysis:
- **Stage 1**: Generates immutable Product-Level Food Profile (Grade A–E, Nutri-Score Rayner FSA algorithm per 100g).
- **Stage 2**: Evaluates each recorded family member against dietary health rules, allergen taxonomy, and clinical standards without altering the product grade.

#### Request Headers:
```http
Content-Type: application/json
Accept: application/json
```

#### Request Body Schema:
| Field | Type | Required | Description |
|---|---|:---:|---|
| `product` | Object | **Yes** | Packaged food product metadata and nutritional composition |
| `product.barcode` | String | **Yes** | EAN/UPC product barcode |
| `product.product_name` | String | **Yes** | Product commercial name |
| `product.brand` | String | No | Manufacturer brand name |
| `product.categories` | String | No | Comma-separated category tags from Open Food Facts |
| `product.ingredients` | String | No | Raw ingredient statement |
| `product.allergens` | Array of Strings | No | Explicit allergen tags reported by manufacturer |
| `product.nutriments` | Object | **Yes** | Nutritional values per 100g (or 100ml) |
| `product.nutriments.calories` | Float | No | Energy in kcal |
| `product.nutriments.sugars` | Float | No | Total sugars in grams per 100g |
| `product.nutriments.sodium` | Float | No | Sodium in milligrams per 100g |
| `product.nutriments.fat` | Float | No | Total lipids in grams per 100g |
| `product.nutriments.saturated_fat` | Float | No | Saturated fatty acids in grams per 100g |
| `product.nutriments.carbohydrates` | Float | No | Total carbohydrates in grams per 100g |
| `product.nutriments.protein` | Float | No | Protein in grams per 100g |
| `product.nutriments.fiber` | Float | No | Dietary fiber in grams per 100g |
| `family_members` | Array of Objects | **Yes** | List of family member profiles to evaluate |
| `family_members[].id` | String | **Yes** | Unique member identifier |
| `family_members[].name` | String | **Yes** | Display name |
| `family_members[].age` | Integer | **Yes** | Age in years |
| `family_members[].gender` | String | No | Gender ("Male", "Female", "Other") |
| `family_members[].health_conditions` | Array of Strings | No | Clinical conditions (e.g., "Diabetes (Type 2)", "Hypertension", "Chronic Kidney Disease") |
| `family_members[].allergies` | Array of Strings | No | Declared food allergies (e.g., "Peanuts", "Milk", "Tree Nuts", "Gluten") |
| `family_members[].dietary_preferences` | Array of Strings | No | Ethical/lifestyle choices (e.g., "Vegetarian", "Vegan", "Halal") |

#### Example Request:
```json
{
  "product": {
    "barcode": "8901030932456",
    "product_name": "Quaker Rolled Oats 100% Wholegrain",
    "brand": "Quaker",
    "categories": "Plant-based foods, Cereals and potatoes, Breakfasts, Rolled oats",
    "ingredients": "100% Whole Grain Rolled Oats",
    "allergens": [],
    "nutriments": {
      "calories": 389.0,
      "sugars": 1.0,
      "sodium": 5.0,
      "fat": 6.9,
      "saturated_fat": 1.2,
      "carbohydrates": 66.3,
      "protein": 16.9,
      "fiber": 10.6
    }
  },
  "family_members": [
    {
      "id": "fam_001",
      "name": "David",
      "age": 52,
      "gender": "Male",
      "health_conditions": ["Diabetes (Type 2)", "Hypertension"],
      "allergies": [],
      "dietary_preferences": ["Vegetarian"]
    },
    {
      "id": "fam_002",
      "name": "Ananya",
      "age": 6,
      "gender": "Female",
      "health_conditions": [],
      "allergies": ["Peanuts"],
      "dietary_preferences": ["None"]
    }
  ]
}
```

#### Example Successful Response (`200 OK`):
```json
{
  "barcode": "8901030932456",
  "product_name": "Quaker Rolled Oats 100% Wholegrain",
  "source": "REMOTE_BACKEND",
  "food_profile": {
    "grade": "A",
    "score": -4,
    "scientific_interpretation": "More favorable nutritional profile",
    "points_unfavorable": 4,
    "points_favorable": 8,
    "category_applied": "cereal_grain",
    "is_beverage": false,
    "data_sufficiency": "SUFFICIENT"
  },
  "family_recommendations": [
    {
      "member_id": "fam_001",
      "member_name": "David",
      "guidance": "REGULAR",
      "risk_level": "LOW",
      "risk_score": 12,
      "clinical_findings": [
        "High dietary fiber density (10.6g/100g) supports glycemic moderation (ADA 2024)",
        "Low sodium content (5mg/100g) fully complies with hypertension guidelines (AHA 2023)"
      ],
      "allergen_conflicts": [],
      "uncertainty_notices": []
    },
    {
      "member_id": "fam_002",
      "member_name": "Ananya",
      "guidance": "REGULAR",
      "risk_level": "LOW",
      "risk_score": 5,
      "clinical_findings": [
        "Minimal sugar content (1.0g/100g) complies with pediatric sugar standards (AAP / WHO)"
      ],
      "allergen_conflicts": [],
      "uncertainty_notices": []
    }
  ],
  "confidence_profile": {
    "data_completeness_pct": 100.0,
    "evidence_applicability": "HIGH",
    "medical_certainty_disclaimer": "Informational dietary decision support only; does not replace licensed medical or clinical advice."
  }
}
```

---

## 3. Error Codes & Validation Handling

| HTTP Status | Error Type | Scenario | Example Response Payload |
|:---:|:---|:---|---|
| `400 Bad Request` | Missing Product Data | Request omitted `product` object | `{"error": "product payload is required"}` |
| `400 Bad Request` | Missing Family Data | `family_members` list is empty | `{"error": "at least one family member profile is required"}` |
| `400 Bad Request` | Invalid Nutrition Types | Calories or sugars passed as strings | `{"error": "sugars must be a numeric value"}` |
| `405 Method Not Allowed` | Wrong HTTP Method | `GET` sent to `/api/v2/recommend/` | `{"detail": "Method \"GET\" not allowed."}` |
| `500 Server Error` | Unhandled Processing Error | Unexpected parsing failure | `{"error": "Internal processing error", "source": "SERVER_ERROR"}` |
