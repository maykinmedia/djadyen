from django.conf import settings as dj_settings

DJADYEN_SERVER_KEY = getattr(dj_settings, "DJADYEN_SERVER_KEY")
DJADYEN_CLIENT_KEY = getattr(dj_settings, "DJADYEN_CLIENT_KEY")
DJADYEN_ENVIRONMENT = getattr(dj_settings, "DJADYEN_ENVIRONMENT", "test")
DJADYEN_APPNAME = getattr(dj_settings, "DJADYEN_APPNAME", "djadyen")
DJADYEN_MERCHANT_ACCOUNT = getattr(dj_settings, "DJADYEN_MERCHANT_ACCOUNT")
# DJADYEN_MERCHANT_SECRET = getattr(dj_settings, "DJADYEN_MERCHANT_SECRET")
DJADYEN_CURRENCYCODE = getattr(dj_settings, "DJADYEN_CURRENCYCODE", "EUR")
DJADYEN_REFETCH_OLD_STATUS = getattr(dj_settings, "DJADYEN_REFETCH_OLD_STATUS", False)
DJADYEN_SKIN_CODE = getattr(dj_settings, "DJADYEN_SKIN_CODE")
DJADYEN_HANDLE_NOTIFICATION_MINUTES_AGO = getattr(
    dj_settings, "DJADYEN_HANDLE_NOTIFICATION_MINUTES_AGO", 15
)
# ADYEN_URL = "https://test.adyen.com/"

DJADYEN_ORDER_MODELS = getattr(dj_settings, "DJADYEN_ORDER_MODELS")
