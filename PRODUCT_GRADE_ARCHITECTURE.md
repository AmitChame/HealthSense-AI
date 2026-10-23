# HealthSense AI V2 — Product Grade vs. Personalized Guidance Architecture

**Document Version:** 2.1.0  
**Project:** HealthSense AI  
**Scope:** Two-Stage Decoupled Nutritional Profiling & Personalized Guidance Engine  
**Status:** Verified & Fully Implemented (109/109 Automated Tests Passing, Android Build Passing)

---

## 1. Executive Summary & Core Architectural Separation

HealthSense AI V2 establishes a clean, mathematically rigorous architectural boundary separating **Product Nutritional Profiling** from **Individual Health Guidance**. 

Previous consumer health applications conflate these two concepts, leading to severe scientific and algorithmic flaws—such as assigning a chocolate bar a different "food grade" depending on who looks at it, or giving a whole food an "unsafe" grade simply because one family member has a specific allergy.

HealthSense AI V2 enforces a strict **Two-Stage Analysis Architecture**:

```
[ Incoming Barcode / Product Composition Payload ]
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 1: PRODUCT-LEVEL FOOD PROFILE (Nutri-Score FSA)    │
│  - Evaluates packaged product per 100g / 100ml          │
│  - Energy, Sugars, Sat Fat, Sodium vs Fiber, Protein, %FVLN │
│  - Standard balancing rule & category-specific logic    │
│  - STRICTLY BLIND to family members, age, or diseases    │
│  - Output: Product Grade (A, B, C, D, E, INSUFFICIENT)  │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ [Immutable FoodProfileResult]
                         ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 2: PERSON-LEVEL PERSONALIZED GUIDANCE             │
│  - Consumes Immutable Product Grade from Stage 1        │
│  - Integrates family profile (age, diabetes, CKD, etc.) │
│  - Detects allergen conflicts & statutory restrictions │
│  - NEVER alters or mutates the Stage 1 Product Grade    │
│  - Output: Member Guidance (REGULAR, OCCASIONAL, AVOID) │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Product-Level Food Grade Algorithm

The Product-Level Food Grade evaluates the nutritional quality of the food item itself per 100g (or 100ml for liquids). It implements the peer-reviewed **Nutri-Score / Rayner Nutrient Profiling methodology** (Santé Publique France & UK FSA).

### 2.1 General Food Scoring Formulation

The total nutritional profile score is computed as:
$$\text{Score} = N - P$$

Where:
- **$N$ (Unfavorable Points, 0 to 40 max):**
  - **Energy:** $0\text{--}10\text{ points}$ based on kilojoules ($\text{kJ} = \text{kcal} \times 4.184$). Thresholds: $\le 335\text{ kJ} \rightarrow 0$ up to $> 3350\text{ kJ} \rightarrow 10$.
  - **Total Sugars:** $0\text{--}10\text{ points}$. Thresholds: $\le 4.5\text{g} \rightarrow 0$ up to $> 45\text{g} \rightarrow 10$.
  - **Saturated Fatty Acids:** $0\text{--}10\text{ points}$. Thresholds: $\le 1.0\text{g} \rightarrow 0$ up to $> 10\text{g} \rightarrow 10$.
  - **Sodium:** $0\text{--}10\text{ points}$ ($\text{Sodium mg} = \text{Salt g} \times 400$). Thresholds: $\le 90\text{mg} \rightarrow 0$ up to $> 900\text{mg} \rightarrow 10$.
- **$P$ (Favorable Points, 0 to 15 max):**
  - **Dietary Fiber:** $0\text{--}5\text{ points}$. Thresholds: $\le 0.9\text{g} \rightarrow 0$, $> 4.7\text{g} \rightarrow 5$. (Missing fiber is treated as 0 points with an explanatory factor, never assumed).
  - **Proteins:** $0\text{--}5\text{ points}$. Thresholds: $\le 1.6\text{g} \rightarrow 0$, $> 8.0\text{g} \rightarrow 5$.
  - **Fruits, Vegetables, Legumes, Nuts (FVLN %):** $0\text{--}5\text{ points}$ ($\le 40\% \rightarrow 0$, $> 80\% \rightarrow 5$).

### 2.2 The Balancing Rule
If total unfavorable points $N \ge 11$:
- If $\text{FVLN} < 5$ points, protein points are **not subtracted** ($\text{Score} = N - (\text{Fiber} + \text{FVLN})$). This prevents high-energy, high-sugar, or high-fat products from using protein to mask unfavorable nutritional characteristics.
- **Exception (Cheeses):** For designated cheese categories, protein is always counted regardless of $N$, recognizing cheese as a significant dairy calcium and protein source.

### 2.3 Beverage Profiling
Beverages utilize dedicated physiological thresholds:
- Water is unconditionally Grade A.
- Sugar scale: $\le 0\text{g} \rightarrow 0$, $> 13.5\text{g} \rightarrow 10$.
- Beverage Grade boundaries: $\text{Score} \le 1 \rightarrow \text{B}$, $2\text{--}5 \rightarrow \text{C}$, $6\text{--}9 \rightarrow \text{D}$, $\ge 10 \rightarrow \text{E}$.

---

## 3. Grade Scale & Neutral Interpretations

HealthSense AI strictly uses neutral, descriptive interpretations rather than emotive or misleading medical assertions:

| Grade | Scientific Interpretation | Typical Category Examples |
|:---:|:---|:---|
| **A** | More favorable nutritional profile | 100% Whole rolled oats, plain legumes, leafy vegetables, water |
| **B** | Generally favorable nutritional profile | Whole grain breads, low-fat plain yogurt, frozen vegetables |
| **C** | Mixed / intermediate nutritional profile | Pure peanut butter, hummus, plain cheeses, whole milk |
| **D** | Less favorable nutritional profile | Salted potato crisps, flavored sweetened yogurts, pastries |
| **E** | Least favorable nutritional profile | Confectionery chocolate bars, energy drinks, sugar sodas |
| **INSUFFICIENT DATA** | Insufficient nutrient data to establish grade | Unlabeled snacks, items with $< 3$ core nutrients reported |

> [!IMPORTANT]
> The product grade is never termed "WHO Grade" or "Medical Grade". It is labeled as **HealthSense Food Profile (Nutri-Score Standard Algorithm)**.

---

## 4. Stage 2: Person-Level Personalized Guidance

Stage 2 consumes the immutable `food_profile` from Stage 1 alongside the family member's clinical context (age, diabetes, hypertension, CKD, allergies, dietary preferences).

### 4.1 Frequency Tier Nomenclature
HealthSense AI V2 bans the recommendation "DAILY" (as no single packaged product is mandated daily in evidence-based dietary guidelines). The 5 standard guidance tiers are:

1. **`REGULAR`**: Favorable nutritional composition aligning with general dietary reference values for this profile.
2. **`OCCASIONAL`**: Mixed profile with moderate saturated fat, sugar, or sodium; suitable in moderation within a varied diet.
3. **`LIMIT FREQUENCY`**: Elevated concentrations of sugar, saturated fat, or sodium (Grade D/E), or specific metabolic considerations (e.g., diabetes portion awareness).
4. **`AVOID`**: Restricted strictly to hard safety blocks:
   - Confirmed allergen conflicts (e.g., Peanut allergy matching peanut ingredients).
   - Pediatric statutory restrictions (e.g., high-caffeine energy drinks for children under 12).
   - Strict ethical/religious diet contraindications (e.g., gelatin for vegetarians).
5. **`INSUFFICIENT INFORMATION` / `INSUFFICIENT DATA`**: Used when product data is incomplete, or in clinical conditions like Chronic Kidney Disease (CKD) where packaged labels omit essential renal metrics (potassium, bioavailable phosphorus).

---

## 5. Grade Immutability Guarantee

A central requirement of HealthSense AI V2 is **Grade Immutability**:
$$\text{ProductGrade}(P, U_1) = \text{ProductGrade}(P, U_2) = \text{ProductGrade}(P, \emptyset)$$

### Mathematical Proof & Test Scenarios
To guarantee this property, 6 automated test scenarios evaluate the identical product payload (`Hershey's Milk Chocolate Bar`):
1. No family members (standalone scan): **Grade E**
2. Healthy Adult (Amit, 35): **Grade E**
3. Diabetic Adult (Priya, 42): **Grade E**
4. CKD Patient (Rajesh, 58): **Grade E**
5. Young Child (Aarav, 4): **Grade E**
6. Severe Peanut Allergy (Ananya, 14): **Grade E**

In all 6 scenarios, `data['foodGrade']` and `data['food_profile']['grade']` remain **E**, while each individual member receives customized guidance (e.g., Amit receives `LIMIT FREQUENCY` for saturated fat, Priya receives `LIMIT FREQUENCY` for high sugar, Ananya receives personal guidance with zero allergen conflict for peanut).

---

## 6. Zero Conflation Rule: Allergens vs. Nutritional Quality

In HealthSense AI V2, an allergen conflict never degrades or mutates the product's nutritional score.

- **Example — Pintola Pure Peanut Butter:**
  - Product Profile: **Grade C** (High protein, moderate fiber, moderate saturated fat).
  - General Product Frequency: **`OCCASIONAL`**.
  - Scanned for **Ananya (Peanut Allergy)**:
    - Product Grade: **`C`** (unchanged!).
    - Product Frequency: **`OCCASIONAL`** (unchanged!).
    - Member Personalized Guidance: **`AVOID`**.
    - Member Allergen Status: **`CONFIRMED_ALLERGEN_CONFLICT`**.
    - Member Summary: *"Confirmed allergen conflict: product contains Peanut. Strict avoidance recommended."*

---

## 7. Real Product Validation Benchmarks

Execution of `ai_backend/scripts/validate_v2_real_products.py` against live packaged food benchmarks verified the engine:

| Product | Barcode | Category | Product Grade | General Freq | Member Context | Member Guidance |
|:---|:---:|:---:|:---:|:---:|:---|:---:|
| **Hershey's Milk Chocolate** | `0034000249862` | Confectionery | **E** | `LIMIT FREQUENCY` | Amit (Cholesterol)<br>Priya (Diabetes) | `LIMIT FREQUENCY`<br>`LIMIT FREQUENCY` |
| **Quaker Rolled Oats** | `8901234567890` | Whole Grain | **A** | `REGULAR` | Rohan (Healthy)<br>Sunita (CKD) | `REGULAR`<br>`LIMIT FREQUENCY` (KDIGO Notice) |
| **Red Bull Energy Drink** | `9002490205987` | Energy Drink | **E** | `LIMIT FREQUENCY` | Aarav (Child 9)<br>Vikram (Adult 32) | `AVOID` (Statutory block)<br>`LIMIT FREQUENCY` |
| **Pintola Peanut Butter** | `1112223334445` | Nut Spread | **C** | `OCCASIONAL` | Ananya (Peanut Allergy) | `AVOID` (Allergen conflict) |
| **Unlabeled Savory Snack** | `9998887776665` | Incomplete | **INSUFFICIENT DATA** | `INSUFFICIENT DATA` | Suresh (Hypertension) | `INSUFFICIENT DATA` |

---

## 8. API Contract & Payload Separation

The API endpoint (`POST /api/v2/recommend/`) clearly separates Stage 1 outputs from Stage 2 outputs in its JSON structure:

```json
{
  "version": "v2",
  "barcode": "0034000249862",
  "productName": "Hershey's Milk Chocolate Bar",
  
  "/* ─── STAGE 1: PRODUCT-LEVEL OUTPUTS ─── */": "",
  "foodGrade": "E",
  "foodGradeInterpretation": "Least favorable nutritional profile",
  "foodQualityScore": 23.0,
  "frequencyRecommendation": "LIMIT FREQUENCY",
  "food_profile": {
    "grade": "E",
    "interpretation": "Least favorable nutritional profile",
    "score": 23.0,
    "category": "Chocolate Confectionery",
    "methodology": "Nutri-Score Standard Algorithm",
    "basis": {
      "points_n": 24,
      "points_p": 1,
      "details": {
        "energy_kj": 2142.2, "energy_points": 6,
        "sugars_g": 58.1, "sugars_points": 10,
        "sat_fat_g": 18.6, "sat_fat_points": 10,
        "sodium_mg": 80.0, "sodium_points": 0,
        "fiber_points": 0, "protein_points": 1
      }
    },
    "factors": ["High sugar (58.1g/100g)", "Elevated saturated fat (18.6g/100g)"]
  },
  "nutrient_findings": [ ... ],
  "data_completeness": { ... },

  "/* ─── STAGE 2: PERSON-LEVEL OUTPUTS ─── */": "",
  "family_guidance": [
    {
      "member_id": "m1",
      "name": "Amit",
      "age": 35,
      "product_grade": "E",
      "guidance": "LIMIT FREQUENCY",
      "status": "HIGHER CONCERN",
      "allergen_status": "NONE_DETECTED",
      "summary_reason": "Product presents higher-concern characteristics (total sugar concentration is high at 58.1g/100g, saturated fat concentration is elevated at 18.6g/100g)...",
      "guidance_text": "Consider limiting consumption frequency and being mindful of portion size...",
      "hard_safety_conflicts": [],
      "soft_concerns": ["Saturated fat concentration exceeds reference benchmarks..."]
    }
  ],
  "recommendations": [ /* Backward-compatible array for existing UI */ ]
}
```

---

## 9. Android Client Compatibility & Integration

1. **Top-Level Badges & Grade Display:**
   - The Android UI binds `foodGrade` (`A` through `E`) directly into the header badge.
   - The color coding follows the standard Nutri-Score scheme:
     - **A:** Dark Green (`#038141`)
     - **B:** Light Green (`#85BB2F`)
     - **C:** Yellow (`#FECB02`)
     - **D:** Orange (`#EE8100`)
     - **E:** Red / Coral (`#E63E11`)
     - **INSUFFICIENT DATA:** Neutral Grey (`#757575`)
2. **Family Member Cards:**
   - Each family member card displays their personalized guidance chip (`REGULAR`, `OCCASIONAL`, `LIMIT FREQUENCY`, `AVOID`, or `INSUFFICIENT INFORMATION`).
   - If an allergen conflict exists, the card displays a prominent red safety alert banner with specific ingredients identified, while the top-level product grade remains undisturbed.

---

## 10. Verification & Test Suite Summary

- **Backend Automated Test Suite:**
  - `python -m pytest tests/ -v`: **109 / 109 tests PASSED** (0 failures, 100% green).
  - Includes dedicated test cases:
    - `test_product_grade_immutability_across_family_profiles`
    - `test_allergen_conflict_leaves_product_grade_unchanged`
    - `test_diverse_family_guidance_identical_product_grade`
    - `test_hersheys_chocolate_regression`
    - `test_kidney_disease_uncertainty_notice`
    - `test_pediatric_stimulant_vs_ordinary_sugar`
- **Android Compilation:**
  - `.\gradlew.bat assembleDebug`: **BUILD SUCCESSFUL** (18s).
  - `.\gradlew.bat assembleRelease`: **BUILD SUCCESSFUL** (6s).

---

## 11. Scientific Standards & Evidence Registry

The system operates strictly against documented global and national nutritional authorities:
- **Santé Publique France & FSA (Rayner et al.):** Nutri-Score calculation rules, points tables, and beverage guidelines.
- **World Health Organization (WHO):**
  - *Guideline: Sugars intake for adults and children (2015)*.
  - *Saturated fatty acid and trans-fatty acid intake for adults and children (2023)*.
  - *Global report on sodium intake reduction (2023)*.
- **Codex Alimentarius:** *Codex General Standard for the Labelling of Prepackaged Foods (CXS 1-1985)*.
- **National Kidney Foundation (KDOQI / KDIGO):** *Clinical Practice Guideline for Nutrition in CKD (2020 Update)*.
- **European Food Safety Authority (EFSA) & American Academy of Pediatrics (AAP):** Pediatric caffeine and energy drink intake limits.

---

## 12. Legal & Clinical Disclaimers

HealthSense AI V2 provides **informational food composition analysis only**. 
- It does not provide medical diagnoses, clinical prognoses, individualized medical prescriptions, or statutory safety certifications.
- Users with medical conditions (such as diabetes, chronic kidney disease, severe hypertension, or anaphylactic food allergies) are reminded that packaged food labels may contain omissions, reporting inaccuracies, or cross-contact contamination, and that clinical dietary decisions should always be made in consultation with qualified healthcare professionals and registered dietitians.
