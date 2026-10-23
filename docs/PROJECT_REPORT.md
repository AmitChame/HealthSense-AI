# HealthSense AI — Academic Project Report & Defense Guide

**Project Title**: HealthSense AI: Intelligent Food Analysis and Personalized Dietary Guidance System  
**Academic Context**: Master of Computer Applications (MCA) Mini Project  
**Author / Developer**: Amit Chame (amitchame19@gmail.com)  
**Academic Year**: 2026  

---

## 1. Executive Summary & Abstract

Prepackaged food products represent a substantial portion of daily caloric intake in modern urban households. However, complex, small-print nutrition facts panels and obscure ingredient chemical codes (such as INS additives, sodium nitrates, and trans fats) make it exceedingly difficult for consumers to discern true nutritional quality. Furthermore, modern multi-generational families have heterogeneous, often conflicting dietary needs: an elderly member may manage hypertension requiring low sodium, an adult may manage Type 2 Diabetes requiring low glycemic impact, a child requires avoidance of stimulants and excess sugars, and another member may suffer from a life-threatening food allergy.

**HealthSense AI** addresses this challenge through a **production-grade, hybrid artificial intelligence and mobile decision-support system**. The solution combines a native Android mobile application (Java, MVVM, CameraX, Google ML Kit, Firebase) with a modular Python/Django AI backend. 

The system implements a scientifically grounded **Decoupled Two-Stage Analysis Architecture**:
- **Stage 1 (Product-Level Profiling)**: Computes an objective, peer-reviewed **Nutri-Score Rayner/FSA nutritional profile grade (A to E)** per 100g, strictly blind to consumer identities.
- **Stage 2 (Person-Level Guidance)**: Evaluates recorded family members individually against 14 international public health standards (WHO, Codex Alimentarius, FSSAI, AAP, EFSA, KDIGO, ADA, AHA), enforcing hard allergen overrides and pediatric contraindications without ever mutating the product's general grade.

---

## 2. Problem Statement & Motivation

### 2.1 The Nutritional Literacy Gap
Consumers typically spend less than 10 seconds evaluating a food product before purchase. Reading nutritional facts panels requires understanding reference daily intakes (RDIs), distinguishing sodium from salt, and deciphering technical ingredient names.

### 2.2 The Multi-Member Family Dilemma
Existing food scanning apps evaluate products on a single dimension or assign a universal score. When a family purchases food for collective consumption, a single score is inadequate:
- Whole peanut butter is nutrient-dense (Grade C) for a healthy athlete, but potentially fatal for a child with an IgE peanut allergy (`AVOID`).
- High-fiber rolled oats are beneficial for a diabetic adult, but an energy drink with taurine and caffeine is contraindicated for a 7-year-old child.

### 2.3 The Architectural Flaw in Existing Solutions
Many previous academic and commercial apps couple product scoring with user profiles—causing chocolate bars to change their fundamental grade based on who scans them. HealthSense AI resolves this through strict architectural decoupling.

---

## 3. System Architecture & Methodology

```
┌────────────────────────────────────────────────────────┐
│               Android Application Tier                 │
│  - Live Barcode Capture (CameraX + ML Kit)             │
│  - Open Food Facts API Client (JSON Ingestion)         │
│  - Cloud Firestore Family Sync (AES Encrypted)         │
│  - Client-Side HealthRuleEngine (Zero-Network Fallback)│
└───────────────────────────┬────────────────────────────┘
                            │ (HTTP REST JSON)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Python / Django Server Tier                │
│  - Stateless Computation (/api/v2/recommend/)          │
│  - Stage 1: Rayner / FSA Nutri-Score Algorithm (A–E)   │
│  - Stage 2: Statutory Evidence & Rule Engine (14 Stds) │
│  - Supporting ML Baseline: LightGBM / XGBoost          │
│  - Explainability: SHAP Feature Attribution            │
└────────────────────────────────────────────────────────┘
```

---

## 4. Technical Implementation Details

### 4.1 Android Client (Java / Android SDK 35)
- **Design Pattern**: MVVM with Repository Pattern and Reactive LiveData.
- **Barcode Scanner**: CameraX lifecycle-aware camera provider paired with Google ML Kit `BarcodeScanning.getClient()`. Operates at 30 FPS with real-time bounding box feedback.
- **Cloud Infrastructure**: Firebase Authentication (Email/Password) and Cloud Firestore with user-scoped security rules.
- **Offline Resilience**: If the Django server is unavailable, `RecommendationRepository` immediately redirects to `HealthRuleEngine.java` client-side, ensuring uninterrupted safety checks.

### 4.2 Django AI/ML Backend (Python 3.11)
- **Django Framework**: Stateless REST API built with Django 5.1 and Django REST Framework 3.17.
- **Dataset Preparation**: 4,200 raw products collected via Open Food Facts API, normalized to 3,428 unique products, evaluated across 8 health profiles to yield 27,424 observations.
- **Machine Learning Benchmark**:
  - Logistic Regression: 70.04% Accuracy, 0.6660 Macro F1
  - Random Forest: 95.39% Accuracy, 0.9480 Macro F1
  - XGBoost: 97.12% Accuracy, 0.9671 Macro F1
  - LightGBM: 97.47% Accuracy, 0.9712 Macro F1
- **SHAP Tree Explainer**: Computes top risk-contributing and protective nutrients per product instance.

---

## 5. Verification & Test Results

The system was validated through extensive automated testing:
- **Android Unit Tests**: 100% pass rate (`HealthRuleEngineTest.java`).
- **Android Gradle Builds**:
  - Debug APK: `app-debug.apk` assembled successfully in 1m 38s.
  - Release APK: `app-release-unsigned.apk` assembled successfully in 1m 06s with R8 full-mode minification.
- **Django System Check**: 0 issues identified.
- **Pytest Suite**: 106 automated tests passing across 13 test modules covering allergen regression, child safety, CKD uncertainty notices, and API contracts.

---

## 6. Viva / Project Defense Questions & Answers

**Q1: Why did you decouple the Product Grade from Family Guidance?**  
*Answer*: Because a food item has an objective physical composition per 100g. Conflating user health conditions with product composition creates mathematical inconsistency (e.g., a product grade changing based on who scans it). Decoupling keeps product profiling objective while allowing personal guidance to be completely personalized.

**Q2: What does the 97.47% LightGBM accuracy actually represent?**  
*Answer*: It measures how accurately the machine learning model learned and reproduced the programmed rule-based labels from the training dataset. It demonstrates successful algorithm fitting; it does not claim clinical trial efficacy or medical outcome validation.

**Q3: Why does Chronic Kidney Disease trigger an uncertainty notice instead of a recommendation?**  
*Answer*: Standard nutrition facts panels do not report potassium or bioavailable phosphorus additives. In advanced CKD, elevated potassium causes fatal cardiac arrhythmias. Making a suitability determination without this data would be chemically and clinically irresponsible.

**Q4: How does the app function without an internet connection?**  
*Answer*: The Android application incorporates `HealthRuleEngine.java`, a native Java implementation of deterministic safety rules. When offline, `RecommendationRepository` catches the network timeout and computes immediate client-side guidance.
