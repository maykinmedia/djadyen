import logging

import Adyen

from djadyen import settings
from djadyen.constants import LIVE_URL_PREFIX_ERROR

logger = logging.getLogger("adyen")


def setup_adyen_client():
    ady = Adyen.Adyen()

    if not settings.DJADYEN_ENVIRONMENT:
        assert False, "Please provide an environment."

    if settings.DJADYEN_ENVIRONMENT == "live" and not settings.DJADYEN_LIVE_URL_PREFIX:
        assert False, LIVE_URL_PREFIX_ERROR

    # Setting global values
    ady.payment.client.platform = settings.DJADYEN_ENVIRONMENT
    ady.payment.client.xapikey = settings.DJADYEN_SERVER_KEY
    ady.payment.client.app_name = settings.DJADYEN_APPNAME
    ady.payment.client.live_endpoint_prefix = settings.DJADYEN_LIVE_URL_PREFIX

    return ady
