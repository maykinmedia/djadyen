from __future__ import annotations

import logging

from django.core.exceptions import ImproperlyConfigured

import Adyen

from djadyen.constants import LIVE_URL_PREFIX_ERROR
from djadyen.models import AdyenIssuer, AdyenPaymentOption
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


def get_payment_option_from_name(
    adyen_name: str,
) -> tuple[AdyenPaymentOption | None, AdyenIssuer | None]:
    """
    Finds the active payment option from the adyen name of the option or the issuer
    :param adyen_name: adyen name of a payment option or issuer
    :return: matching payment option and issuer if exists
    """

    if payment_method := AdyenPaymentOption.objects.filter(
        adyen_name=adyen_name, is_active=True
    ).first():
        return payment_method, None

    elif issuer := AdyenIssuer.objects.filter(
        adyen_id=adyen_name, payment_option__is_active=True
    ).first():
        return issuer.payment_option, issuer

    return None, None
