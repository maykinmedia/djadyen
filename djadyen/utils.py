import logging

from django.core.exceptions import ImproperlyConfigured

import Adyen

from djadyen.constants import LIVE_URL_PREFIX_ERROR
from djadyen.settings import get_setting

logger = logging.getLogger("adyen")


def setup_adyen_client():
    ady = Adyen.Adyen()

    if not get_setting("DJADYEN_ENVIRONMENT"):
        raise ImproperlyConfigured("Please provide an environment.")

    if get_setting("DJADYEN_ENVIRONMENT") == "live" and not get_setting(
        "DJADYEN_LIVE_URL_PREFIX"
    ):
        raise ImproperlyConfigured(LIVE_URL_PREFIX_ERROR)

    # Setting global values
    ady.payment.client.platform = get_setting("DJADYEN_ENVIRONMENT")
    ady.payment.client.xapikey = get_setting("DJADYEN_SERVER_KEY")
    ady.payment.client.app_name = get_setting("DJADYEN_APPNAME")
    ady.payment.client.live_endpoint_prefix = get_setting("DJADYEN_LIVE_URL_PREFIX")

    return ady
