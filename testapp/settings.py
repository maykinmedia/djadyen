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
DJADYEN_SERVER_KEY = "test_server_key"
DJADYEN_CLIENT_KEY = "test_client_key"
DJADYEN_APPNAME = "Djadyen testapp"
DJADYEN_MERCHANT_ACCOUNT = "Djadyen_merchant_account"
DJADYEN_SKIN_CODE = "test"

# Old settings
DJADYEN_HOST_URL = "http://localhost:8000"
DJADYEN_MERCHANT_SECRET = (
    "300D38999F4D3830FADC54CAABEAC05C3E69F5DF0E3D4EF34882EAE1226F6CAF"
)
DJADYEN_NOTIFICATION_SECRET = (
    "55587C1E969D37996BEFF51BB3C2BDDDEA927D7CEBB2A6652EF4381EFC53BF4D"
)
DJADYEN_SKIN_CODE = "test"

DJADYEN_ORDER_MODELS = ["testapp.Order"]

ADYEN_CURRENCYCODE = "EUR"
ADYEN_ENABLED = False
ADYEN_NEXT_STATUS = "AUTHORISED"
ADYEN_REFETCH_OLD_STATUS = False
ADYEN_SESSION_MINUTES = 10
ADYEN_URL = "https://test.adyen.com/"
