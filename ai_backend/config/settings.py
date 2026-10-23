"""
Django settings for HealthSense AI Backend.

Environment-aware configuration:
  - Development: DEBUG=True, ALLOWED_HOSTS=*, CORS_ALLOW_ALL_ORIGINS=True (default for LAN testing)
  - Production:  Set DEBUG=False, ALLOWED_HOSTS=<comma-separated>, CORS_ALLOWED_ORIGINS_LIST=<comma-separated>
                 via environment variables. SECRET_KEY must be set via DJANGO_SECRET_KEY env var.

Usage (LAN development):
    python manage.py runserver 0.0.0.0:8000
    (No extra env vars needed — defaults work for local LAN Android testing)

Usage (Production):
    export DEBUG=False
    export DJANGO_SECRET_KEY=<your-secret-key>
    export ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
    export CORS_ALLOWED_ORIGINS_LIST=https://yourdomain.com
    gunicorn config.wsgi:application
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Secret Key ─────────────────────────────────────────────────────────────
# SECURITY: Never commit a real secret key. Always set DJANGO_SECRET_KEY in production.
_DEFAULT_DEV_KEY = 'django-insecure-healthsense-ai-local-dev-key-change-in-prod'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', _DEFAULT_DEV_KEY)

# Warn loudly if running in production with the insecure default key
_is_insecure_key = (SECRET_KEY == _DEFAULT_DEV_KEY)

# ─── Debug Mode ──────────────────────────────────────────────────────────────
# Development default: True. Production: set DEBUG=False in environment.
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

# Warn if production key is missing in non-debug mode
if not DEBUG and _is_insecure_key:
    import warnings
    warnings.warn(
        "WARNING: Running with DEBUG=False but using the insecure default SECRET_KEY. "
        "Set DJANGO_SECRET_KEY environment variable before deploying to production.",
        RuntimeWarning,
        stacklevel=1
    )

# ─── Allowed Hosts ───────────────────────────────────────────────────────────
# Development: '*' allows LAN Android devices and emulators to connect.
# Production: Set ALLOWED_HOSTS env var to comma-separated explicit hosts.
_allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '').strip()
if _allowed_hosts_env and _allowed_hosts_env != '*':
    # Production: explicit list from environment
    ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()]
else:
    # Development / LAN testing: allow all
    ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'corsheaders',
    'rest_framework',
    # Local apps
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database (lightweight SQLite for local metadata)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── CORS Configuration ──────────────────────────────────────────────────────
# Development: CORS_ALLOW_ALL_ORIGINS=True supports Android emulators and LAN devices.
# Production: Set CORS_ALLOWED_ORIGINS_LIST env var to comma-separated allowed origins.
#             Example: https://yourapp.com,https://admin.yourapp.com
#
# IMPORTANT: CORS_ALLOW_ALL_ORIGINS=True is a development convenience only.
# It must NOT be used in production as it allows any origin to call the API.

_cors_origins_env = os.environ.get('CORS_ALLOWED_ORIGINS_LIST', '').strip()
if _cors_origins_env:
    # Production: explicit whitelist from environment
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins_env.split(',') if o.strip()]
else:
    # Development / LAN testing: allow all origins
    # This is intentional for local Android device + emulator access
    CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'UNAUTHENTICATED_USER': None,
}

# HealthSense AI Specific Config Paths
HEALTHSENSE_CONFIG_DIR = BASE_DIR / 'config'
HEALTHSENSE_ARTIFACTS_DIR = BASE_DIR / 'artifacts'
HEALTHSENSE_DATA_DIR = BASE_DIR / 'data'

