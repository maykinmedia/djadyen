import logging
from django import template
from django.utils.translation import get_language

import Adyen

from djadyen import settings
from djadyen.choices import Status

register = template.Library()
logger = logging.getLogger("adyen")


@register.inclusion_tag("adyen/component.html")
def adyen_payment_component(
    language,
    order,
    merchant_account=settings.DJADYEN_MERCHANT_ACCOUNT,
    country_code=settings.DJADYEN_DEFAULT_COUNTRY_CODE,
):
    """
    Will display a singular payment method.
    """
    logger.info("Start new payment for {}".format(str(order.reference)))
    ady = Adyen.Adyen()

    if not settings.DJADYEN_ENVIRONMENT:
        assert False, "Please provide an environment."

    if settings.DJADYEN_ENVIRONMENT == "live" and not settings.DJADYEN_LIVE_URL_PREFIX:
        assert False, "Please provide the live_url_prefix. https://docs.adyen.com/development-resources/live-endpoints#live-url-prefix"

    # Setting global values
    ady.payment.client.platform = settings.DJADYEN_ENVIRONMENT
    ady.payment.client.xapikey = settings.DJADYEN_SERVER_KEY
    ady.payment.client.app_name = settings.DJADYEN_APPNAME
    ady.payment.client.live_endpoint_prefix = settings.DJADYEN_LIVE_URL_PREFIX

    # Setting request data.
    request = {
        "amount": {
            "value": order.get_price_in_cents(),
            "currency": settings.DJADYEN_CURRENCYCODE,
        },
        "reference": str(order.reference),
        "merchantAccount": merchant_account,
        "returnUrl": order.get_return_url(),
        "shopperLocale": language.lower(),
        "countryCode": country_code.lower()
        if country_code
        else settings.DJADYEN_DEFAULT_COUNTRY_CODE,
    }
    try:
        request["shopperEmail"] = order.email
    except Exception:
        pass

    logger.info(request)
    # Starting the checkout.
    result = ady.checkout.sessions(request)

    if result.status_code == 201:
        return {
            "client_key": settings.DJADYEN_CLIENT_KEY,
            "session_id": result.message.get("id"),
            "session_data": result.message.get("sessionData"),
            "environment": settings.DJADYEN_ENVIRONMENT,
            "redirect_url": order.get_return_url,
            "language": get_language(),
            "payment_type": order.payment_option.adyen_name
            if order.payment_option
            else "",
            "issuer": order.issuer.adyen_id if order.issuer else "",
        }
    return {}


@register.inclusion_tag("adyen/polling.html")
def adyen_status_polling(order, status_url):
    return {
        "status_url": status_url,
        "pending": order.status in [Status.Created, Status.Pending],
    }
