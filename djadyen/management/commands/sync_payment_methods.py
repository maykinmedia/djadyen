from datetime import datetime

from django.core.management.base import BaseCommand

import requests

from djadyen import settings

from ...hpp import sign_params
from ...models import AdyenIssuer, AdyenPaymentOption


class Command(BaseCommand):
    help = "Sync the payment methods from adyen."

    def handle(self, *args, **options):
        params = {
            'merchantAccount': settings.ADYEN_MERCHANT_ACCOUNT,
            'skinCode': settings.ADYEN_SKIN_CODE,
            'merchantReference': 'payment_options',
            'currencyCode': settings.ADYEN_CURRENCYCODE,
            'paymentAmount': 199,
            'countryCode': 'NL',
            'sessionValidity': datetime.now().isoformat(),
        }
        params = sign_params(params)
        response = requests.post('{}hpp/directory.shtml'.format(settings.ADYEN_URL), params=params)

        payment_methods = response.json()['paymentMethods']
        for payment_method in payment_methods:
            payment_qs = AdyenPaymentOption.objects.filter(adyen_name=payment_method['brandCode'])
            if payment_qs.exists():
                payment = payment_qs.first()
                payment.name = payment_method.get('name')
                payment.save()
            else:
                payment = AdyenPaymentOption.objects.create(
                    name=payment_method.get('name'),
                    adyen_name=payment_method.get('brandCode')
                )

            if payment_method.get('issuers'):
                issuers = payment_method.get('issuers')
                for issuer in issuers:
                    issuer_qs = AdyenIssuer.objects.filter(adyen_id=issuer['issuerId'])
                    if issuer_qs.exists():
                        issuer_obj = issuer_qs.first()
                        issuer_obj.name = issuer.get('name')
                        issuer_obj.payment_option = payment
                        issuer_obj.save()
                    else:
                        issuer_obj = AdyenIssuer.objects.create(
                            name=issuer.get('name'),
                            adyen_id=issuer.get('issuerId'),
                            payment_option=payment
                        )
