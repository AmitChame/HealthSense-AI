# HealthSense AI — Application Screenshots & Screen Guide

This directory documents the visual interface of the **HealthSense AI** native Android application. 

In strict adherence to academic and repository integrity rules, **no fabricated, synthetic, or mock screenshots are included**. All screenshots in this project must be captured directly from a real Android device or official Android Studio emulator running the verified application.

---

## 📸 Implemented Screens & Capture Guide

To capture genuine screenshots from your connected physical Android device or Android Studio emulator:
```powershell
# Capture screenshot via ADB directly from PowerShell:
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png docs/screenshots/01_dashboard.png
```

| Screen Name | Implemented Activity / Fragment | Key Visual Elements |
|---|---|---|
| **1. Splash & Auth** | `SplashActivity.java`, `LoginActivity.java` | Clean brand logo, email/password inputs, Firebase sign-in, validation states |
| **2. Home Dashboard** | `HomeFragment.java`, `MainActivity.java` | Quick barcode scan action, recent scans list, registered family members summary |
| **3. Family Management** | `FamilyListFragment.java`, `AddEditFamilyMemberActivity.java` | Multi-member card list, conditions chips, allergy selector, age/gender inputs |
| **4. Live Barcode Scanner**| `ScannerActivity.java`, `BarcodeAnalyzer.java` | Live CameraX viewfinder, bounding box target, flash toggle, fast detection overlay |
| **5. Product Nutrition** | `ProductDetailActivity.java` | Open Food Facts product image, brand, Nutri-Score badge, nutrient table per 100g |
| **6. Product Food Grade** | `RecommendationActivity.java` | Stage 1 Product Grade card (A–E), Rayner score breakdown, data completeness gauge |
| **7. Family Guidance Cards**| `RecommendationActivity.java`, `FamilyRecommendationAdapter.java` | Individual guidance cards (`REGULAR`, `OCCASIONAL`, `AVOID`), risk score badge |
| **8. Clinical Findings** | `RecommendationActivity.java` | Statutory evidence citations (WHO, ADA, AHA), allergen conflict warnings |
| **9. Scan History** | `HistoryFragment.java`, `ScanHistoryAdapter.java` | Chronological history of scanned items stored in Cloud Firestore |
| **10. Settings & Network** | `ProfileFragment.java` | Dynamic Django API URL configuration, offline mode toggle, account logout |

---

## 🖼️ Suggested Gallery Placement
Once authentic PNG images are captured and placed in this directory, they can be referenced in the main `README.md`:

```markdown
| Home Dashboard | Live Barcode Scanner | Personalized Results |
|:---:|:---:|:---:|
| ![Dashboard](docs/screenshots/01_dashboard.png) | ![Scanner](docs/screenshots/04_scanner.png) | ![Results](docs/screenshots/07_results.png) |
```
