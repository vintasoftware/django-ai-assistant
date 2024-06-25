from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-tests"  # noqa

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
    "django_ai_assistant",
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

ROOT_URLCONF = "tests.urls"

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

# Not necessary
# WSGI_APPLICATION = "tests.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

# Speed up password hashing for tests
# https://docs.djangoproject.com/en/5.0/topics/testing/overview/#password-hashing

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
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

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# django-ai-assistant

# NOTE: set a OPENAI_API_KEY on .env.tests file at root when updating the VCRs.
AI_ASSISTANT_INIT_API_FN = "django_ai_assistant.api.views.init_api"
AI_ASSISTANT_CAN_CREATE_THREAD_FN = "django_ai_assistant.permissions.allow_all"
AI_ASSISTANT_CAN_VIEW_THREAD_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_UPDATE_THREAD_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_DELETE_THREAD_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_CREATE_MESSAGE_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_UPDATE_MESSAGE_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_DELETE_MESSAGE_FN = "django_ai_assistant.permissions.owns_thread"
AI_ASSISTANT_CAN_RUN_ASSISTANT = "django_ai_assistant.permissions.allow_all"
