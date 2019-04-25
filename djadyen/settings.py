import sys

from django.conf import settings


class _Settings(object):
    @property
    def ADYEN_HOST_URL(self):
        return getattr(settings, 'ADYEN_HOST_URL')

    @property
    def ADYEN_MERCHANT_ACCOUNT(self):
        return getattr(settings, 'ADYEN_MERCHANT_ACCOUNT')

    @property
    def ADYEN_MERCHANT_SECRET(self):
        return getattr(settings, 'ADYEN_MERCHANT_SECRET')

    @property
    def ADYEN_SKIN_CODE(self):
        return getattr(settings, 'ADYEN_SKIN_CODE')

    @property
    def ADYEN_CURRENCYCODE(self):
        return getattr(settings, 'ADYEN_CURRENCYCODE', 'EUR')

    @property
    def ADYEN_ENABLED(self):
        return getattr(settings, 'ADYEN_ENABLED', True)

    @property
    def ADYEN_NEXT_STATUS(self):
        return getattr(settings, 'ADYEN_NEXT_STATUS', 'AUTHORISED')

    @property
    def ADYEN_REFETCH_OLD_STATUS(self):
        return getattr(settings, 'ADYEN_REFETCH_OLD_STATUS', False)

    @property
    def ADYEN_SESSION_MINUTES(self):
        return getattr(settings, 'ADYEN_SESSION_MINUTES', 10)

    @property
    def ADYEN_URL(self):
        return getattr(settings, 'ADYEN_URL', 'https://test.adyen.com/')

    @property
    def ADYEN_ORDER_MODELS(self):
        return getattr(settings, 'ADYEN_ORDER_MODELS', [])

    @property
    def ADYEN_NOTIFICATION_SECRET(self):
        return getattr(settings, 'ADYEN_NOTIFICATION_SECRET', '')

    @property
    def ADYEN_HANDLE_NOTIFICATION_MINUTES_AGO(self):
        # The default is 15 minutes
        return getattr(settings, 'ADYEN_HANDLE_NOTIFICATION_MINUTES_AGO', 15)

    def __getattr__(self, name):
        return globals()[name]


# other parts of itun that you WANT to code in
# module-ish ways
sys.modules[__name__] = _Settings()
