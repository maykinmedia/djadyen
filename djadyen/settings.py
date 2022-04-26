import sys

from django.conf import settings as dj_settings

DJADYEN_SERVER_KEY = getattr(
    dj_settings,
    "DJADYEN_SERVER_KEY",
    "AQE1hmfxKYnGYhNBw0m/n3Q5qf3VZopZGIFLeXdCz2uGn2FCjdNkEcCgSFvtVBqr0UeIJcQ7SXwQwV1bDb7kfNy1WIxIIkxgBw==-HI5Mbes1zzL4CULcJvoTw56Ro4dE5Sjj3/F4cqkb8+4=-VYB,}T8bfN#Vt&H}",
)
DJADYEN_CLIENT_KEY = getattr(
    dj_settings, "DJADYEN_CLIENT_KEY", "test_TAWAPT2EKBBTJIXH5NWY2JVZEUOOSA3A"
)
DJADYEN_ENVIRONMENT = getattr(dj_settings, "DJADYEN_ENVIRONMENT", "test")
DJADYEN_APPNAME = getattr(dj_settings, "DJADYEN_APPNAME", "test")
DJADYEN_MERCHANT_ACCOUNT = getattr(
    dj_settings, "DJADYEN_MERCHANT_ACCOUNT", "Artis_Dagtickets"
)
DJADYEN_CURRENCYCODE = getattr(dj_settings, "DJADYEN_CURRENCYCODE", "EUR")
DJADYEN_REFETCH_OLD_STATUS = getattr(dj_settings, "DJADYEN_REFETCH_OLD_STATUS", False)

# @property
# def ADYEN_HOST_URL(self):
#     return getattr(dj_settings, 'ADYEN_HOST_URL')

# @property
# def ADYEN_MERCHANT_SECRET(self):
#     return getattr(dj_settings, 'ADYEN_MERCHANT_SECRET')

# @property
# def ADYEN_SKIN_CODE(self):
#     return getattr(dj_settings, 'ADYEN_SKIN_CODE')

# @property
# def ADYEN_ENABLED(self):
#     return getattr(dj_settings, 'ADYEN_ENABLED', True)

# @property
# def ADYEN_NEXT_STATUS(self):
#     return getattr(dj_settings, 'ADYEN_NEXT_STATUS', 'AUTHORISED')

# @property
# def ADYEN_REFETCH_OLD_STATUS(self):
#     return getattr(dj_settings, 'ADYEN_REFETCH_OLD_STATUS', False)

# @property
# def ADYEN_SESSION_MINUTES(self):
#     return getattr(dj_settings, 'ADYEN_SESSION_MINUTES', 10)

# @property
# def ADYEN_URL(self):
#     return getattr(dj_settings, 'ADYEN_URL', 'https://test.adyen.com/')

# @property
# def ADYEN_ORDER_MODELS(self):
#     return getattr(dj_settings, 'ADYEN_ORDER_MODELS', [])

# @property
# def ADYEN_NOTIFICATION_SECRET(self):
#     return getattr(dj_settings, 'ADYEN_NOTIFICATION_SECRET', '')

# @property
# def ADYEN_HANDLE_NOTIFICATION_MINUTES_AGO(self):
#     # The default is 15 minutes
#     return getattr(dj_settings, 'ADYEN_HANDLE_NOTIFICATION_MINUTES_AGO', 15)
