from __future__ import annotations

import json
import logging

from django import template

from djadyen.choices import Status
from djadyen.models import AdyenOrder
from djadyen.settings import get_setting
from djadyen.utils import setup_adyen_client

register = template.Library()
logger = logging.getLogger("adyen")


def get_common_checkout_context(
    language: str,
    order: AdyenOrder,
    country_code: str,
) -> dict:

    return {
        # Adyen Settings
        "client_key": get_setting("DJADYEN_CLIENT_KEY"),
        "environment": get_setting("DJADYEN_ENVIRONMENT"),
        "language": language,
        "country_code": country_code,
        # Djadyen Adyen Settings
        "redirect_url": order.get_return_url,
        "adyen_styles_json": json.dumps(adyen_styles)
        if (adyen_styles := get_setting("DJADYEN_STYLES"))
        else None,
    }


def get_single_option_contex(order: AdyenOrder) -> dict:
    """
    Gets the context needed for a single payment option.
    :param order:
    :return:
    """

    return {
        "payment_type": (
            order.payment_option.adyen_name if order.payment_option else ""
        ),
        "issuers": (
            json.dumps(
                list(
                    order.payment_option.issuers.all().values(
                        "name", "adyen_id"
                    )
                )
            )
            if order.payment_option
            else []
        ),
        "issuer": order.issuer.adyen_id if order.issuer else "",
    }


def get_adyen_session(
    language: str,
    order: AdyenOrder,
    merchant_account: str,
    country_code: str,
) -> dict[str, str]:
    """
    Creates an Adyen session
    :param language:
    :param order:
    :param merchant_account:
    :param country_code:
    :return: dict with the session_id and session_data or empty
    """

    logger.info("Start new payment for %s", order.reference)
    ady = setup_adyen_client()

    # Setting request data.
    request = {
        "amount": {
            "value": order.get_price_in_cents(),
            "currency": get_setting("DJADYEN_CURRENCYCODE"),
        },
        "reference": str(order.reference),
        "merchantAccount": merchant_account,
        "returnUrl": order.get_return_url(),
        "shopperLocale": language,
        "countryCode": country_code,
    }

    if hasattr(order, "email"):
        request["shopperEmail"] = order.email

    logger.info(request)
    # Starting the checkout.
    result = ady.checkout.payments_api.sessions(
        request, idempotency_key=f"{order.reference}-session"
    )

    if result.status_code == 201:
        return {
            "session_id": result.message.get("id"),
            "session_data": result.message.get("sessionData"),
        }
    return {}


@register.inclusion_tag("adyen/component.html")
def adyen_payment_component(
    language,
    order,
    merchant_account: str | None = None,
    country_code: str | None = None,
):
    """
    Will display a singular session payment method.
    """

    country_code = (
        country_code.lower()
        if country_code
        else get_setting("DJADYEN_DEFAULT_COUNTRY_CODE")
    )

    if not merchant_account:
        merchant_account = get_setting("DJADYEN_MERCHANT_ACCOUNT")

    if session_context := get_adyen_session(
        language, order, merchant_account, country_code
    ):
        return (
            session_context
            | get_common_checkout_context(language, order, country_code)
            | get_single_option_contex(order)
        )

    return {}


@register.inclusion_tag("adyen/advanced_component.html")
def adyen_advanced_payment_component(
    language: str,
    order: AdyenOrder,
    country_code: str | None = None,
):
    country_code = (
        country_code.lower()
        if country_code
        else get_setting("DJADYEN_DEFAULT_COUNTRY_CODE")
    )

    return (
        {
            "amount": order.get_price_in_cents(),
            "currency": get_setting("DJADYEN_CURRENCYCODE"),
            "payments_api": order.get_payments_api(),
            "payment_details_api": order.get_payment_details_api(),
        }
        | get_common_checkout_context(
            language,
            order,
            country_code,
        )
        | get_single_option_contex(order)
    )


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
    country_code: str | None = None,
) -> dict:
    """
    Renders the Adyen Giving donation component.
    :param language: Locale of the adyen donation component
    :param campaign: Adyen donation campaign
    :param redirect_url: Redirect url after canceling the donation.
    :param country_code: Adyen Country Code
    :return: Template tag context
    """

    if not campaign:
        return {}

    return {
        "campaign": json.dumps(campaign),
        "campaign_id": campaign["id"],
        "client_key": get_setting("DJADYEN_CLIENT_KEY"),
        "environment": get_setting("DJADYEN_ENVIRONMENT"),
        "language": language,
        "redirect_url": redirect_url,
        "country_code": (
            country_code.lower()
            if country_code
            else get_setting("DJADYEN_DEFAULT_COUNTRY_CODE")
        ),
    }
