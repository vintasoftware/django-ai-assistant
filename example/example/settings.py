import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-3(fj*=+t(_645f4-)h&e=%jgmx_@bf=h5x3gq&983+@*ke)u%^"  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "webpack_loader",
    "django_ai_assistant",
    "demo",  # contains the views
    "weather",
    "movies",
    "rag",
    "issue_tracker",
    "tour_guide",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "example.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            # Necessary to avoid "OperationalError: database is locked" errors
            # on parallel tool calling:
            "init_command": "PRAGMA journal_mode=WAL;",
            "transaction_mode": "IMMEDIATE",
            "timeout": 20,
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = (BASE_DIR / "assets",)

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(levelname)-8s [%(asctime)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django_ai_assistant": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        # Log OpenAI API requests:
        "openai": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}

# django-webpack-loader

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "webpack_bundles/",
        "CACHE": not DEBUG,
        "STATS_FILE": BASE_DIR / "webpack-stats.json",
        "POLL_INTERVAL": 0.1,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    }
}


# django-ai-assistant

AI_ASSISTANT_INIT_API_FN = "django_ai_assistant.api.views.init_api"
AI_ASSISTANT_CAN_CREATE_THREAD_FN = "django_ai_assistant.permissions.allow_all"
AI_ASSISTANT_CAN_VIEW_THREAD_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_UPDATE_THREAD_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_DELETE_THREAD_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_CREATE_MESSAGE_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_UPDATE_MESSAGE_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_DELETE_MESSAGE_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_RUN_ASSISTANT = "django_ai_assistant.permissions.allow_all"


# Example specific settings:

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # get for free at https://www.weatherapi.com/
JINA_API_KEY = os.getenv("JINA_API_KEY")  # get for free at https://jina.ai/
BRAVE_SEARCH_API_KEY = os.getenv(
    "BRAVE_SEARCH_API_KEY"
)  # get for free at https://brave.com/search/api/
DJANGO_DOCS_BRANCH = "stable/5.0.x"
