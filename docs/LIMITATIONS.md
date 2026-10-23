# HealthSense AI — Limitations, Risks & Clinical Disclosures

**Status**: Required Disclosure & Transparency Statement  
**Audience**: Users, Clinical Evaluators, Academic Reviewers, and Developers  

---

## 1. Regulatory Status & Non-Medical Device Declaration

> [!WARNING]
> **HealthSense AI is NOT a Certified Medical Device.**
> It is an academic prototype and informational dietary decision-support tool. It has not undergone formal regulatory clearance (such as FDA 510(k), CE mark under EU MDR, or CDSCO medical device registration) as Software as a Medical Device (SaMD).

HealthSense AI does NOT:
- Diagnose diseases, metabolic syndromes, or inborn errors of metabolism.
- Prescribe medical nutrition therapy or personalized therapeutic diets.
- Guarantee clinical safety of any food item for individuals with acute, life-threatening conditions.

---

## 2. Specific Clinical & Nutritional Limitations

### 2.1 Chronic Kidney Disease (Renal Diet Restrictions)
Standard mandatory nutrition facts panels in almost all global jurisdictions (including US FDA, EU Regulation 1169/2011, and FSSAI) **do NOT mandate declaration of potassium or bioavailable phosphorus additives**.

Because elevated serum potassium (hyperkalemia) and phosphorus can induce life-threatening cardiac arrhythmias and vascular calcification in advanced CKD patients, digital packaging data is **legally, chemically, and clinically INSUFFICIENT** to evaluate renal suitability. 
- **HealthSense AI Behavior**: Strictly returns an **explicit clinical uncertainty notice** (KDIGO 2020) instructing patients to consult their nephrologist or renal dietitian.

### 2.2 Anaphylactic & Severe Food Allergies
1. **Hidden Ingredients**: Food labels often group processing aids, spice mixes, or natural flavorings under generalized terms.
2. **Cross-Contact & Shared Facility Lines**: Statements like "packaged in a facility that also handles peanuts" are voluntary in many countries.
3. **Reformulation Lag**: Manufacturers frequently alter product formulations and production lines without immediately reflecting changes on crowdsourced databases.
- **HealthSense AI Behavior**: Confirmed allergen matches trigger an immediate hard-stop `AVOID`. However, users with severe IgE-mediated allergies must physically inspect the physical package before consumption.

### 2.3 Sugar Semantics (Total Sugars vs. Added/Free Sugars)
1. In many regions, food labeling regulations only mandate **Total Sugars** (which aggregates natural lactose from milk and fructose from fruit with refined sugars).
2. HealthSense AI V2 does not artificially guess or infer added sugars when omitted from the label, flagging added sugar status as **`Unknown`**.

### 2.4 Serving Size Standardization Discrepancies
Nutritional profiles are calculated per **100g (or 100ml)** to ensure objective comparability under the Nutri-Score Rayner model. However, actual consumer portion sizes vary widely (e.g., a single chocolate bar may be 30g, while a meal bowl may be 400g).

### 2.5 Crowdsourced Database Variance (Open Food Facts)
Open Food Facts relies on community contributions via OCR camera uploads. While barcode records are vetted by community moderators, errors such as misread decimal points (e.g. 10g read as 1.0g) or outdated formulations can occur.

---

## 3. Safe Usage Recommendations

1. Use HealthSense AI as an educational companion to improve nutritional awareness and understand food labels.
2. For severe medical conditions, chronic illnesses, or pregnancy dietary needs, always defer to a licensed physician or registered dietitian.
3. In case of discrepancies between app recommendations and the physical package label, **always trust the physical product package**.
