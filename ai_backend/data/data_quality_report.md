# HealthSense AI Data Quality Report

**Dataset Version:** OFF_HEALTHSENSE_v1
**Generated:** 2026-08-16 23:49:36

## Ingestion Overview
- **Raw Records Processed:** 4200
- **Unique Products (Final):** 3428
- **Duplicates Removed:** 262
- **Invalid Barcodes Removed:** 0

## Quality Filter Rejections
- **Missing Barcode:** 0
- **Insufficient Ingredients:** 283
- **Missing Energy Data:** 145
- **Missing Core Macros:** 60
- **Missing Sodium/Salt:** 22

## Feature Coverage & Missingness
| Feature | Coverage % | Missingness % |
| :--- | :---: | :---: |
| Barcode | 100.0% | 0.0% |
| Product Name | 100.0% | 0.0% |
| Ingredients | 100.0% | 0.0% |
| Energy (kcal/100g) | 100.0% | 0.0% |
| Sugars | 100.0% | 0.0% |
| Fat | 100.0% | 0.0% |
| Saturated Fat | 99.5% | 0.5% |
| Protein | 100.0% | 0.0% |
| Carbohydrates | 100.0% | 0.0% |
| Sodium (mg/100g) | 100.0% | 0.0% |
| Fiber | 77.2% | 22.8% |
| NOVA Group | 96.1% | 3.9% |
| Nutri-Score | 100.0% | 0.0% |

## Label Distribution (Unified)
- **RECOMMENDED:** 13634 (49.72%)
- **CAUTION:** 6740 (24.58%)
- **AVOID:** 7050 (25.71%)

## Distribution by Health Profile
- **General_Healthy:** {'RECOMMENDED': 2372, 'CAUTION': 1056}
- **Diabetic_Patient:** {'RECOMMENDED': 1694, 'CAUTION': 659, 'AVOID': 1075}
- **Hypertensive_Patient:** {'RECOMMENDED': 1225, 'CAUTION': 1290, 'AVOID': 913}
- **High_Cholesterol_Patient:** {'RECOMMENDED': 1368, 'CAUTION': 920, 'AVOID': 1140}
- **Peanut_Allergic:** {'RECOMMENDED': 2287, 'CAUTION': 1011, 'AVOID': 130}
- **Dairy_Allergic:** {'RECOMMENDED': 1467, 'CAUTION': 533, 'AVOID': 1428}
- **Celiac_Gluten_Allergic:** {'RECOMMENDED': 1527, 'CAUTION': 612, 'AVOID': 1289}
- **Diabetic_Hypertensive_Senior:** {'RECOMMENDED': 1694, 'CAUTION': 659, 'AVOID': 1075}
