# HealthSense AI — Installation & Setup Guide

This guide provides verified, step-by-step instructions to configure, build, test, and run both the **Django AI Backend** and the **Native Android Application**.

---

## 📋 Prerequisites & Tooling Requirements

| Platform / Subsystem | Requirement | Verified Version | Notes |
|---|---|---|---|
| **Operating System** | Windows 10/11, macOS, or Linux | Windows 11 / Ubuntu 22.04 | Cross-platform |
| **Python** | Python 3.10 to 3.12 | Python 3.11.9 | Required for Django AI backend |
| **Java Development Kit** | OpenJDK 17 or OpenJDK 21 | OpenJDK 21 (Android Studio JBR) | Required for Gradle builds |
| **Android Studio** | Android Studio Koala / Ladybug / Meerkat | Latest Stable | SDK Tools 35.0.0 |
| **Android SDK** | compileSdk: 35, minSdk: 24, targetSdk: 35 | SDK Platform 35 | Android 7.0 (Nougat) to 15 (Vanilla Ice Cream) |
| **Git** | Git 2.30+ | Git 2.55+ | Version control |

---

## 🐍 Part 1: Django AI/ML Backend Setup

### 1.1 Clone the Repository
```bash
git clone https://github.com/AmitChame/HealthSense-AI.git
cd HealthSense-AI
```

### 1.2 Set Up Virtual Environment

#### On Windows (PowerShell):
```powershell
# Navigate to the backend directory
cd ai_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

#### On macOS / Linux (Bash):
```bash
cd ai_backend
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.4 Environment Configuration
Copy the template configuration file:
```powershell
# Windows PowerShell:
Copy-Item .env.example .env

# Linux / macOS:
cp .env.example .env
```

For local testing on LAN or Android emulator, default settings work without modification:
```ini
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-healthsense-ai-local-dev-key-change-in-prod
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS_LIST=
PORT=8000
```

### 1.5 Run Database Migrations
HealthSense AI uses a lightweight local SQLite database for session metadata:
```bash
python manage.py migrate
```

### 1.6 Verify System Health & Automated Tests
Run the Django system check:
```bash
python manage.py check
```
*(Expected output: `System check identified no issues (0 silenced).`)*

Run the automated test suite with pytest:
```bash
pytest
```
*(Expected output: 106+ unit and regression tests passing)*

### 1.7 Start Development Server
To allow physical Android phones on your local Wi-Fi network and Android emulators to connect, bind the server to `0.0.0.0`:
```bash
python manage.py runserver 0.0.0.0:8000
```

Verify in your web browser:
- Health Check: `http://localhost:8000/api/health/`
  *(Expected JSON response: `{"status": "healthy", "service": "HealthSense AI Backend", "version": "2.0.0", ...}`)*

---

## 📱 Part 2: Native Android Application Setup

### 2.1 Open the Project in Android Studio
1. Launch **Android Studio**.
2. Select **File > Open...**
3. Navigate to the cloned repository root (`HealthSense-AI/`) and click **OK**.
4. Allow Gradle to sync the project dependencies.

### 2.2 Configure Firebase Client (`google-services.json`)
The repository includes a template file: `app/google-services.json.template`.

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Create a new Firebase project (or open an existing one).
3. Add an Android app with package name: `com.healthsenseai`.
4. Enable **Firebase Authentication** (Email/Password provider).
5. Enable **Cloud Firestore** in test mode or production with security rules.
6. Download your project's `google-services.json`.
7. Move the downloaded file into `app/google-services.json`:
   ```powershell
   # PowerShell example:
   Copy-Item app/google-services.json.template app/google-services.json
   # Replace with your actual Firebase config file
   ```

### 2.3 Configure Backend Base URL in Android App
The Android application provides **dynamic runtime URL configuration**:

| Environment | Backend URL to Configure | Notes |
|---|---|---|
| **Android Studio Emulator** | `http://10.0.2.2:8000/` | `10.0.2.2` is the special Android loopback alias to host machine `127.0.0.1` |
| **Physical Phone (Same Wi-Fi)** | `http://<YOUR-PC-IP>:8000/` | Find your IP with `ipconfig` (Windows) or `ifconfig` (macOS/Linux), e.g. `http://192.168.1.15:8000/` |
| **Production Cloud Server** | `https://api.yourdomain.com/` | Requires valid HTTPS certificate |

To change the URL in the app:
1. Open the HealthSense AI app.
2. Tap the **Profile** tab in bottom navigation.
3. Tap **FastAPI / Django Backend URL**.
4. Enter your URL (ensure it ends with a trailing slash `/`) and tap **Save**.

### 2.4 Run Android Unit Tests
In Android Studio: Right-click `app/src/test/java` and select **Run 'Tests in 'java''**.
Or from terminal:
```powershell
# Windows:
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
.\gradlew.bat testDebugUnitTest

# macOS / Linux:
./gradlew testDebugUnitTest
```

### 2.5 Build and Install Debug APK
From Android Studio: Click the green **Run 'app'** button (Shift + F10) targeting your emulator or connected device.
Or from terminal:
```powershell
# Build Debug APK:
.\gradlew.bat assembleDebug

# Output APK location:
# app/build/outputs/apk/debug/app-debug.apk

# Install directly to USB-connected device via adb:
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

---

## 🔌 Troubleshooting Common Connection Pitfalls

1. **Android Emulator cannot connect to `http://localhost:8000`**:
   - In Android emulators, `localhost` refers to the Android device itself. Always use `http://10.0.2.2:8000/` to reach your host computer.
2. **Physical phone displays "Remote analysis request FAILED"**:
   - Ensure both your PC and phone are connected to the same Wi-Fi router.
   - Verify Windows Firewall is allowing incoming connections on port 8000 (`New-NetFirewallRule -DisplayName "Django 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow`).
   - Confirm Django is running with `0.0.0.0:8000`, not `127.0.0.1:8000`.
3. **App functions without backend?**:
   - Yes! If the Django server is offline, the app seamlessly falls back to its built-in client-side `HealthRuleEngine.java`.
