# HealthSense AI — System Architecture Specification

## 1. Architectural Philosophy & Core Decoupling

The fundamental principle governing **HealthSense AI** is the **Decoupled Two-Stage Analysis Paradigm**:

> **Product grade belongs to the product; personalized guidance belongs to the person.**

A food product has an intrinsic, objective nutritional composition per 100g or 100ml. An individual consumer has personal physiological characteristics (age, life-stage, clinical conditions, allergen sensitivities, ethical dietary preferences). 

HealthSense AI strictly enforces that an individual's personal dietary conflict (such as a peanut allergy or diabetic sugar restriction) **never alters or mutates the product's general nutritional profile grade**. A whole-grain granola bar does not cease to be a nutrient-dense food simply because a peanut-allergic person must avoid it; rather, the product grade remains favorable while the allergic person receives an explicit `AVOID` advisory.

---

## 2. High-Level System Architecture

The system consists of two loosely coupled sub-systems:
1. **Client Tier**: Native Android Application (Java, MVVM, Material 3, ViewBinding, CameraX, ML Kit, Firebase Auth, Cloud Firestore).
2. **Server Tier**: Python / Django REST Backend (`ai_backend/`), integrating a deterministic rule engine, evidence registry, feature extraction pipeline, pluggable scikit-learn / XGBoost / LightGBM models, and SHAP explainability.

```mermaid
graph TD
    subgraph Client ["Android Client Tier (Java / MVVM)"]
        UI[Material 3 Activities & Fragments] --> VM[Android ViewModels]
        VM --> Repo[Repositories Pattern]
        Scanner[CameraX + Google ML Kit Barcode Scanner] --> VM
        Repo --> OFF[Open Food Facts REST API]
        Repo --> Firestore[(Cloud Firestore - Family Profiles)]
        Repo --> LocalRule[Local HealthRuleEngine Fallback]
    end

    subgraph Transport ["REST API Protocol"]
        Repo -- "POST /api/v2/recommend/ (HTTP JSON)" --> DRF[Django REST Framework]
    end

    subgraph Backend ["Server Tier (ai_backend / Python 3.11)"]
        DRF --> V2View[AnalyzeFoodViewV2]
        
        subgraph Stage1 ["Stage 1: Product-Level Food Profiling"]
            V2View --> Grader[HealthSense Food Grader]
            Grader --> NutriScore[Nutri-Score FSA Algorithm]
            Grader --> Norm[Ingredient Normalizer]
            Grader --> FVLN[FVLN % & Balancing Rule Engine]
            NutriScore --> ProfileResult["Immutable Product Profile (A–E)"]
        end

        subgraph Stage2 ["Stage 2: Personalized Guidance Engine"]
            V2View --> RuleEngine[HealthSense Rule Engine]
            ProfileResult --> RuleEngine
            RuleEngine --> AllergenDet[Allergen Taxonomy Engine (9+ Classes)]
            RuleEngine --> ConcernDet[Additive & Concern Detector]
            RuleEngine --> LifeStage[Life Stage Boundary Engine]
            RuleEngine --> CKD[KDIGO Clinical Uncertainty Engine]
            RuleEngine --> Standards[(Evidence Standards Registry - 14 Standards)]
        end

        subgraph ML ["Supporting ML & Explainability Tier"]
            V2View -.-> ModelFactory[Model Factory & Registry]
            ModelFactory --> ActiveModel[LightGBM / XGBoost Baseline]
            ActiveModel --> SHAP[SHAP Feature Attribution / Fallback]
        end

        RuleEngine --> ResponseAssembler[Response Builder]
        SHAP --> ResponseAssembler
        ProfileResult --> ResponseAssembler
    end

    ResponseAssembler --> Transport
```

---

## 3. Subsystem Detailed Responsibilities

### 3.1 Client Tier (Android Application)
- **Namespace**: `com.healthsenseai`
- **Architecture**: MVVM with Repository Pattern and Reactive LiveData.
- **Key Modules**:
  - `ScannerActivity` & `BarcodeAnalyzer`: High-speed live scanning using Android CameraX and Google ML Kit Barcode Scanning.
  - `FoodProductRepository`: Direct retrieval of packaging, ingredient lists, and nutritional facts from Open Food Facts API (`https://world.openfoodfacts.org/api/v2/product/{barcode}.json`).
  - `FamilyRepository`: CRUD operations for family member profiles stored in user-isolated Cloud Firestore collections (`users/{userId}/family_members`).
  - `RecommendationRepository`: Hybrid execution orchestrator. Dispatches requests to the Django backend (`/api/v2/recommend/`). If the remote backend is unreachable, times out, or offline mode is toggled, it automatically triggers the client-side `HealthRuleEngine` fallback with zero disruption to the user experience.
  - `AppPreferences`: Dynamic runtime configuration of the backend base URL (allowing seamless switching between Android emulator `10.0.2.2`, physical LAN IP, or production cloud domain).

### 3.2 Server Tier (Django AI/ML Backend)
- **Django Configuration**: `ai_backend/config/settings.py` (environment-aware, CORS configurable, stateless).
- **Core Processing Modules**:
  - `HealthSenseFoodGrader` (`src/features/food_grader.py`): Computes Rayner/FSA nutritional points (Energy, Sugars, Sat Fat, Sodium vs. Fiber, Protein, FVLN) per 100g, enforcing the FSA balancing rule ($N \ge 11$ cutoff).
  - `IngredientNormalizer` (`src/ingredient_engine/normalizer.py`): Strips noise, OCR artifacts, brackets, and percentage tags from crowdsourced ingredient text.
  - `AllergenDetector` (`src/ingredient_engine/allergen_detector.py`): Multi-lingual taxonomy matching for major allergens (peanuts, tree nuts, milk/dairy, gluten/wheat, egg, soy, fish, shellfish, sesame, mustard, sulfites). Differentiates confirmed ingredients from trace statements ("may contain").
  - `HealthSenseRuleEngine` (`src/rules/rule_engine.py`): Applies statutory health standards, pediatric restrictions, glycemic caution, and hard allergen overrides.
  - `ModelFactory` & `ModelRegistry` (`src/models/`): Lazy resolution of scikit-learn, XGBoost, and LightGBM models trained on the V1 benchmark dataset.
  - `HealthSenseShapExplainer` (`src/explainability/shap_explainer.py`): Generates local feature contributions (top risk and protective factors), falling back gracefully to model feature importances when SHAP tree explainer is unavailable.

---

## 4. Component Interface Contract

The contract between Android and Django is defined by the following immutable JSON structure:

### Request Contract (`POST /api/v2/recommend/`):
```json
{
  "product": {
    "barcode": "3017620422003",
    "product_name": "Nutella Hazelnut Spread",
    "brand": "Ferrero",
    "categories": "Spreads, Breakfasts, Cocoa and hazelnuts spreads",
    "ingredients": "Sugar, palm oil, hazelnuts (13%), skimmed milk powder (8.7%), fat-reduced cocoa (7.4%), emulsifier: lecithins (soya), vanillin",
    "allergens": ["nuts", "milk", "soybeans"],
    "nutriments": {
      "calories": 539.0,
      "sugars": 56.3,
      "sodium": 42.0,
      "fat": 30.9,
      "saturated_fat": 10.6,
      "carbohydrates": 57.5,
      "protein": 6.3,
      "fiber": 3.0
    }
  },
  "family_members": [
    {
      "id": "member_diabetic_01",
      "name": "Alex",
      "age": 48,
      "gender": "Male",
      "health_conditions": ["Diabetes (Type 2)"],
      "allergies": [],
      "dietary_preferences": ["None"]
    },
    {
      "id": "member_nut_allergy_02",
      "name": "Maya",
      "age": 10,
      "gender": "Female",
      "health_conditions": [],
      "allergies": ["Tree Nuts"],
      "dietary_preferences": ["Vegetarian"]
    }
  ]
}
```

### Response Contract:
```json
{
  "barcode": "3017620422003",
  "product_name": "Nutella Hazelnut Spread",
  "source": "REMOTE_BACKEND",
  "food_profile": {
    "grade": "E",
    "score": 26,
    "scientific_interpretation": "Least favorable nutritional profile",
    "points_unfavorable": 28,
    "points_favorable": 2,
    "category_applied": "general_food",
    "is_beverage": false,
    "data_sufficiency": "SUFFICIENT"
  },
  "family_recommendations": [
    {
      "member_id": "member_diabetic_01",
      "member_name": "Alex",
      "guidance": "LIMIT FREQUENCY",
      "risk_level": "HIGH",
      "risk_score": 82,
      "clinical_findings": [
        "High sugar density (56.3g/100g) exceeds diabetes cautious threshold (ADA 2024 Standards of Care)"
      ],
      "allergen_conflicts": [],
      "uncertainty_notices": []
    },
    {
      "member_id": "member_nut_allergy_02",
      "member_name": "Maya",
      "guidance": "AVOID",
      "risk_level": "CRITICAL",
      "risk_score": 100,
      "clinical_findings": [
        "HARD ALLERGEN OVERRIDE: Declared hazelnut ingredient conflicts with recorded Tree Nut allergy"
      ],
      "allergen_conflicts": ["hazelnuts"],
      "uncertainty_notices": []
    }
  ],
  "confidence_profile": {
    "data_completeness_pct": 95.0,
    "evidence_applicability": "HIGH",
    "medical_certainty_disclaimer": "Informational decision support only; not clinical medical diagnosis"
  }
}
```

---

## 5. Offline Fallback Architecture

When network access is interrupted, the Android app switches to `HealthRuleEngine.java`:
1. The repository intercepts the network exception.
2. `HealthRuleEngine.evaluate(product, familyMembers)` executes client-side deterministic rules.
3. The response payload sets `"source": "LOCAL_OFFLINE_MODE"`.
4. High-risk allergens and high-sugar/sodium rules fire client-side to ensure user safety even when disconnected.
