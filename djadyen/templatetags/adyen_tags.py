import json
import logging

from django import template
from django.utils.translation import get_language

from djadyen import settings
from djadyen.choices import Status
from djadyen.conf import get_adyen_styles
from djadyen.utils import setup_adyen_client

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
    ady = setup_adyen_client()

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
        "countryCode": (
            country_code.lower()
            if country_code
            else settings.DJADYEN_DEFAULT_COUNTRY_CODE
        ),
    }
    try:
        request["shopperEmail"] = order.email
    except Exception:
        pass

    logger.info(request)
    # Starting the checkout.
    result = ady.checkout.payments_api.sessions(request)

    if result.status_code == 201:
        context = {
            "client_key": settings.DJADYEN_CLIENT_KEY,
            "session_id": result.message.get("id"),
            "session_data": result.message.get("sessionData"),
            "environment": settings.DJADYEN_ENVIRONMENT,
            "redirect_url": order.get_return_url,
            "language": get_language(),
            "payment_type": (
                order.payment_option.adyen_name if order.payment_option else ""
            ),
            "issuer": order.issuer.adyen_id if order.issuer else "",
        }

        # Add custom styles to context as JSON
        adyen_styles = get_adyen_styles()
        if adyen_styles:
            context["adyen_styles_json"] = json.dumps(adyen_styles)
        else:
            context["adyen_styles_json"] = None

        return context
    return {}


@register.inclusion_tag("adyen/polling.html")
def adyen_status_polling(order, status_url):
    return {
        "status_url": status_url,
        "pending": order.status in [Status.Created, Status.Pending],
    }
