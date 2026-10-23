# HealthSense AI — Privacy Architecture & Security Notes (V2)
==============================================================

## 1. Data Minimization
- **Stateless Recommendation API**: The Django backend (`/api/v2/recommend/` and `/api/v1/recommend/`) is completely stateless. It processes food and member profile data in-memory and does NOT store user health profiles, scans, or recommendation payloads in the backend database.
- **Client Cloud Store**: Family health conditions and scan history are stored in the user's isolated Firebase Firestore path (`users/{userId}/...`). Firestore security rules ensure users can only access their own profile documents.

## 2. PII & Sensitive Health Data Protection
- **No PHI Logging**: In release builds, OkHttp logging is disabled (`minifyEnabled true`, `shrinkResources true`), ensuring sensitive health conditions and request bodies are not leaked to logcat.
- **Local Fallback Privacy**: Offline fallback mode (`HealthRuleEngine.java`) executes entirely on-device with zero network transmissions.

## 3. Network Security
- Android network security config (`network_security_config.xml`) restricts cleartext traffic. Production builds must use encrypted HTTPS endpoints.
