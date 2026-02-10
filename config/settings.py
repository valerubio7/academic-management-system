import os
import sys
import tempfile
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =================================================================
# HELPER FUNCTIONS (DRY)
# =================================================================


def get_env_bool(key, default="False"):
    """Convert environment variable to boolean."""
    return os.getenv(key, default).lower() in ["true", "1", "yes"]


def get_env_list(key, default=""):
    """Convert comma-separated env variable to list."""
    value = os.getenv(key, default)
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def require_env(key, error_msg):
    """Require an environment variable or raise error."""
    value = os.getenv(key)
    if not value:
        raise ImproperlyConfigured(error_msg)
    return value


# =================================================================
# CORE SETTINGS
# =================================================================

SECRET_KEY = require_env(
    "SECRET_KEY",
    'SECRET_KEY environment variable is required. Generate one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"',
)

DEBUG = get_env_bool("DEBUG", "False")

ALLOWED_HOSTS = get_env_list("ALLOWED_HOSTS")
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must be set in production (DEBUG=False). "
        "Set the ALLOWED_HOSTS environment variable with your domain(s)."
    )
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users.apps.UsersConfig",
    "academics.apps.AcademicsConfig",
    "enrollments.apps.EnrollmentsConfig",
    "grading.apps.GradingConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# =================================================================
# DATABASE
# =================================================================

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.getenv("PGDATABASE", os.getenv("POSTGRES_DB")),
            "USER": os.getenv("PGUSER", os.getenv("POSTGRES_USER")),
            "PASSWORD": os.getenv("PGPASSWORD", os.getenv("POSTGRES_PASSWORD")),
            "HOST": os.getenv("PGHOST", os.getenv("DATABASE_HOST", "localhost")),
            "PORT": os.getenv("PGPORT", os.getenv("DATABASE_PORT", "5432")),
            "CONN_MAX_AGE": 600,
            "OPTIONS": {"connect_timeout": 10},
        }
    }

# =================================================================
# AUTHENTICATION
# =================================================================

AUTH_USER_MODEL = "users.CustomUser"
LOGIN_URL = "login"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =================================================================
# INTERNATIONALIZATION
# =================================================================

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =================================================================
# STATIC FILES
# =================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if "test" in sys.argv or DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =================================================================
# SECURITY SETTINGS (PRODUCTION ONLY)
# =================================================================

if not DEBUG:
    # SSL/HTTPS settings - can be disabled via environment variable
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False") == "True"
    SECURE_PROXY_SSL_HEADER = (
        ("HTTP_X_FORWARDED_PROTO", "https") if SECURE_SSL_REDIRECT else None
    )
    SECURE_HSTS_SECONDS = 31536000 if SECURE_SSL_REDIRECT else 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_SSL_REDIRECT
    SECURE_HSTS_PRELOAD = SECURE_SSL_REDIRECT
    SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
    CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = "same-origin"
    CSRF_TRUSTED_ORIGINS = get_env_list("CSRF_TRUSTED_ORIGINS")

# =================================================================
# SESSION CONFIGURATION
# =================================================================

SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_NAME = "ams_sessionid"

# =================================================================
# EMAIL CONFIGURATION
# =================================================================

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = get_env_bool("EMAIL_USE_TLS", "True")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# =================================================================
# CACHE CONFIGURATION
# =================================================================

if DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": str(BASE_DIR / "cache"),
        }
    }

# =================================================================
# LOGGING CONFIGURATION
# =================================================================

LOGS_DIR = Path(tempfile.gettempdir()) / "ams_logs" if DEBUG else BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True, mode=0o755 if not DEBUG else 0o777)

_FORMATTERS = {
    "simple": {"format": "{levelname} {asctime} {message}", "style": "{"},
    "verbose": {
        "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
        "style": "{",
    },
}

_CONSOLE_HANDLER = {
    "level": "DEBUG" if DEBUG else "INFO",
    "class": "logging.StreamHandler",
    "formatter": "simple",
}

if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _FORMATTERS,
        "handlers": {"console": _CONSOLE_HANDLER},
        "root": {"handlers": ["console"], "level": "INFO"},
        "loggers": {
            "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
            "app": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        },
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _FORMATTERS,
        "filters": {
            "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
        },
        "handlers": {
            "console": _CONSOLE_HANDLER,
            "file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(LOGS_DIR / "django.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "formatter": "verbose",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
                "filters": ["require_debug_false"],
                "formatter": "verbose",
            },
        },
        "root": {"handlers": ["console", "file"], "level": "INFO"},
        "loggers": {
            "django": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "django.request": {
                "handlers": ["file", "mail_admins"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.security": {
                "handlers": ["file", "mail_admins"],
                "level": "ERROR",
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

# =================================================================
# ADMINS
# =================================================================

ADMINS = []
MANAGERS = ADMINS
