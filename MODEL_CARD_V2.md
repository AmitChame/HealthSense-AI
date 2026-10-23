# HealthSense AI — Model Card (V2)
==================================

## Model Details
- **Developer**: HealthSense AI Team (MCA Mini Project)
- **Model Version**: HealthSense V2 (Hybrid Evidence-Informed System + V1 Rule-Derived Baseline)
- **Model Type**: Multi-dimensional rule engine + LightGBM baseline generalizer
- **Release Date**: September 2026

## Intended Use
- **Primary Use**: Educational dietary decision support and informational nutrient analysis for prepackaged foods.
- **Out-of-Scope / Prohibited Use**:
  - Medical diagnosis of disease.
  - Clinical dietary prescription or medical nutrition therapy.
  - Determining clinical safety for advanced medical conditions (e.g. chronic kidney disease, inborn errors of metabolism).
  - Use as a sole decision tool for life-threatening anaphylactic food allergies.

## Label Methodology & Scientific Reality
- **V1 Baseline**: Trained on 3,428 Open Food Facts products (27,424 synthetic scenarios). Labels were generated deterministically by applying nutritional rules.
- **Metric Interpretation**: The 97.47% accuracy of the V1 LightGBM model proves that the algorithm successfully learned and interpolated the internal labeling rules. **It does NOT represent medical efficacy or clinical ground truth.**
- **V2 Evolution**: Replaces synthetic medical assertions with evidence-informed nutrient findings, multi-dimensional data completeness, and explicit clinical uncertainty.

## Quantitative Metrics (V1 Baseline)
- **Accuracy**: 97.47%
- **Macro Precision**: 97.33%
- **Macro Recall**: 96.93%
- **Macro F1**: 97.12%
- **ROC AUC**: 0.9978
- **Latency**: 0.013 ms / inference
- *Note*: Evaluated on held-out 20% stratified test split. Zero barcode leakage confirmed.

## Ethical Considerations & Bias
- **Multilingual Data**: Open Food Facts ingredient texts frequently contain French or German text. TF-IDF features may have lower density on regional Indian/English packaged goods.
- **Missing Data**: Food packaging labels frequently omit fiber, potassium, and added sugars. V2 strictly handles missing data as "Unavailable" rather than zero.
