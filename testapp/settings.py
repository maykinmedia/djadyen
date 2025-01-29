import os

PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = PROJECT_DIR  # setting present in new startproject

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SITE_ID = 1

INSTALLED_APPS = [
    "djadyen",
    "testapp",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

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

ROOT_URLCONF = "testapp.urls"

DEBUG = True
SECRET_KEY = "this-is-really-not-a-secret"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

STATIC_URL = "/static/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(PROJECT_DIR, "database.db"),
    }
}

LANGUAGES = ["en"]

STATIC_URL = "/static/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

# New settings
DJADYEN_ENVIRONMENT = "test"
DJADYEN_SERVER_KEY = "test_server_key"
DJADYEN_CLIENT_KEY = "test_client_key"
DJADYEN_APPNAME = "Djadyen testapp"
DJADYEN_MERCHANT_ACCOUNT = "Djadyen_merchant_account"
DJADYEN_ORDER_MODELS = ["testapp.Order"]
DJADYEN_NOTIFICATION_KEY = (
    "3424242342353453422435626342654643645624564526436435643542364365"
)
