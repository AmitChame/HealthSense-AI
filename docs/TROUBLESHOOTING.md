# HealthSense AI — Troubleshooting Guide

This guide documents verified solutions to common setup, build, and networking issues encountered across Android Studio and the Django AI backend.

---

## 📱 Android Application Issues

### Issue 1: "File google-services.json is missing"
- **Symptom**: Gradle sync or build fails with `File google-services.json is missing. The Google Services Plugin cannot function without it.`
- **Cause**: The production `google-services.json` is gitignored to protect client configurations.
- **Solution**:
  1. For quick local compiling, copy the provided template:
     ```powershell
     Copy-Item app/google-services.json.template app/google-services.json
     ```
  2. For live Firebase Authentication, download your project's `google-services.json` from the [Firebase Console](https://console.firebase.google.com/) and place it in the `app/` directory.

### Issue 2: "JAVA_HOME is not set and no 'java' command could be found"
- **Symptom**: Running `.\gradlew.bat` in Windows PowerShell produces `ERROR: JAVA_HOME is not set`.
- **Cause**: Android Studio installs its own bundled OpenJDK (JetBrains Runtime) which is not automatically added to the global system PATH.
- **Solution**:
  Set `JAVA_HOME` pointing to Android Studio's bundled runtime in your PowerShell session:
  ```powershell
  $env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
  .\gradlew.bat assembleDebug
  ```

### Issue 3: "Remote analysis request FAILED (Network/Protocol Error)"
- **Symptom**: The Android app shows "Falling back to local HealthRuleEngine" during scanning.
- **Cause**: The app cannot reach the Django backend over the network.
- **Solution**:
  1. **If using Android Emulator**: Open app **Profile > FastAPI / Django Backend URL** and set to `http://10.0.2.2:8000/`. (Do not use `localhost` or `127.0.0.1` inside an emulator).
  2. **If using Physical Phone**:
     - Ensure PC and phone are on the **same Wi-Fi network**.
     - Check your computer's IP using `ipconfig` (e.g. `192.168.1.15`).
     - Set URL in app to `http://192.168.1.15:8000/`.
     - Ensure Django is running with `python manage.py runserver 0.0.0.0:8000`.
     - Allow inbound connections on port 8000 in Windows Firewall:
       ```powershell
       New-NetFirewallRule -DisplayName "Django 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
       ```

### Issue 4: Camera Preview is Blank or Crashes
- **Symptom**: `ScannerActivity` does not display camera feed.
- **Cause**: Runtime Camera permission not granted.
- **Solution**: On your Android device, go to **Settings > Apps > HealthSense AI > Permissions > Camera** and select **Allow only while using the app**.

---

## 🐍 Django AI Backend Issues

### Issue 5: "DLL load failed while importing _loss: An Application Control policy has blocked this file"
- **Symptom**: Importing `sklearn.linear_model` or `sklearn.ensemble` fails on Windows with WinError 4551.
- **Cause**: Windows Application Control (AppLocker or WDAC) blocks Cython dynamic link libraries in user `AppData` directories.
- **Solution**:
  - The HealthSense AI backend incorporates **lazy model resolution** in `ModelRegistry` and defensive import handling in `shap_explainer.py`.
  - The default active model (`LightGBM`) and `XGBoost` do not depend on this blocked DLL and execute cleanly.
  - To run scikit-learn models locally, either whitelist Python DLLs in your Windows AppLocker policy, run in a Linux container (Docker/WSL2), or deploy to a standard Linux CI/cloud runner.

### Issue 6: "DisallowedHost at /api/v2/recommend/"
- **Symptom**: Django returns HTTP 400 Bad Request with `Invalid HTTP_HOST header`.
- **Cause**: `ALLOWED_HOSTS` in `.env` does not include the incoming IP address or domain.
- **Solution**: For local LAN testing, ensure `ALLOWED_HOSTS=*` in `ai_backend/.env`.

---

## 🌐 Open Food Facts Integration Issues

### Issue 7: "Product not found in Open Food Facts"
- **Symptom**: Scanned barcode displays `Product Not Found`.
- **Cause**: Open Food Facts is a community database and may not have every regional barcode indexed.
- **Solution**:
  - Test with widely distributed global barcodes:
    - Nutella: `3017620422003`
    - Coca-Cola: `5449000000996`
    - Quaker Oats: `8901030932456`
    - Barilla Pasta: `8076800195057`
