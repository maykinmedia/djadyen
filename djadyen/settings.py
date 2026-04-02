from typing import Literal

from django.conf import settings

DJADYEN_SERVER_KEY: str = ""
"""
The Adyen API key used in backend API requests. Required
https://docs.adyen.com/development-resources/api-authentication#api-key-authentication
"""

DJADYEN_CLIENT_KEY: str = ""
"""
The Adyen environment to used in frontend API requests. Required.
https://docs.adyen.com/development-resources/client-side-authentication
"""

DJADYEN_ENVIRONMENT: str = "test"
"""
The Adyen environment to use. Defaults to `test`
"""

DJADYEN_MERCHANT_ACCOUNT: str = ""
"""
Merchant account from Adyen
"""


DJADYEN_APPNAME: str = "Djadyen Payment"
"""
Django's app name for Adyen. Defaults to `Djadyen Payment`
"""


DJADYEN_CURRENCYCODE: str = "EUR"
"""
Adyen current code used in payments. Defaults to `EUR`
https://docs.adyen.com/development-resources/currency-codes#currency-codes
"""


DJADYEN_REFETCH_OLD_STATUS: bool = False
"""
Fetch the older status when updating an order.

Defaults to `False`.
"""


DJADYEN_ORDER_MODELS: list["str"] = []
"""
List of DjAdyen orders that should be handled by the webhook.
e.g. ["app.Order", "app.Donation"]
"""


DJADYEN_HANDLE_NOTIFICATION_MINUTES_AGO: int = 0
"""
Delay to handle notifications in minutes. e.g 0 is immediate, 1 is older than 1 minute.
Default is 0.
"""

DJADYEN_NOTIFICATION_KEY: str = ""
"""
HMAC signatures to verify notifications are sent by Adyen.
https://docs.adyen.com/development-resources/webhooks/verify-hmac-signatures
"""


DJADYEN_DEFAULT_COUNTRY_CODE: str = ""
"""
Default shopper's two-letter country code.
"""

DJADYEN_LIVE_URL_PREFIX: str = ""
"""
The live URL prefix from adyen required to use live payments.
https://docs.adyen.com/development-resources/live-endpoints#live-url-prefix

Defaults to empty string. Required to not be empty for live
"""


DJADYEN_STYLES: dict = {}
"""
Styles are passed to the Adyen payment component configuration.
Defaults to `{}`

Example setting:
DJADYEN_STYLES = {
    'base': {
        'color': '#000000',
        'fontSize': '16px',
        'fontFamily': 'Arial, sans-serif',
    },
    'placeholder': {
        'color': '#999999',
    },
    'error': {
        'color': '#ff0000',
    }
}
"""


# TODO: type statement after 3.11 support is dropped
SettingName = Literal[
    "DJADYEN_SERVER_KEY",
    "DJADYEN_CLIENT_KEY",
    "DJADYEN_ENVIRONMENT",
    "DJADYEN_APPNAME",
    "DJADYEN_MERCHANT_ACCOUNT",
    "DJADYEN_CURRENCYCODE",
    "DJADYEN_REFETCH_OLD_STATUS",
    "DJADYEN_HANDLE_NOTIFICATION_MINUTES_AGO",
    "DJADYEN_ORDER_MODELS",
    "DJADYEN_NOTIFICATION_KEY",
    "DJADYEN_DEFAULT_COUNTRY_CODE",
    "DJADYEN_LIVE_URL_PREFIX",
    "DJADYEN_STYLES",
]


def get_setting(name: SettingName):
    default = globals()[name]
    return getattr(settings, name, default)
