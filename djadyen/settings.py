from django.conf import settings


ADYEN_HOST_URL = getattr(settings, 'ADYEN_HOST_URL')
ADYEN_MERCHANT_ACCOUNT = getattr(settings, 'ADYEN_MERCHANT_ACCOUNT')
ADYEN_MERCHANT_SECRET = getattr(settings, 'ADYEN_MERCHANT_SECRET')
ADYEN_SKIN_CODE = getattr(settings, 'ADYEN_SKIN_CODE')

ADYEN_CURRENCYCODE = getattr(settings, 'ADYEN_CURRENCYCODE', 'EUR')
ADYEN_ENABLED = getattr(settings, 'ADYEN_ENABLED', True)
ADYEN_NEXT_STATUS = getattr(settings, 'ADYEN_NEXT_STATUS', 'AUTHORISED')
ADYEN_REFETCH_OLD_STATUS = getattr(settings, 'ADYEN_REFETCH_OLD_STATUS', False)
ADYEN_SESSION_MINUTES = getattr(settings, 'ADYEN_SESSION_MINUTES', 10)
ADYEN_URL = getattr(settings, 'ADYEN_URL', 'https://test.adyen.com/')
