"""Django settings for the PlayStyle Compass."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Base Dir
BASE_DIR = os.path.dirname(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

SECRET_KEY = str(os.getenv("SECRET_KEY"))

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "playstyle_compass",
    "users",
    "bootstrap4",
    "captcha",
    # Default django apps.
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
]

RECAPTCHA_PUBLIC_KEY = str(os.getenv("RECAPTCHA_PUBLIC_KEY"))
RECAPTCHA_PRIVATE_KEY = str(os.getenv("RECAPTCHA_PRIVATE_KEY"))

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "playstyle_manager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "src", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "playstyle_manager.wsgi.application"

SENDGRID_SANDBOX_MODE_IN_DEBUG = False
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = str(os.getenv("SENDGRID_API_KEY"))
DEFAULT_FROM_EMAIL = str(os.getenv("DEFAULT_FROM_EMAIL"))
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_USER_CONTACT = str(os.getenv("EMAIL_USER_CONTACT"))
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True

PASSWORD_RESET_TIMEOUT = 1800

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "utils/db.sqlite3"),
    },
    "games_db": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "utils/games_data.db"),
    },
}

DATABASE_ROUTERS = ["playstyle_compass.database_router.GameRouter"]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# My settings
LOGIN_URL = "users:login"
