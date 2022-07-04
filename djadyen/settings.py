from django.conf import settings as dj_settings

DJADYEN_SERVER_KEY = getattr(dj_settings, "DJADYEN_SERVER_KEY")
DJADYEN_CLIENT_KEY = getattr(dj_settings, "DJADYEN_CLIENT_KEY")
DJADYEN_ENVIRONMENT = getattr(dj_settings, "DJADYEN_ENVIRONMENT", "test")
DJADYEN_APPNAME = getattr(dj_settings, "DJADYEN_APPNAME", "Djadyen Payment")
DJADYEN_MERCHANT_ACCOUNT = getattr(dj_settings, "DJADYEN_MERCHANT_ACCOUNT")
DJADYEN_CURRENCYCODE = getattr(dj_settings, "DJADYEN_CURRENCYCODE", "EUR")
DJADYEN_REFETCH_OLD_STATUS = getattr(dj_settings, "DJADYEN_REFETCH_OLD_STATUS", False)
DJADYEN_HANDLE_NOTIFICATION_MINUTES_AGO = getattr(
    dj_settings, "DJADYEN_HANDLE_NOTIFICATION_MINUTES_AGO", 15
)
DJADYEN_ORDER_MODELS = getattr(dj_settings, "DJADYEN_ORDER_MODELS")
