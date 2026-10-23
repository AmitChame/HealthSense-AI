# HealthSense AI — Data Dictionary (V2)
=======================================

## 1. Food Product Fields
- `barcode`: EAN/UPC barcode string identifier.
- `productName`: Commercial name of the food product.
- `brand`: Manufacturer or brand owner.
- `ingredients`: Raw declared ingredient text.
- `servingSize`: Declared serving size (e.g. "40 g", "250 ml").
- `nutriments`:
  - `calories`: Energy density in kcal per 100g.
  - `sugars`: Total declared sugars in grams per 100g.
  - `addedSugars`: Declared added sugars in grams per 100g (or null if undeclared).
  - `sodium`: Sodium in milligrams per 100g.
  - `fats`: Total lipids in grams per 100g.
  - `saturatedFat`: Saturated fatty acids in grams per 100g.
  - `proteins`: Protein in grams per 100g.
  - `carbohydrates`: Available carbohydrates in grams per 100g.
  - `fiber`: Dietary fiber in grams per 100g (or null if undeclared).
- `allergens`: Array of tagged allergen identifiers (e.g. `["en:milk", "en:soybeans"]`).

## 2. V2 Response Schema
- `version`: Protocol version string (`"v2"`).
- `philosophy`: Core non-medical declaration string.
- `foodGrade`: Profile category (`"A"`, `"B"`, `"C"`, `"D"`, `"E"`, or `"INSUFFICIENT DATA"`).
- `foodGradeInterpretation`: Human-readable interpretation.
- `frequencyRecommendation`: Category (`"REGULAR"`, `"OCCASIONAL"`, `"LIMIT FREQUENCY"`, `"AVOID"`, `"INSUFFICIENT DATA"`).
- `data_completeness`:
  - `nutrition_data`: `"COMPLETE"`, `"PARTIAL"`, `"LIMITED"`.
  - `nutrition_coverage_pct`: Float percentage of core nutrients reported.
  - `missing_nutrients`: List of core nutrients absent from the packaging label.
  - `ingredient_data`: `"COMPLETE"`, `"PARTIAL"`, `"MISSING"`.
  - `allergen_data`: `"REPORTED"`, `"PARTIAL"`, `"UNKNOWN"`.
  - `evidence_applicability`: `"HIGH"`, `"MEDIUM"`, `"LOW"`.
- `confidence_breakdown`:
  - `data_completeness_level`: Data quality tier.
  - `evidence_applicability`: Standard applicability tier.
  - `model_confidence_label`: Rule-derived ML baseline reference.
  - `medical_certainty_disclaimer`: Mandatory non-medical advisory.
