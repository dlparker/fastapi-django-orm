from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / "subdir"
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# Settings are read from the environment. A .env file in the project root is
# loaded too, if present; real environment variables take precedence.
env = environ.Env()
if (BASE_DIR / ".env").exists():
    env.read_env(BASE_DIR / ".env")

# Overridden in production.py, which requires a real key
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Defaults to SQLite. For PostgreSQL, `pip install "psycopg[binary]"` and set
# e.g. DATABASE_URL=postgres://user:password@localhost:5432/dbname
#
# Connections are opened per request and closed at the end of it (see
# app/db.py). To reuse connections with PostgreSQL, enable Django's built-in
# pool rather than CONN_MAX_AGE:
#   DATABASES["default"]["OPTIONS"] = {"pool": True}
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app.core",
]

# Only applies to requests handled by Django (the app mounted at /d),
# not to FastAPI routes
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
        "DIRS": [],
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

# Static files are served by FastAPI at /static (see app/main.py)
STATIC_URL = "/static/"

USE_TZ = True
