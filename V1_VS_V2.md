# HealthSense AI — V1 vs. V2 Comparison Matrix
==============================================

| Dimension | V1 Architecture | V2 Architecture |
|---|---|---|
| **Core Philosophy** | Heuristic suitability tiers (Suitable / Caution / Avoid) | Informational nutrition analysis with documented uncertainty |
| **Medical Stance** | Could imply medical safety ("within safe thresholds", "safe daily") | Explicit non-medical disclaimer: "Does not diagnose, prescribe, or determine medical safety" |
| **Evidence Provenance** | Hardcoded cutoff values in config | Every standard has explicit ID, document, URL, population scope, and jurisdiction |
| **Missing Nutrients** | Frequently converted to 0.0 or treated as absent | Missing != zero. Missing fiber, sodium, or sugars explicitly flagged as "Unavailable" |
| **Total vs Free Sugar** | Total sugar used without qualification | Clear distinction: total sugar != free sugar != added sugar. Missing added sugars flagged as Unknown |
| **Kidney Disease** | Treated like general conditions | Strict KDIGO 2020 clinical uncertainty rule: returns "INSUFFICIENT INFORMATION" notice |
| **Food Profile Grades** | A-E described simply as grades | A: More favorable profile, B: Generally favorable, C: Mixed, D: Higher-concern, E: Very high-concern, or INSUFFICIENT DATA |
| **Frequency Guidance** | Automatically assigned "DAILY" for Grade A/B | Categories: REGULAR, OCCASIONAL, LIMIT FREQUENCY, AVOID, INSUFFICIENT DATA ("REGULAR" != "eat daily") |
| **Allergens** | Basic boolean match | Hard safety override for confirmed allergen; distinct precautionary notice for traces ("May contain") |
| **Confidence** | Single confidence float | Multi-dimensional: Data Completeness, Evidence Applicability, Model Baseline Label, Medical Certainty Disclaimer |
| **API Endpoints** | `POST /api/v1/recommend/` | `POST /api/v2/recommend/` (V1 preserved 100% for backward compatibility) |
| **Local Fallback** | Claimed "standard daily dietary guidelines" | Labeled "Offline Analysis — Limited Evidence", cautious phrasing, renal uncertainty rule |
