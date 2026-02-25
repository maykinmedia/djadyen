import json
import logging

from django import template

from djadyen import settings
from djadyen.choices import Status
from djadyen.conf import get_adyen_styles
from djadyen.models import AdyenOrder
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
    logger.info("Start new payment for %s", order.reference)
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
        "shopperLocale": language,
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
    result = ady.checkout.payments_api.sessions(
        request, idempotency_key=order.reference
    )

    if result.status_code == 201:
        context = {
            "client_key": settings.DJADYEN_CLIENT_KEY,
            "session_id": result.message.get("id"),
            "session_data": result.message.get("sessionData"),
            "environment": settings.DJADYEN_ENVIRONMENT,
            "redirect_url": order.get_return_url,
            "language": language,
            "payment_type": (
                order.payment_option.adyen_name if order.payment_option else ""
            ),
            "issuers": (
                json.dumps(
                    list(
                        order.payment_option.adyenissuer_set.all().values(
                            "name", "adyen_id"
                        )
                    )
                )
                if order.payment_option
                else []
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


@register.inclusion_tag("adyen/advanced_component.html")
def adyen_advanced_payment_component(
    language: str,
    order: AdyenOrder,
    country_code: str = settings.DJADYEN_DEFAULT_COUNTRY_CODE,
):
    context = {
        "client_key": settings.DJADYEN_CLIENT_KEY,
        "environment": settings.DJADYEN_ENVIRONMENT,
        "redirect_url": order.get_return_url,
        "amount": order.get_price_in_cents(),
        "currency": settings.DJADYEN_CURRENCYCODE,
        "country_code": country_code,
        "language": language,
        "payment_type": (
            order.payment_option.adyen_name if order.payment_option else ""
        ),
        "issuers": (
            json.dumps(
                list(
                    order.payment_option.adyenissuer_set.all().values(
                        "name", "adyen_id"
                    )
                )
            )
            if order.payment_option
            else []
        ),
        "issuer": order.issuer.adyen_id if order.issuer else "",
        "payments_api": order.get_payments_api(),
        "payment_details_api": order.get_payment_details_api(),
    }

    return context


@register.inclusion_tag("adyen/polling.html")
def adyen_status_polling(order, status_url):
    return {
        "status_url": status_url,
        "pending": order.status in [Status.Created, Status.Pending],
    }


@register.inclusion_tag("adyen/donation_component.html")
def adyen_donation_component(
    language: str,
    campaign: dict,
    redirect_url: str,
    country_code: str = settings.DJADYEN_DEFAULT_COUNTRY_CODE,
) -> dict:
    """
    Renders the Adyen Giving donation component.
    :param language: Locale of the adyen donation component
    :param campaign: Adyen donation campaign
    :param redirect_url: Redirect url after canceling the donation.
    :param country_code: Adyen Country Code
    :return: Template tag context
    """
    return {
        "campaign": json.dumps(campaign),
        "campaign_id": campaign["id"],
        "client_key": settings.DJADYEN_CLIENT_KEY,
        "environment": settings.DJADYEN_ENVIRONMENT,
        "language": language,
        "redirect_url": redirect_url,
        "country_code": (
            country_code.lower()
            if country_code
            else settings.DJADYEN_DEFAULT_COUNTRY_CODE
        ),
    }
