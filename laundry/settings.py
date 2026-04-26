import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-utclz(o!8y6@$1nxz$$oq3se6r0vocj-vk=!k9k1x^kb31fk53')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'expressless-unsesquipedalian-caren.ngrok-free.dev',
    'web-production-8348e.up.railway.app',
]

CSRF_TRUSTED_ORIGINS = [
    'https://web-production-8348e.up.railway.app',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    'accounts',
    'services',
    'orders',
    'payments',
    'staff',
    'pwa',
    'ussd',
]

PWA_APP_NAME = 'LAUNDRY MANAGEMENT SYSTEM'
PWA_APP_DESCRIPTION = 'A system that digitizes laundry services'
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'serviceworker.js')
PWA_APP_BACKGROUND_COLOR = 'blue'
PWA_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_DEBUG_MODE = False

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'laundry.urls'

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'laundry' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'laundry.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── M-Pesa ────────────────────────────────────────────────────────────────────
MPESA_CONSUMER_KEY    = '8wGhceuFGAfuwtSNSZNuoMUwCvadwDHKX4EZZ7q9Y307aeAk'
MPESA_CONSUMER_SECRET = 'bP0lt6Asg77ZagLdg4fEWFafCegtLJ0gTzx4pGxugG1wb64A7vzcQnzDo6r4rU63'
MPESA_SHORTCODE       = '174379'
MPESA_PASSKEY         = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
MPESA_CALLBACK_URL    = 'https://web-production-8348e.up.railway.app/payments/mpesa/callback/'
MPESA_ENV             = config("MPESA_ENV", default="sandbox")

# ── Africa's Talking SMS ──────────────────────────────────────────────────────
AT_USERNAME = config("AT_USERNAME", default="sandbox")
AT_API_KEY  = config("AT_API_KEY",  default="")

# ── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True