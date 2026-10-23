# Contributing to HealthSense AI

Thank you for your interest in **HealthSense AI**! This project was developed as an **MCA Mini Project** focusing on intelligent food-health decision support through a decoupled Android application and Django machine learning backend.

While this repository is primarily an academic portfolio project, constructive contributions, bug reports, and discussions are welcome.

---

## 🧭 Code of Conduct

All contributors and participants are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful, professional, and constructive.

---

## 🛠️ How to Contribute

### 1. Reporting Bugs
- Before creating an issue, search the [existing issues](https://github.com/AmitChame/HealthSense-AI/issues) to verify if the bug has already been reported.
- Use our [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).
- Clearly describe:
  - Exact steps to reproduce the issue
  - Expected versus actual behavior
  - Device/OS version (e.g., Android 14, Windows 11, Ubuntu 22.04)
  - Applicable logcat snippets or backend terminal tracebacks

### 2. Suggesting Enhancements
- Check [docs/LIMITATIONS.md](docs/LIMITATIONS.md) and [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md) to understand current design decisions.
- Open an issue using our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md).
- Focus on evidence-informed nutrition improvements, offline rule enhancements, or UI/UX accessibility.

### 3. Pull Request Guidelines
1. Fork or branch from `main`.
2. Name your branch descriptively:
   - `fix/nutrient-parsing-edge-case`
   - `docs/clarify-installation-steps`
   - `feat/allergen-synonym-expansion`
3. Adhere to the established code architecture:
   - **Android**: Java MVVM architecture with Repository pattern and ViewBinding.
   - **Django Backend**: Python 3.11, PEP 8 style, decoupled two-stage rule + ML architecture.
   - **Never mix product grade with person guidance**: Product grade belongs to the product; personalized guidance belongs to the individual.
4. Verify your changes locally:
   - Run Android unit tests: `./gradlew testDebugUnitTest`
   - Run backend checks: `python manage.py check`
   - Run pytest suite: `pytest`
5. Submit a pull request referencing any relevant issue.

---

## 🧪 Scientific & Algorithmic Integrity Rules

Contributors proposing nutritional rules or ML modifications must adhere to:
1. **Traceability**: Any dietary threshold must cite an authoritative standard (e.g., WHO, Codex Alimentarius, FSSAI, AAP, EFSA, KDIGO).
2. **Missing Data Distinction**: Missing values must never be treated as zero or assumed safe.
3. **Clinical Uncertainty**: Never state or imply that the system certifies medical safety or clinical suitability.

---

## 📬 Contact & Questions

For project discussions or academic review questions, reach out to **Amit Chame** at [amitchame19@gmail.com](mailto:amitchame19@gmail.com).
