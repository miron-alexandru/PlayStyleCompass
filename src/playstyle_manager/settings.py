import os
import sys
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = os.path.dirname(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

# General Settings
SECRET_KEY = str(os.getenv("SECRET_KEY"))
DEBUG = True
ALLOWED_HOSTS = []

# Installed Apps
INSTALLED_APPS = [
    "playstyle_compass",
    "users",
    "bootstrap4",
    "django_recaptcha",
    "daphne",
    "rosetta",
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

# Form Renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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

# Database Configuration
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
USE_I18N = True
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_L10N = True
USE_TZ = True

# Static and Media Files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Authentication Settings
LOGIN_URL = "users:login"
