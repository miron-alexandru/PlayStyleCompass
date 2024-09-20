import os
import sys
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _
import dj_database_url
from google.oauth2 import service_account
from google.cloud import storage
import json

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = os.path.dirname(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

# General Settings
SECRET_KEY = str(os.getenv("SECRET_KEY"))
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "playstylecompass.onrender.com"]

# Installed Apps
INSTALLED_APPS = [
    "social_django",
    "playstyle_compass",
    "users",
    "bootstrap4",
    "django_recaptcha",
    "modeltranslation",
    "daphne",
    "rosetta",
    "tz_detect",
    "storages",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
]

# Recaptcha Settings
RECAPTCHA_PUBLIC_KEY = str(os.getenv("RECAPTCHA_PUBLIC_KEY"))
RECAPTCHA_PRIVATE_KEY = str(os.getenv("RECAPTCHA_PRIVATE_KEY"))

# GS Settings
GS_BUCKET_NAME = str(os.getenv("GS_BUCKET_NAME"))

if DEBUG:
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        os.path.join(BASE_DIR, "gcs-key.json")
    )
else:
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        "/etc/secrets/gcs-key.json"
    )

# Form Renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "tz_detect.middleware.TimezoneMiddleware",
    "users.middleware.UserTimezoneMiddleware",
]

# Authentication Backends:
AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

# Google OAuth2 Credentials:
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = str(os.getenv("GOOGLE_CLIENT_ID"))
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = str(os.getenv("GOOGLE_CLIENT_SECRET"))

# Social Authentication Settings:
SOCIAL_AUTH_URL_NAMESPACE = "social"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

# Social Authentication Pipeline Settings:
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "users.pipeline.send_email_confirmation",
)

# General Authentication Redirects:
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Locale Paths
LOCALE_PATHS = [os.path.join(BASE_DIR, "src", "locale")]

# URL Configuration
ROOT_URLCONF = "playstyle_manager.urls"

# Templates Configuration
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
                "playstyle_compass.context_processors.current_year",
            ],
        },
    },
]

# ASGI Application
ASGI_APPLICATION = "playstyle_manager.asgi.application"

CSRF_TRUSTED_ORIGINS = [
    "https://localhost",
    "https://127.0.0.1",
    "https://playstylecompass.onrender.com",
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Channel Layers
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# SendGrid Email Settings
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

# Password Reset Timeout
PASSWORD_RESET_TIMEOUT = 1800

if not DEBUG:
    # Database Configuration (PostgreSQL)
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
        "games_db": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "utils/games_data.db"),
        },
    }
else:
    # Database Configuration (SQLITE 3)
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

# Database Routers
DATABASE_ROUTERS = [
    "playstyle_compass.database_router.GameRouter",
    "playstyle_compass.database_router.ReviewRouter",
    "playstyle_compass.database_router.FranchiseRouter",
    "playstyle_compass.database_router.CharacterRouter",
    "playstyle_compass.database_router.NewsRouter",
]

# Default Auto Field
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "users.validators.validators.LowercaseValidator",
    },
    {
        "NAME": "users.validators.validators.UppercaseValidator",
    },
    {
        "NAME": "users.validators.validators.SpecialCharValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {"max_similarity": 0.7, "user_attributes": ("username", "email")},
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGES = [("en", _("English")), ("ro", _("Romanian"))]
MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
USE_I18N = True
LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Bucharest"
USE_L10N = True
USE_TZ = True

# Static and Media Files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if DEBUG:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"


# Authentication Settings
LOGIN_URL = "users:login"
