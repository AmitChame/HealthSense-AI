# HealthSense AI — Advanced AI/ML Backend

> **Hybrid AI Decision Support Engine for Packaged Food & Multi-Profile Health Analysis**  
> *Built with Python, Django REST Framework, Scikit-Learn, XGBoost, LightGBM, and SHAP*

---

## 🌟 Architecture Overview

The HealthSense AI Backend implements a **Hybrid AI Architecture** that combines:
1. **Deterministic Safety Rules**: Absolute hard overrides for food allergies (e.g. Peanut Allergy + Peanut Product $\rightarrow$ `AVOID`) and chronic condition thresholds.
2. **Ingredient Intelligence & NLP Engine**: Normalization, 9+ major allergen taxonomy detection, ultra-processed additive & preservative flagging, and TF-IDF feature extraction.
3. **Standalone HealthSense Food Quality Grader (A–E)**: Independent composite scoring engine combining nutrient balance, ingredient purity, and NOVA processing level.
4. **Pluggable Machine Learning Models**: Multi-class risk prediction adapters (`LogisticRegression`, `RandomForest`, `XGBoost`, `LightGBM`) under a common abstract interface (`BaseHealthSenseModel`), dynamically selected via `config/model_config.yaml`.
5. **Explainability & Reason Generation**: SHAP feature attribution + clinical explanation synthesis.

---

## 📊 Empirical Model Benchmark Results

Models were trained and evaluated on stratified multi-profile scenario splits generated from Open Food Facts data.

| Model Name | Accuracy | F1-Macro | Precision (Macro) | Recall (Macro) | Avoid Class Recall | False Negative Rate (Avoid) | ROC-AUC (OVR) | Avg Latency (ms) |
|---|---|---|---|---|---|---|---|---|
| **Logistic Regression** | 67.56% | 0.6171 | 0.6150 | 0.6253 | 50.00% | 50.00% | 0.8593 | 0.002 ms |
| **Random Forest** | 89.49% | 0.8708 | 0.8644 | 0.8781 | 80.39% | 19.61% | 0.9702 | 0.189 ms |
| **XGBoost (Active)** 🏆 | **97.54%** | **0.9720** | **0.9748** | **0.9695** | **93.14%** | **6.86%** | **0.9959** | **0.022 ms** |
| **LightGBM** | 97.32% | 0.9698 | 0.9714 | 0.9686 | 92.16% | 7.84% | 0.9957 | 0.026 ms |

> 🏆 **Selection Rationale**: **XGBoost** was empirically selected as the best model due to achieving the highest F1-Macro score (0.9720), the lowest False Negative Rate on high-risk items (6.86%), and microsecond-level inference latency (0.022 ms).

---

## ⚙️ How to Switch Active Models

To switch the active model used by the Django REST API without changing any code, edit `config/model_config.yaml`:

```yaml
# Set active to any registered model: "xgboost", "lightgbm", "random_forest", or "logistic_regression"
active: "lightgbm"
```

---

## 🚀 Running the AI Backend

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run Tests
```bash
pytest tests/
```

### 3. Start Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

> **Testing on Physical Android Devices**:  
> Running with `0.0.0.0:8000` allows physical phones on the same Wi-Fi network to connect via your computer's local LAN IP (e.g. `http://192.168.1.15:8000/`).

---

## 📡 API Endpoints

### 1. System Health & Active Model Status
- **Method**: `GET`
- **Path**: `/api/health/`
- **Response**:
```json
{
  "status": "healthy",
  "service": "HealthSense AI Recommendation Service",
  "version": "1.0.0",
  "active_model": "xgboost",
  "is_model_trained": true,
  "available_models": ["logistic_regression", "random_forest", "xgboost", "lightgbm"]
}
```

### 2. Personalized Food Analysis & Recommendation
- **Method**: `POST`
- **Path**: `/api/analyze/` (or `/api/v1/recommend/`)
- **Request Payload**:
```json
{
  "foodProduct": {
    "barcode": "5000159461122",
    "productName": "Snickers Chocolate Bar",
    "ingredients": "Sugar, peanuts, glucose syrup, skimmed milk powder, cocoa butter",
    "allergens": ["peanuts", "milk"],
    "nutriments": {
      "calories": 481.0,
      "sugars": 51.0,
      "sodium": 220.0,
      "saturatedFat": 9.5
    }
  },
  "familyMembers": [
    {
      "id": "member_1",
      "name": "Sarah",
      "age": 12,
      "allergies": ["Peanuts"],
      "healthConditions": []
    },
    {
      "id": "member_2",
      "name": "John",
      "age": 45,
      "allergies": [],
      "healthConditions": ["Diabetes (Type 2)"]
    }
  ]
}
```
- **Response Payload**:
```json
{
  "barcode": "5000159461122",
  "productName": "Snickers Chocolate Bar",
  "foodGrade": "D",
  "foodQualityScore": 38.5,
  "activeModel": "xgboost",
  "recommendations": [
    {
      "familyMemberId": "member_1",
      "familyMemberName": "Sarah",
      "category": "NOT_RECOMMENDED",
      "riskLevel": "HIGH",
      "riskScore": 100.0,
      "summaryReason": "Not recommended for Sarah. Strict Allergen Conflict: Product contains or may contain peanuts. Absolute avoidance required.",
      "warnings": ["Product contains peanuts or peanut derivatives."],
      "foodGrade": "D"
    },
    {
      "familyMemberId": "member_2",
      "familyMemberName": "John",
      "category": "NOT_RECOMMENDED",
      "riskLevel": "HIGH",
      "riskScore": 75.0,
      "summaryReason": "Not recommended for John. High Sugar for Diabetes: Sugar content (51.0g/100g) exceeds safety threshold (12.0g).",
      "foodGrade": "D"
    }
  ],
  "overallVerdict": "Grade D — High Risk for some family members. Review member warnings before consumption."
}
```
