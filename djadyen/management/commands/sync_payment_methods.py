from django.core.management.base import BaseCommand

import Adyen

from djadyen import settings

from ...models import AdyenIssuer, AdyenPaymentOption


def create_payment_method(type, name, issuers):
    payment_qs = AdyenPaymentOption.objects.filter(adyen_name=type)
    if not payment_qs.exists():
        payment = AdyenPaymentOption.objects.create(
            name=name,
            adyen_name=type,
        )
    else:
        payment = payment_qs.first()

    for issuer in issuers:
        issuer_qs = AdyenIssuer.objects.filter(adyen_id=issuer["id"])
        if issuer_qs.exists():
            issuer_obj = issuer_qs.first()
            issuer_obj.name = issuer.get("name")
            issuer_obj.payment_option = payment
            issuer_obj.save()
        else:
            issuer_obj = AdyenIssuer.objects.create(
                name=issuer.get("name"),
                adyen_id=issuer.get("id"),
                payment_option=payment,
            )


class Command(BaseCommand):
    help = "Sync the payment methods from adyen."

    def handle(self, *args, **options):
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
            "merchantAccount": settings.DJADYEN_MERCHANT_ACCOUNT,
        }
        # Starting the checkout.
        result = ady.checkout.payment_methods(request)

        payment_methods = result.message.get("paymentMethods")
        for payment_method in payment_methods:
            name = payment_method.get("name")
            type = payment_method.get("type")
            brands = payment_method.get("brands")
            issuers = payment_method.get("issuers", [])
            if brands:
                for brand in brands:
                    create_payment_method(brand, name, issuers)
            else:
                create_payment_method(type, name, issuers)
