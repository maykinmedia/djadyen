import base64
import binascii
import hashlib
import hmac
import logging
from collections import OrderedDict
from datetime import timedelta

from django.utils import timezone

from djadyen import settings

logger = logging.getLogger('adyen')


def escape_val(val):
    try:
        return val.replace('\\', '\\\\').replace(':', '\\:')
    except AttributeError:
        return str(val)


def sign_params(params):
    """
    Description of how the HMAC can be calculated can be found here

    https://docs.adyen.com/developers/classic-integration/hosted-payment-pages/hmac-signature-calculation
    """
    hmac_key = binascii.a2b_hex(settings.ADYEN_MERCHANT_SECRET)

    params = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
    logger.debug("Ordered Params: %s", params)

    signing_string = ':'.join(map(escape_val, list(params.keys()) + list(params.values())))
    logger.debug("Signing Params: %s", signing_string)

    hmac_string = hmac.new(hmac_key, signing_string.encode('utf-8'), hashlib.sha256)
    logger.debug("HMAC: %s", hmac_string)

    params['merchantSig'] = base64.b64encode(hmac_string.digest()).decode("utf-8")
    logger.debug("merchantSig: %s", params['merchantSig'])
    return params


class HPPPaymenRequest:
    def __init__(self, merchant_reference, payment_amount, result_url,
                 shopper_email=None, brand_code=None, issuer_id=None):
        self.merchant_reference = merchant_reference
        self.payment_amount = payment_amount
        self.result_url = result_url

        self.shopper_email = shopper_email
        self.shopper_locale = 'nl_NL'
        self.brand_code = brand_code
        self.issuer_id = issuer_id
        self.skin_code = settings.ADYEN_SKIN_CODE
        self.currency_code = settings.ADYEN_CURRENCYCODE
        self.merchant_account = settings.ADYEN_MERCHANT_ACCOUNT

        self.ship_before_date = timezone.now()

        self.session_validity = (
            timezone.now() + timedelta(minutes=settings.ADYEN_SESSION_MINUTES)
        )

    def get_adyen_url(self):
        page = 'hpp/select.shtml'
        if self.brand_code:
            page = 'hpp/details.shtml'
        if self.issuer_id:
            page = 'hpp/skipDetails.shtml'
        url = '{}{}'.format(settings.ADYEN_URL, page)

        logger.debug("Adyen Url: %s", url)
        return url

    @classmethod
    def from_object(cls, obj, return_url):
        kwargs = {
            'merchant_reference': obj.reference,
            'payment_amount': obj.get_price_in_cents(),
            'result_url': '{}{}'.format(settings.ADYEN_HOST_URL, return_url)
        }
        if obj.email:
            kwargs['shopper_email'] = obj.email
        if obj.payment_option:
            kwargs['brand_code'] = obj.payment_option.adyen_name
        if obj.issuer:
            kwargs['issuer_id'] = obj.issuer.adyen_id

        return cls(**kwargs)

    def get_adyen_params(self):
        params = {
            'shipBeforeDate': self.ship_before_date.isoformat(),
            'shopperLocale': self.shopper_locale,
            'merchantReference': self.merchant_reference,
            'paymentAmount': self.payment_amount,
            'resURL': self.result_url,
            'currencyCode': self.currency_code,
            'merchantAccount': self.merchant_account,
            'shopperEmail': self.shopper_email,
            'skinCode': self.skin_code,
            'sessionValidity': self.session_validity.isoformat(),
        }

        if self.issuer_id:
            params['issuerId'] = self.issuer_id

        if self.brand_code is not None:
            params['brandCode'] = self.brand_code

        return sign_params(params)


class HPPPaymentResponse:
    def __init__(self, auth_result, psp_reference, merchant_reference,
                 skin_code, payment_method, shopper_locale, merchant_return_data, reason, merchant_sig):
        self.auth_result = auth_result
        self.psp_reference = psp_reference
        self.merchant_reference = merchant_reference
        self.skin_code = skin_code
        self.payment_method = payment_method
        self.shopper_locale = shopper_locale
        self.merchant_return_data = merchant_return_data
        self.reason = reason
        self.merchant_sig = merchant_sig

    @classmethod
    def from_data(cls, data):
        kwargs = {
            'auth_result': data.get('authResult'),
            'psp_reference': data.get('pspReference'),
            'merchant_reference': data.get('merchantReference'),
            'skin_code': data.get('skinCode'),
            'payment_method': data.get('paymentMethod'),
            'shopper_locale': data.get('shopperLocale'),
            'merchant_return_data': data.get('merchantReturnData'),
            'reason': data.get('reason'),
            'merchant_sig': data.get('merchantSig'),
        }

        return cls(**kwargs)

    def get_adyen_params(self):
        params = {
            'authResult': self.auth_result,
            'merchantReference': self.merchant_reference,
            'skinCode': self.skin_code,
            'paymentMethod': self.payment_method,
            'shopperLocale': self.shopper_locale,
        }

        if self.psp_reference:
            params['pspReference'] = self.psp_reference
        if self.merchant_return_data:
            params['merchantReturnData'] = self.merchant_return_data
        if self.reason:
            params['reason'] = self.reason

        return sign_params(params)

    def is_valid(self):
        if self.merchant_sig is None:
            return False

        calculated_params = self.get_adyen_params()
        return calculated_params['merchantSig'] == self.merchant_sig
