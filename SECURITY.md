# Security Policy — HealthSense AI

The HealthSense AI team takes application security, user privacy, and responsible disclosure seriously.

---

## 🔒 Supported Versions

| Version | Supported | Description |
|---|---|---|
| **V2.x (Current)** | ✅ Yes | Two-Stage Decoupled Evidence Engine & Modern Android Architecture |
| **V1.x (Legacy)** | ⚠️ Maintenance Only | Single-model heuristic endpoint (`/api/v1/recommend/`) |

---

## 🛡️ Reporting a Vulnerability

If you discover a security vulnerability or sensitive information exposure in HealthSense AI:

1. **Do NOT open a public GitHub issue.** Public disclosure exposes users and evaluators before a patch can be developed.
2. Email full vulnerability details directly to:
   - **Amit Chame**: [amitchame19@gmail.com](mailto:amitchame19@gmail.com)
3. Please include:
   - Description of the vulnerability and its potential impact
   - Step-by-step instructions or proof of concept to reproduce the issue
   - Affected component (Android application, Django API, or documentation)
4. You will receive an acknowledgment within **48 hours**. We will coordinate a remediation timeline before any public disclosure.

---

## 🔐 Security Architecture & Privacy Principles

HealthSense AI enforces strict data security and privacy boundaries:

### 1. Zero Health Information on AI Backend
- The Django AI backend operates as a **stateless computation engine**.
- Family profiles, individual health conditions, and allergen lists sent to `/api/v2/recommend/` are evaluated in memory and **never written to a backend database or persistent storage**.
- No Protected Health Information (PHI) or personal identifiers (PII) are stored on the server.

### 2. Client-Side Firebase Isolation
- User authentication and family member profiles are stored securely in **Cloud Firestore** under user-specific document paths (`users/{uid}/family_members/`).
- The Django backend does not hold or require Firebase service-account private keys to compute dietary guidance.
- Client Firebase configuration (`google-services.json`) contains only public client identifiers restricted by Android package name and SHA-1 certificate fingerprints in the Google Cloud Console.

### 3. Backend Secrets & Network Protection
- Django `SECRET_KEY` is loaded strictly from environment variables (`DJANGO_SECRET_KEY`) with an alert if run in production with defaults.
- `DEBUG=False` is enforced for production environments to eliminate stack trace exposure.
- Cross-Origin Resource Sharing (CORS) is restricted to configured domains via `CORS_ALLOWED_ORIGINS_LIST` in production mode.
- Local LAN IP addresses are never hardcoded in public repository files; dynamic configuration is provided via the Android in-app settings screen.

---

## ⚠️ Medical Safety Disclaimer

HealthSense AI provides **informational dietary guidance**, not medical diagnoses or clinical prescriptions. Software security does not replace professional medical judgment for acute, life-threatening food allergies or medical emergencies.
