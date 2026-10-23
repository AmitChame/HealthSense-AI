# HealthSense AI — Nutritional Profiling & Guidance Methodology

## 1. Two-Stage Decoupled Methodology

HealthSense AI V2 implements a clean, scientifically grounded two-stage methodology:

```
Packaged Food Data (per 100g)
             │
             ▼
┌──────────────────────────────────────────────────────────┐
│ STAGE 1: PRODUCT-LEVEL NUTRITIONAL PROFILE (A–E)         │
│ - Nutri-Score Rayner / FSA Nutrient Profiling Model      │
│ - Unfavorable points (Energy, Sugars, Sat Fat, Sodium)   │
│ - Favorable points (Fiber, Protein, % FVLN)              │
│ - The Balancing Rule (N >= 11 cutoff; cheese exception)  │
│ - IMMUTABLE output: Product Grade (A, B, C, D, E)        │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ STAGE 2: PERSONALIZED FAMILY GUIDANCE                    │
│ - Evaluates recorded profile (age, diabetes, CKD, etc.) │
│ - Checks allergen taxonomy (9+ classes)                  │
│ - Applies statutory public health standards (WHO, ADA)   │
│ - STAGE 1 PRODUCT GRADE REMAINS 100% UNCHANGED           │
│ - Output: Member Guidance (REGULAR, OCCASIONAL, AVOID)   │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Product-Level Food Grade (Nutri-Score Standard)

The product-level food grade evaluates the intrinsic nutritional density of the packaged food item per 100g (or 100ml for liquids).

### 2.1 Points Formulation: $\text{Score} = N - P$

#### $N$ (Unfavorable Points, 0 to 40 max):
1. **Energy Density** ($0\text{--}10\text{ pts}$): Calculated from kilojoules ($\text{kJ} = \text{kcal} \times 4.184$). Thresholds range from $\le 335\text{ kJ}$ ($0\text{ pts}$) to $> 3,350\text{ kJ}$ ($10\text{ pts}$).
2. **Total Sugars** ($0\text{--}10\text{ pts}$): $\le 4.5\text{g}/100\text{g} \rightarrow 0\text{ pts}$, stepping up to $> 45.0\text{g}/100\text{g} \rightarrow 10\text{ pts}$.
3. **Saturated Fatty Acids** ($0\text{--}10\text{ pts}$): $\le 1.0\text{g}/100\text{g} \rightarrow 0\text{ pts}$, stepping up to $> 10.0\text{g}/100\text{g} \rightarrow 10\text{ pts}$.
4. **Sodium** ($0\text{--}10\text{ pts}$): $\le 90\text{mg}/100\text{g} \rightarrow 0\text{ pts}$, stepping up to $> 900\text{mg}/100\text{g} \rightarrow 10\text{ pts}$.

#### $P$ (Favorable Points, 0 to 15 max):
1. **Dietary Fiber** ($0\text{--}5\text{ pts}$): $\le 0.9\text{g}/100\text{g} \rightarrow 0\text{ pts}$, $> 4.7\text{g}/100\text{g} \rightarrow 5\text{ pts}$.
2. **Protein** ($0\text{--}5\text{ pts}$): $\le 1.6\text{g}/100\text{g} \rightarrow 0\text{ pts}$, $> 8.0\text{g}/100\text{g} \rightarrow 5\text{ pts}$.
3. **Fruits, Vegetables, Legumes, Nuts (FVLN %)** ($0\text{--}5\text{ pts}$): $\le 40\% \rightarrow 0\text{ pts}$, $> 80\% \rightarrow 5\text{ pts}$.

### 2.2 The Balancing Rule
If total unfavorable points $N \ge 11$:
- If $\text{FVLN} < 5$ points, protein points are **not deducted** ($\text{Score} = N - (\text{Fiber} + \text{FVLN})$). This prevents ultra-processed products high in energy, sugar, or sodium from using added protein to mask unfavorable nutritional characteristics.
- **Cheese Exception**: For products identified in the cheese category, protein points are always subtracted regardless of $N$, recognizing cheese as a traditional dairy calcium and protein source.

### 2.3 Beverage Profiling
Beverages use dedicated physiological thresholds:
- Plain water is unconditionally assigned **Grade A**.
- Sugar thresholds: $\le 0\text{g} \rightarrow 0\text{ pts}$, $> 13.5\text{g}/100\text{ml} \rightarrow 10\text{ pts}$.
- Beverage Grade Scale: $\text{Score} \le 1 \rightarrow \textbf{B}$, $2\text{--}5 \rightarrow \textbf{C}$, $6\text{--}9 \rightarrow \textbf{D}$, $\ge 10 \rightarrow \textbf{E}$.

### 2.4 Grade Boundaries & Interpretations

| Grade | Final Score (General Foods) | Scientific Interpretation | Typical Examples |
|:---:|:---:|:---|:---|
| **A** | $\text{Score} \le -1$ | More favorable nutritional profile | 100% Whole rolled oats, plain lentils, raw nuts, water |
| **B** | $0 \le \text{Score} \le 2$ | Generally favorable nutritional profile | Whole-wheat bread, plain low-fat yogurt, unsweetened muesli |
| **C** | $3 \le \text{Score} \le 10$ | Mixed / intermediate nutritional profile | Peanut butter, whole milk, cheddar cheese, hummus |
| **D** | $11 \le \text{Score} \le 18$ | Higher-concern nutritional profile | Sweetened yogurts, salted potato chips, mayonnaise |
| **E** | $\text{Score} \ge 19$ | Very high-concern nutritional profile | Confectionery chocolate bars, energy drinks, sugar sodas |
| **INSUFFICIENT DATA** | N/A | Missing core nutrients; grade cannot be computed | Unlabeled packaged goods ($< 3$ core nutrients) |

---

## 3. Stage 2: Personalized Guidance Methodology

Stage 2 applies personal physiological rules to the immutable product profile:

### 3.1 Guideline Hierarchy & Hard Overrides
1. **Hard Allergen Overrides (Highest Priority)**:
   - If an ingredient matches a declared allergy (e.g. "hazelnuts" for a tree nut allergy), guidance is set to **`AVOID`** (`risk_level: CRITICAL`, `risk_score: 100`).
   - If the label has a precautionary trace warning ("may contain"), the app issues a **`Precautionary Allergen Notice`** without asserting medical safety.
2. **Pediatric Safety**:
   - Children $< 12$: Energy drinks and added caffeine trigger a contraindication advisory (**`AVOID`**).
   - Toddlers $< 5$: High sugar density triggers a pediatric sugar restriction advisory.
3. **Chronic Clinical Conditions**:
   - **Type 2 Diabetes**: Products with sugar density $> 12\text{g}/100\text{g}$ receive cautious glycemic advisories citing ADA 2024 Standards of Care.
   - **Hypertension**: Products with sodium density $> 400\text{mg}/100\text{g}$ receive sodium moderation advisories citing AHA 2023 Guidelines.
   - **Chronic Kidney Disease (CKD)**: Triggers a **mandatory clinical uncertainty notice** (KDIGO 2020), informing the patient that potassium and phosphorus are absent from standard nutrition labels.

### 3.2 Guidance Labels & Definitions
- **`REGULAR`**: Nutrient density aligns with regular inclusion within a balanced dietary pattern (does not mean "eat exclusively" or "eat without limit").
- **`OCCASIONAL`**: Mixed or higher-density profile suitable for mindful, moderate consumption.
- **`LIMIT FREQUENCY`**: Substantial presence of sugar, saturated fat, or sodium warrants infrequent consumption for this profile.
- **`AVOID`**: Direct contraindication (declared allergen, child stimulant, or critical clinical mismatch).
- **`INSUFFICIENT INFORMATION`**: Nutrition facts lack required fields to make an informed determination.

---

## 4. Sugar Semantics & Disclosure Standards

HealthSense AI strictly distinguishes sugar nomenclature:
- **Total Sugars**: All mono- and disaccharides (including naturally occurring sugars in milk and fruit).
- **Free Sugars**: Monosaccharides and disaccharides added to foods plus sugars naturally present in honey, syrups, fruit juices, and fruit juice concentrates (WHO 2015 definition).
- **Added Sugars**: Sugars added during food processing or packaging.

Where manufacturer food labels do not explicitly declare added sugars, HealthSense AI flags added sugar as **`Unknown`**, never falsely equating total sugar with added sugar.
