# HealthSense AI — Deployment & Production Guide

This document outlines the procedure for deploying the **Django AI Backend** to production cloud environments and preparing the **Android Application** for release.

---

## ☁️ Part 1: Django AI Backend Production Deployment

### 1.1 Production Environment Variables
Create a production `.env` file on your cloud host (e.g. AWS, Render, Railway, DigitalOcean):

```ini
DEBUG=False
DJANGO_SECRET_KEY=generate-a-strong-random-50-character-key
ALLOWED_HOSTS=api.yourdomain.com,your-app.onrender.com
CORS_ALLOWED_ORIGINS_LIST=https://yourdomain.com
PORT=8000
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 1.2 Running with a WSGI Production Server (Gunicorn)
Install Gunicorn and Uvicorn workers:
```bash
pip install gunicorn
```

Start the production server:
```bash
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
```

### 1.3 Containerized Deployment (Dockerfile)
A lightweight production `Dockerfile` for the backend:

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY ai_backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application source
COPY ai_backend/ /app/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health/ || exit 1

# Start Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### 1.4 Reverse Proxy (Nginx) Configuration
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📱 Part 2: Android Application Release Packaging

### 2.1 Generating a Production Keystore
Generate an Android release signing key using `keytool`:
```bash
keytool -genkey -v -keystore healthsense-release.jks \
    -alias healthsense-key -keyalg RSA -keysize 2048 -validity 10000
```
*(Store this keystore securely outside version control; never commit `.jks` files)*

### 2.2 Configuring Signing in `app/build.gradle`
Reference the keystore via environment variables or `local.properties`:

```groovy
android {
    signingConfigs {
        release {
            storeFile file(System.getenv("KEYSTORE_PATH") ?: "healthsense-release.jks")
            storePassword System.getenv("KEYSTORE_PASSWORD")
            keyAlias System.getenv("KEY_ALIAS")
            keyPassword System.getenv("KEY_PASSWORD")
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

### 2.3 Building Signed Release Artifacts
```powershell
# Assemble signed release APK:
.\gradlew.bat assembleRelease

# Build Android App Bundle (AAB) for Google Play Store:
.\gradlew.bat bundleRelease
```
Outputs:
- APK: `app/build/outputs/apk/release/app-release.apk`
- AAB: `app/build/outputs/bundle/release/app-release.aab`
