# HealthSense AI — V2 Architecture Specification
=================================================

## 1. Product Philosophy
> "HealthSense AI does not diagnose, prescribe, or determine medical safety. It analyzes available food composition and ingredient information against documented nutrition evidence and the user's recorded dietary context, then provides informational food insights with appropriate uncertainty."

The system communicates:
"Here is what the available food information suggests."
NOT:
"This food is medically safe / unsafe" or "You should eat this daily."

---

## 2. Four-Layer Evidence-Informed Architecture

```
                 PACKAGED PRODUCT (Barcode / OFF)
                               │
                               ▼
        LAYER 1: DATA COMPLETENESS & NORMALIZATION
        • Nutrient Completeness (Complete / Partial / Limited)
        • Ingredient Completeness (Complete / Partial / Missing)
        • Serving size normalization (per 100g vs per serving)
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
LAYER 1: GENERAL FOOD PROFILE         LAYER 2: EVIDENCE FINDINGS
• Transparent A-E Grade               • Authoritative Standards:
  A: More favorable profile             WHO, Codex, USDA FDC,
  B: Generally favorable profile        FSSAI, US FDA, EFSA, ADA, AHA
  C: Mixed profile                    • Free/Added Sugar vs Total Sugar
  D: Higher-concern profile           • Missing != Zero (Fiber, Sodium)
  E: Very high-concern profile        • Provenance tracking
  or INSUFFICIENT DATA                • Policy context (WHO Euro NPM)
            │                                     │
            └──────────────────┬──────────────────┘
                               │
                               ▼
                LAYER 3: PERSONAL CONTEXT
                • Age & Life Stage (Young child, Child, Adult)
                • Health Conditions (Non-medical dietary considerations)
                • KDIGO 2020 Kidney Disease Clinical Uncertainty Rule
                • Confirmed Allergen Hard Overrides (AVOID)
                • Precautionary Traces ("May contain")
                               │
                               ▼
                LAYER 4: GUIDANCE & FREQUENCY
                • Frequencies: REGULAR, OCCASIONAL, LIMIT FREQUENCY, AVOID, INSUFFICIENT DATA
                • Favorable / Considerations / Higher Concern
                • Multi-Dimensional Confidence Breakdown:
                  - Data Completeness Level
                  - Evidence Applicability
                  - Model Baseline Label
                  - Medical Certainty Disclaimer
```

---

## 3. API Versioning
- **V1 Canonical**: `POST /api/v1/recommend/` (Preserved 100% untouched for backward compatibility).
- **V2 Evidence-Informed**: `POST /api/v2/recommend/` (Provides full V2 structured payload, multi-dimensional confidence, evidence provenance, and cautious terminology).
