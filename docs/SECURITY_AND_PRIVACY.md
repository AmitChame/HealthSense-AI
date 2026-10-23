# HealthSense AI — Security & Privacy Architecture

## 1. Core Privacy Philosophy & Data Minimization

HealthSense AI is engineered with a strict **Privacy-by-Design** and **Data Minimization** philosophy in alignment with international privacy standards (GDPR Article 5 and HIPAA Privacy Rule principles).

> **Core Principle: The AI Backend is a Stateless Computation Engine.**
> No user account data, personal medical histories, or family member profiles are stored, logged to disk, or persisted in the backend database.

```mermaid
graph TD
    User([Mobile User]) -->|1. Email/Password Auth| FirebaseAuth[Firebase Authentication]
    User -->|2. Encrypted TLS Sync| Firestore[(Cloud Firestore)]
    
    subgraph ClientDevice ["User Device (Local Sandbox)"]
        Firestore -.->|User-isolated document path| LocalCache[App SQLite / Preferences]
        LocalCache --> PayloadAssembler[Payload Assembler]
    end

    subgraph BackendHost ["Django AI Backend (Stateless Cloud)"]
        PayloadAssembler -->|3. POST /api/v2/recommend/ (Transient In-Memory)| MemoryOnly[In-Memory Nutrition & Rule Engine]
        MemoryOnly --> EvaluationResult[Evaluation Result JSON]
        MemoryOnly -.->|Zero PHI Written to Disk| NoDB[(No User DB)]
    end

    EvaluationResult -->|4. Return Guidance| User
```

---

## 2. Security Tier Breakdown

### 2.1 Backend Tier Security (`ai_backend/`)
1. **Stateless Request Processing**:
   - The Django API receives the product composition and family context in memory, computes nutritional findings and rule evaluations, and returns the response payload.
   - Once the HTTP response is serialized, all personal attributes are garbage collected.
2. **Environment-Driven Configuration**:
   - `SECRET_KEY`: Loaded strictly via `os.environ.get('DJANGO_SECRET_KEY')`. If `DEBUG=False` and the default key is detected, Django issues an immediate `RuntimeWarning`.
   - `DEBUG`: Must be set to `False` in production to prevent stack trace or path exposure on unhandled exceptions.
   - `ALLOWED_HOSTS`: Explicitly white-listed in production.
   - `CORS Protection`: In development, all origins are permitted to facilitate LAN and emulator testing; in production, `CORS_ALLOWED_ORIGINS_LIST` strictly limits requests to trusted domains.
3. **Database Isolation**:
   - The backend `db.sqlite3` contains zero user tables or medical records (`Users count: 0`). It is used solely for standard Django framework migrations.

### 2.2 Client Tier Security (Android Application)
1. **Firebase Authentication**:
   - User identity is managed using Firebase Authentication with industry-standard bcrypt/scrypt password hashing managed by Google Cloud identity infrastructure.
   - Passwords are never transmitted to or processed by the Django AI backend.
2. **Cloud Firestore Rules & User Isolation**:
   - Family member profiles are saved under user-scoped paths:
     ```
     /users/{userId}/family_members/{memberId}
     ```
   - Firestore security rules restrict read and write access strictly to authenticated requests matching the document owner's `request.auth.uid`.
3. **Client Configuration (`google-services.json`)**:
   - The `google-services.json` file in Android contains **public client configuration keys**, not server private keys.
   - In Google Cloud Console, the associated API key is locked by **Android package name (`com.healthsenseai`)** and **SHA-1 certificate fingerprint**.
   - No Firebase Admin SDK private keys or service-account credentials are built into the client application.

---

## 3. Threat Modeling & Safeguards

| Threat Vector | Potential Impact | HealthSense AI Mitigation |
|---|---|---|
| **Server Compromise** | Exposure of user medical conditions | **Zero data at rest**: Backend stores no personal records. |
| **Man-in-the-Middle (MitM)** | Interception of nutritional queries | HTTPS / TLS 1.3 encryption required for production deployments. |
| **Tampered Product Barcode** | Misleading nutritional grading | Rayner/FSA scoring engine validates nutrient plausibility ($0 \le \text{nutrient} \le 100\text{g}$). |
| **Reversed Release APK** | Extraction of internal logic or DTOs | **R8 ProGuard Obfuscation** enabled in release builds (`minifyEnabled true`, `shrinkResources true`). |
| **Offline Denial of Service** | Application unable to advise user | **Client-side HealthRuleEngine** operates locally without network access. |

---

## 4. Medical Liability & Safe Product Disclosures

- HealthSense AI provides informational dietary support and cannot replace licensed medical diagnosis or prescription.
- Severe food allergy advisories (`AVOID`) are backed by deterministic code rules, but users with life-threatening allergies are explicitly instructed to physically inspect product packaging.
- Chronic kidney disease profiles receive an automatic uncertainty advisory disclosing that standard nutrition facts panels omit potassium and bioavailable phosphorus.
