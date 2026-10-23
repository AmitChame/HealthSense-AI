# Changelog — HealthSense AI

All notable changes to the HealthSense AI project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-10-23

### Added
- **Academic Repository Professionalization**: Full multi-document architectural suite under `docs/`.
- **Root Security & Environment Configuration**: Standardized `.env.example`, `.gitignore`, `.gitattributes`, and `.editorconfig`.
- **Academic Evaluation License**: Formally documented academic evaluation terms and third-party license attributions in `LICENSE`.
- **GitHub Automation**: GitHub Actions CI workflow for backend test automation and Android lint checks.
- **Lazy Model Resolution**: Hardened `ModelRegistry` and `shap_explainer.py` to prevent optional ML DLL/AppLocker platform incompatibilities from interrupting core Django server execution.

### Changed
- Refactored `shap_explainer.py` to catch `(ImportError, OSError)` on environments where `llvmlite` is restricted by OS Application Control policies, seamlessly falling back to feature importance attribution.
- Synchronized root dependency declarations with `ai_backend/requirements.txt`.

### Verified
- Android debug build (`gradlew assembleDebug`): **BUILD SUCCESSFUL** (Generated `app-debug.apk`).
- Android release build (`gradlew assembleRelease`): **BUILD SUCCESSFUL** with R8 code/resource shrinking.
- Android unit tests (`gradlew testDebugUnitTest`): **PASSED** (100% test pass rate).
- Django system check (`python manage.py check`): **PASSED** (0 issues).
- Automated backend test suite (`pytest`): **106 PASSED** across safety rules, allergen regression, nutritional methodology, and API contracts.

---

## [2.0.0] - 2026-09-15

### Added
- **Two-Stage Decoupled Architecture**: Strictly decoupled Stage 1 (Product-Level Nutri-Score FSA Profile) from Stage 2 (Individual Family Guidance).
- **Evidence-Informed Standards Registry**: 14 formal public health standards integrated into `config/evidence_standards.yaml` (WHO, Codex Alimentarius, FSSAI, AAP, EFSA, KDIGO, ADA, AHA).
- **Mandatory Clinical Uncertainty for CKD**: Strict KDIGO 2020 compliance generating an explicit uncertainty notice for renal conditions due to missing potassium/phosphorus on food labels.
- **Trace Allergen Precautionary System**: Differentiated confirmed allergen presence (`AVOID`) from precautionary cross-contact statements (`May contain`).
- **Sugar Semantics Distinction**: Separated total sugar from free sugar and added sugar indicators.
- **Multi-Dimensional Confidence Score**: Decomposed single confidence float into Data Completeness, Evidence Applicability, and Medical Certainty indicators.
- **Backward Compatible V2 Endpoint**: Added `POST /api/v2/recommend/` while retaining `POST /api/v1/recommend/`.

### Fixed
- Fixed bug where product grades changed depending on which family member viewed the product. Product grade is now strictly immutable.
- Fixed missing nutrient handling: Missing nutrients are now flagged as `Unavailable` rather than coerced to `0.0`.

---

## [1.0.0] - 2026-08-16

### Added
- **Native Android Application**:
  - Live barcode scanning via Google ML Kit and CameraX.
  - Direct Open Food Facts REST API integration.
  - Multi-profile family management with Cloud Firestore.
  - Firebase Authentication (Email/Password registration and login).
  - Client-side offline fallback engine (`HealthRuleEngine.java`).
  - Dynamic backend URL configuration via in-app preferences.
- **Django AI/ML Backend (V1)**:
  - 4 ML classification models trained on 3,428 cleaned Open Food Facts products (27,424 observations): Logistic Regression, Random Forest, XGBoost, and LightGBM.
  - SHAP tree explanation integration for local feature attribution.
  - REST API endpoint (`POST /api/v1/recommend/` and `POST /api/analyze/`).
