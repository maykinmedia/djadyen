from django import template
from django.utils.translation import get_language

import Adyen

from djadyen import settings
from djadyen.choices import Status

register = template.Library()


@register.inclusion_tag("adyen/component.html")
def adyen_payment_component(order):
    """
    Will display a singular payment method.
    """
    ady = Adyen.Adyen()

    # Setting global values
    ady.payment.client.platform = settings.DJADYEN_ENVIRONMENT
    ady.payment.client.xapikey = settings.DJADYEN_SERVER_KEY
    ady.payment.client.app_name = settings.DJADYEN_APPNAME

    # Setting request data.
    request = {
        "amount": {
            "value": order.get_price_in_cents(),
            "currency": settings.DJADYEN_CURRENCYCODE,
        },
        "reference": str(order.reference),
        "merchantAccount": settings.DJADYEN_MERCHANT_ACCOUNT,
        "returnUrl": order.get_return_url(),
    }

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
