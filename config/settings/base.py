"""Base settings shared by all environments."""

from pathlib import Path

import environ

# BASE_DIR points at the repository root (three levels up from this file).
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DJANGO_DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-dev-only-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # Third-party
    "easy_thumbnails",
    "simple_history",
    # Local apps
    "apps.core",
    "apps.services",
    "apps.projects",
    "apps.credentials",
    "apps.media_center",
    "apps.leads",
    "apps.dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Activates the request's language from cookie/session/Accept-Language.
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Records the logged-in user on each history record (must follow auth).
    "simple_history.middleware.HistoryRequestMiddleware",
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
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.user_roles",
                "apps.core.context_processors.site_settings",
                "apps.core.context_processors.structured_data",
                "apps.core.context_processors.cache_version",
                "apps.core.context_processors.dashboard_badges",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Dar_es_Salaam"
USE_I18N = True
USE_TZ = True

# Available languages for the public site. English is the default; Swahili
# translations live in locale/sw and fall back to English until filled in.
LANGUAGES = [
    ("en", "English"),
    ("sw", "Kiswahili"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

# The public language switcher stays hidden until the Swahili catalogue is
# actually translated (avoids shipping a toggle that just shows English).
# Flip to True (or set DJANGO_SHOW_LANGUAGE_TOGGLE=1) once locale/sw is filled.
SHOW_LANGUAGE_TOGGLE = env.bool("DJANGO_SHOW_LANGUAGE_TOGGLE", default=False)

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Cache backend. Defaults to per-process local memory (fine for a single
# worker / dev); point ``DJANGO_CACHE_URL`` at Redis or Memcached in prod for a
# shared cache. Used by the public-page fragment cache (see core.cache_version).
CACHES = {
    "default": env.cache_url(
        "DJANGO_CACHE_URL",
        default="locmemcache://dieynem-cache",
    )
}

# easy-thumbnails: responsive WebP derivatives served via <picture>/srcset.
# Derivatives are generated on first request and cached; the originals are
# never upscaled (see the responsive_image template tag). Extensions are NOT
# preserved so WebP derivatives end in .webp and serve the correct mime type.
THUMBNAIL_QUALITY = 82
THUMBNAIL_DEFAULT_OPTIONS = {"quality": THUMBNAIL_QUALITY}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication redirects
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard:overview"
LOGOUT_REDIRECT_URL = "home"

# Lead notifications
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="info@dieynem.co.tz")
LEADS_NOTIFY_EMAIL = env("LEADS_NOTIFY_EMAIL", default="info@dieynem.co.tz")
